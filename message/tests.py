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

	def test_recipient_can_list_and_open_messages(self):
		contact_message = ContactMessage.objects.create(
			recipient=self.recipient,
			name='Visitor',
			email='visitor@example.com',
			subject='A new opportunity',
			message='Please contact me.',
		)
		self.client.force_login(self.recipient)

		list_response = self.client.get(reverse('message_list'))
		self.assertContains(list_response, 'A new opportunity')
		self.assertContains(list_response, 'is-unread')

		detail_response = self.client.get(reverse('message_detail', args=[contact_message.pk]))
		self.assertEqual(detail_response.status_code, 200)
		self.assertContains(detail_response, 'Please contact me.')
		self.assertTrue(ContactMessage.objects.get(pk=contact_message.pk).is_read)

	def test_other_user_cannot_open_message(self):
		other_user = UserCustom.objects.create_user(
			username='other',
			email='other@example.com',
			phone_number='09123456780',
			password='test-password',
		)
		contact_message = ContactMessage.objects.create(
			recipient=self.recipient,
			name='Visitor',
			email='visitor@example.com',
			subject='Private message',
			message='Private content.',
		)
		self.client.force_login(other_user)

		response = self.client.get(reverse('message_detail', args=[contact_message.pk]))
		self.assertEqual(response.status_code, 404)
		self.assertFalse(ContactMessage.objects.get(pk=contact_message.pk).is_read)
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
