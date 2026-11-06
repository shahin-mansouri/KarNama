from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from account.models import Skill, UserCustom, UserProfile
from .models import BlogPost, Category


class BlogGeneratorCommandTests(SimpleTestCase):
	def test_generator_rejects_unexpected_article_data(self):
		from home.management.commands.blog_generator import _validate_blog_data

		with self.assertRaises(ValueError):
			_validate_blog_data(
				{
					'title': 'عنوان',
					'excerpt': 'خلاصه',
					'content': 'متن',
					'category': 'استخدام',
				},
				expected_category='رزومه موفق',
			)

		with self.assertRaises(ValueError):
			_validate_blog_data(
				{
					'title': 'عنوان',
					'excerpt': 'خلاصه' * 21,
					'content': 'متن',
					'category': 'رزومه موفق',
				},
				expected_category='رزومه موفق',
			)

	def test_scheduler_does_not_start_for_manual_generation_command(self):
		from home.apps import _is_web_server_process

		with patch('home.apps.sys.argv', ['manage.py', 'blog_generator']):
			self.assertFalse(_is_web_server_process())

	def test_scheduler_starts_for_runserver_child_process(self):
		from home.apps import _is_web_server_process

		with (
			patch('home.apps.sys.argv', ['manage.py', 'runserver']),
			patch.dict('os.environ', {'RUN_MAIN': 'true'}),
		):
			self.assertTrue(_is_web_server_process())

	def test_manual_command_shows_progress(self):
		blog_json = {
			'title': 'عنوان آزمایشی',
			'excerpt': 'خلاصه',
			'content': 'متن',
			'category': 'رزومه موفق',
		}

		def generate_blog(progress):
			progress.write_stage('مرحله ۱ از ۵: آماده‌سازی', 65)
			return blog_json

		output = StringIO()
		with (
			patch(
				'home.management.commands.blog_generator.blog_generator',
				side_effect=generate_blog,
			),
			patch(
				'home.management.commands.blog_generator._get_or_create_category',
				return_value=object(),
			),
			patch('home.management.commands.blog_generator._save_blog_post'),
		):
			call_command('blog_generator', stdout=output)

		self.assertIn('مرحله ۱ از ۵', output.getvalue())
		self.assertIn('مرحله ۵ از ۵', output.getvalue())
		self.assertIn('با موفقیت منتشر شد', output.getvalue())

	def test_automatic_publisher_does_not_write_progress(self):
		from home.management.commands.blog_generator import publish_generated_blog

		blog_json = {
			'title': 'عنوان آزمایشی',
			'excerpt': 'خلاصه',
			'content': 'متن',
			'category': 'رزومه موفق',
		}
		output = StringIO()
		with (
			patch(
				'home.management.commands.blog_generator.blog_generator',
				return_value=blog_json,
			) as generate_blog,
			patch(
				'home.management.commands.blog_generator._get_or_create_category',
				return_value=object(),
			),
			patch('home.management.commands.blog_generator._save_blog_post'),
			patch('sys.stdout', output),
			patch('sys.stderr', output),
		):
			publish_generated_blog()

		self.assertEqual(output.getvalue(), '')
		generate_blog.assert_called_once_with()

	def test_scheduler_waits_five_minutes_between_attempts(self):
		from home import blog_scheduler

		class StopAfterRetry:
			def __init__(self):
				self.calls = 0

			def wait(self, interval):
				self.calls += 1
				self_intervals.append(interval)
				return self.calls == 2

		self_intervals = []
		stop_event = StopAfterRetry()
		with (
			patch.object(blog_scheduler, '_stop_event', stop_event),
			patch(
				'home.management.commands.blog_generator.publish_generated_blog',
				side_effect=ValueError('bad model response'),
			),
			patch('home.blog_scheduler.close_old_connections'),
		):
			blog_scheduler._publish_periodically()

		self.assertEqual(
			self_intervals,
			[5 * 60, 5 * 60],
		)


class BlogPostPublishingTests(TestCase):
	def test_repeated_title_gets_a_unique_slug(self):
		from home.management.commands.blog_generator import _save_blog_post

		category = Category.objects.create(name='رزومه موفق', slug='resume-success')
		blog_json = {
			'title': 'عنوان آزمایشی',
			'excerpt': 'خلاصه',
			'content': 'متن',
		}

		_save_blog_post(blog_json, category)
		_save_blog_post(blog_json, category)

		self.assertEqual(
			list(BlogPost.objects.order_by('id').values_list('slug', flat=True)),
			['عنوان-آزمایشی', 'عنوان-آزمایشی-2'],
		)


