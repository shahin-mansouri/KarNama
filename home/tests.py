from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from account.models import Skill, UserCustom, UserProfile
from .models import BlogPost


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

	def test_sitemap_includes_published_blog_details(self):
		response = self.client.get(reverse('django_sitemap'), HTTP_HOST='127.0.0.1')

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, '<loc>https://127.0.0.1/</loc>')
		self.assertNotContains(response, 'http://127.0.0.1/')
		self.assertContains(response, '/blog/post-0/')
		self.assertNotContains(response, '/blog/private-post/')
