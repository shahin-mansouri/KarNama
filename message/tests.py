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

# Create your tests here.