class ResumeDiscoveryTests(TestCase):
	def setUp(self):
		self.admin = UserCustom.objects.create_superuser(
			username='admin',
			email='admin@example.com',
			phone_number='09120000001',
			password='test-password',
			first_name='مدیر',
			last_name='سایت',
		)
		UserProfile.objects.create(user=self.admin, title='مدیر محصول')

		self.developer = UserCustom.objects.create_user(
			username='developer',
			email='developer@example.com',
			phone_number='09120000002',
			password='test-password',
			first_name='توسعه‌دهنده',
			last_name='پایتون',
		)
		UserProfile.objects.create(user=self.developer, title='توسعه‌دهنده نرم‌افزار')
		Skill.objects.create(user=self.developer, name='Python', proficiency=90)

	def test_home_lists_superuser_first_in_successful_people(self):
		response = self.client.get(reverse('home'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['successful_people'][0], self.admin)

	def test_resume_bank_search_matches_skills(self):
		response = self.client.get(reverse('resume_bank'), {'q': 'Python'})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(list(response.context['resume_users']), [self.developer])


class BlogContentRenderingTests(SimpleTestCase):
	def test_legacy_plain_text_preserves_paragraphs(self):
		from home.templatetags.blog_tags import render_blog_content

		rendered = render_blog_content('پاراگراف اول\nادامه همان پاراگراف\n\nپاراگراف دوم')

		self.assertEqual(
			rendered,
			'<p>پاراگراف اول<br>ادامه همان پاراگراف</p><p>پاراگراف دوم</p>',
		)

	def test_structured_html_keeps_safe_markup_and_removes_unsafe_markup(self):
		from home.templatetags.blog_tags import render_blog_content

		rendered = render_blog_content(
			'<h2>عنوان بخش</h2><p onclick="alert(1)">متن <strong>مهم</strong></p>'
			'<script>alert(1)</script>'
		)

		self.assertEqual(rendered, '<h2>عنوان بخش</h2><p>متن <strong>مهم</strong></p>')


class BlogTests(TestCase):
	def setUp(self):
		published_at = timezone.now()
		for index in range(6):
			BlogPost.objects.create(
				title=f'مطلب {index}',
				slug=f'post-{index}',
				excerpt='خلاصه مطلب',
				content='متن کامل مطلب',
				category='رزومه',
				published_at=published_at,
				is_published=True,
			)
		BlogPost.objects.create(
			title='مطلب خصوصی',
			slug='private-post',
			excerpt='خلاصه مطلب خصوصی',
			content='متن مطلب خصوصی',
			category='رزومه',
			published_at=published_at,
			is_published=False,
		)

	def test_blog_list_paginates_published_posts_by_five(self):
		first_page = self.client.get(reverse('blog_list'), {'page': 1})
		second_page = self.client.get(reverse('blog_list'), {'page': 2})

		self.assertEqual(first_page.status_code, 200)
		self.assertEqual(len(first_page.context['blog_posts']), 5)
		self.assertTrue(first_page.context['page_obj'].has_next())
		self.assertEqual(len(second_page.context['blog_posts']), 1)
		self.assertNotContains(first_page, 'مطلب خصوصی')

	def test_blog_detail_shows_published_post_and_hides_unpublished_post(self):
		response = self.client.get(reverse('blog_detail', args=['post-0']))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'متن کامل مطلب')
		self.assertEqual(
			self.client.get(reverse('blog_detail', args=['private-post'])).status_code,
			404,
		)
		self.assertEqual(self.client.get(reverse('blog_detail', args=['missing'])).status_code, 404)

	def test_blog_detail_renders_allowed_html_and_removes_unsafe_markup(self):
		post = BlogPost.objects.get(slug='post-0')
		post.content = (
			'<h2>عنوان بخش</h2><p onclick="alert(1)">متن <strong>مهم</strong></p>'
			'<script>alert(1)</script>'
		)
		post.save(update_fields=['content'])

		response = self.client.get(reverse('blog_detail', args=['post-0']))

		self.assertContains(response, '<h2>عنوان بخش</h2>', html=True)
		self.assertContains(response, '<p>متن <strong>مهم</strong></p>', html=True)
		self.assertNotContains(response, 'onclick')
		self.assertNotContains(response, '<script>')
		self.assertNotContains(response, 'alert(1)')

	def test_sitemap_includes_published_blog_details(self):
		response = self.client.get(reverse('django_sitemap'), HTTP_HOST='127.0.0.1')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<loc>https://127.0.0.1/</loc>')
		self.assertNotContains(response, 'http://127.0.0.1/')
		self.assertContains(response, '/blog/post-0/')
		self.assertNotContains(response, '/blog/private-post/')
