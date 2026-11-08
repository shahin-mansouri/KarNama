from io import BytesIO
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import FieldOfActivity, OTPCode, Project, UserProfile


def make_test_image():
	image_data = BytesIO()
	Image.new('RGB', (10, 10), color='red').save(image_data, format='PNG')
	return SimpleUploadedFile('same-name.png', image_data.getvalue(), content_type='image/png')


class PhoneLoginTests(TestCase):
	def setUp(self):
		self.phone = '09121234567'
		self.user = get_user_model().objects.create_user(
			username='existing-user',
			password='unused-password',
			email='user@example.com',
			first_name='Existing',
			last_name='User',
			phone_number=self.phone,
		)

	@patch('account.views.SMS')
	def test_phone_login_sends_otp_and_authenticates_user(self, sms_class):
		sms_class.return_value.send_code.return_value = SimpleNamespace(status_code=200)

		response = self.client.post(reverse('login'), {'phone_number': '۰۹۱۲۱۲۳۴۵۶۷'})

		self.assertRedirects(response, reverse('login'))
		sms_class.return_value.send_code.assert_called_once()
		sent_phone, sent_code = sms_class.return_value.send_code.call_args.args
		self.assertEqual(sent_phone, self.phone)
		self.assertEqual(len(sent_code), 6)
		otp = OTPCode.objects.get(pk=self.client.session['otp_id'])
		self.assertNotEqual(otp.code_hash, sent_code)
		self.assertFalse(otp.used_at)
		self.assertEqual(self.client.session['otp_phone'], self.phone)
		response = self.client.get(reverse('login'))
		self.assertContains(response, self.phone)
		self.assertNotContains(response, 'None')
		self.assertContains(response, '۰۲:۰۰')

		response = self.client.post(reverse('login'), {'code': sent_code})

		self.assertRedirects(response, reverse('dashboard'))
		self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

	@patch('account.views.SMS')
	def test_resend_requires_two_minutes_and_issues_a_new_code(self, sms_class):
		sms_class.return_value.send_code.return_value = SimpleNamespace(status_code=200)
		self.client.post(reverse('login'), {'phone_number': self.phone})
		first_code = sms_class.return_value.send_code.call_args.args[1]
		first_otp_id = self.client.session['otp_id']

		response = self.client.post(reverse('login'), {'action': 'resend'})

		self.assertRedirects(response, reverse('login'))
		sms_class.return_value.send_code.assert_called_once()

		session = self.client.session
		session['otp_resend_at'] = 0
		session.save()
		response = self.client.post(reverse('login'), {'action': 'resend'})

		self.assertRedirects(response, reverse('login'))
		self.assertEqual(sms_class.return_value.send_code.call_count, 2)
		self.assertEqual(sms_class.return_value.send_code.call_args.args[0], self.phone)
		new_otp = OTPCode.objects.get(pk=self.client.session['otp_id'])
		self.assertNotEqual(new_otp.pk, first_otp_id)
		self.assertNotEqual(first_code, sms_class.return_value.send_code.call_args.args[1])
		self.assertEqual(self.client.session['otp_phone'], self.phone)

		response = self.client.post(reverse('login'), {
			'code': sms_class.return_value.send_code.call_args.args[1],
		})
		self.assertRedirects(response, reverse('dashboard'))

	@patch('account.views.SMS')
	def test_failed_resend_keeps_the_current_otp_available(self, sms_class):
		sms_class.return_value.send_code.side_effect = [
			SimpleNamespace(status_code=200),
			SimpleNamespace(status_code=500),
		]
		self.client.post(reverse('login'), {'phone_number': self.phone})
		first_code = sms_class.return_value.send_code.call_args.args[1]
		first_otp_id = self.client.session['otp_id']
		session = self.client.session
		session['otp_resend_at'] = 0
		session.save()

		response = self.client.post(reverse('login'), {'action': 'resend'})

		self.assertRedirects(response, reverse('login'))
		self.assertEqual(self.client.session['otp_id'], first_otp_id)
		self.assertTrue(OTPCode.objects.filter(pk=first_otp_id).exists())
		self.assertEqual(OTPCode.objects.count(), 1)

		response = self.client.post(reverse('login'), {'code': first_code})
		self.assertRedirects(response, reverse('dashboard'))

	@patch('account.views.SMS')
	def test_failed_sms_does_not_start_verification(self, sms_class):
		sms_class.return_value.send_code.return_value = SimpleNamespace(status_code=500)

		response = self.client.post(reverse('login'), {'phone_number': self.phone})

		self.assertEqual(response.status_code, 200)
		self.assertNotIn('otp_id', self.client.session)
		self.assertEqual(OTPCode.objects.count(), 0)
		self.assertContains(response, 'ارسال کد تأیید انجام نشد')

	def test_new_user_enters_dashboard_after_account_details(self):
		new_phone = '09129876543'
		session = self.client.session
		session['onboarding_phone'] = new_phone
		session['onboarding_step'] = 0
		session.save()

		response = self.client.post(reverse('onboarding'), {
			'username': 'new-user',
			'first_name': 'New',
			'last_name': 'User',
			'email': 'new@example.com',
			'phone_number': new_phone,
			'address': 'Test address',
		})

		self.assertRedirects(response, reverse('dashboard'))
		self.assertTrue(response.wsgi_request.user.is_authenticated)
		self.assertFalse(response.wsgi_request.session.get('onboarding_phone'))
		self.assertFalse(response.wsgi_request.session.get('onboarding_step'))
		self.assertTrue(get_user_model().objects.filter(username='new-user').exists())


class WebPImageUploadTests(TestCase):
	def test_profile_and_project_images_are_unique_webp_files(self):
		with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
			user = get_user_model().objects.create_user(
				username='image-user',
				password='unused-password',
				email='image@example.com',
				first_name='Image',
				last_name='User',
				phone_number='09121111111',
			)
			profile = UserProfile.objects.create(user=user, title='Developer', profile_picture=make_test_image())
			project = Project.objects.create(
				user=user,
				field_of_activity=FieldOfActivity.objects.create(name='Software'),
				name='Test project',
				technologies_used='Django',
				project_picture=make_test_image(),
			)

			self.assertTrue(profile.profile_picture.name.endswith('.webp'))
			self.assertTrue(project.project_picture.name.endswith('.webp'))
			self.assertNotEqual(profile.profile_picture.name, project.project_picture.name)
			with Image.open(profile.profile_picture.path) as profile_image:
				self.assertEqual(profile_image.format, 'WEBP')
			with Image.open(project.project_picture.path) as project_image:
				self.assertEqual(project_image.format, 'WEBP')
