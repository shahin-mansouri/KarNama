from django.db import models

from account.models import UserCustom


class ContactMessage(models.Model):
	recipient = models.ForeignKey(
		UserCustom,
		on_delete=models.CASCADE,
		related_name='received_messages',
	)
	name = models.CharField(max_length=120)
	email = models.EmailField()
	subject = models.CharField(max_length=200)
	message = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self):
		return f'{self.subject} from {self.name}'
