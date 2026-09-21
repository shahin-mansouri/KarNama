from django.test import TestCase
from django.urls import reverse

from account.models import UserCustom

from .models import ContactMessage


class ContactMessageTests(TestCase):
	def setUp(self):
		self.recipient = UserCustom.objects.create_user(
			username='shahin',
			email='shahin@example.com',
			phone_number='09123456789',
			password='test-password',
		)

	def test_contact_form_creates_message_for_profile_owner(self):
		response = self.client.post(
			reverse('send_message', kwargs={'username': self.recipient.username}),
			{
				'name': 'Visitor',
				'email': 'visitor@example.com',
				'subject': 'Project inquiry',
				'message': 'I would like to discuss a project.',
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()['success'])
		self.assertEqual(ContactMessage.objects.get().recipient, self.recipient)

	def test_contact_form_rejects_incomplete_message(self):
		response = self.client.post(
			reverse('send_message', kwargs={'username': self.recipient.username}),
			{'name': 'Visitor'},
		)

		self.assertEqual(response.status_code, 400)
		self.assertFalse(response.json()['success'])
		self.assertEqual(ContactMessage.objects.count(), 0)
from django.test import TestCase

from account.models import UserCustom

from .models import Testimonial


class TestimonialViewTests(TestCase):
	def setUp(self):
		self.recipient = UserCustom.objects.create_user(
			username='owner',
			email='owner@example.com',
			phone_number='09120000001',
			password='test-password',
		)
		self.author = UserCustom.objects.create_user(
			username='colleague',
			email='colleague@example.com',
			phone_number='09120000002',
			password='test-password',
		)
		self.url = f'/messages/{self.recipient.username}/testimonial/'

	def test_guest_is_redirected_to_login(self):
		response = self.client.post(self.url, {'text': 'نظر آزمایشی'})

		self.assertRedirects(response, f'/account/login/?next={self.url}')
		self.assertFalse(Testimonial.objects.exists())

	def test_authenticated_user_can_submit_testimonial(self):
		self.client.force_login(self.author)

		response = self.client.post(self.url, {
			'text': 'همکاری بسیار خوبی بود.',
			'role': 'مدیر محصول',
		})

		self.assertEqual(response.status_code, 200)
		self.assertJSONEqual(response.content, {
			'success': True,
			'message': 'نظر شما با موفقیت ثبت شد.',
			'testimonial': {
				'author': 'colleague',
				'role': 'مدیر محصول',
				'text': 'همکاری بسیار خوبی بود.',
			},
		})
		testimonial = Testimonial.objects.get()
		self.assertEqual(testimonial.recipient, self.recipient)
		self.assertEqual(testimonial.author, self.author)
