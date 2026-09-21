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


class Testimonial(models.Model):
	recipient = models.ForeignKey(
		UserCustom,
		on_delete=models.CASCADE,
		related_name='testimonials',
		verbose_name='صاحب رزومه',
	)
	author = models.ForeignKey(
		UserCustom,
		on_delete=models.CASCADE,
		related_name='authored_testimonials',
		verbose_name='نویسنده',
	)
	text = models.TextField(max_length=600, verbose_name='متن نظر')
	role = models.CharField(max_length=120, blank=True, verbose_name='سمت یا شرکت')
	created_at = models.DateTimeField(auto_now_add=True)
	is_approved = models.BooleanField(default=True, verbose_name='تأیید شده')

	class Meta:
		ordering = ('-created_at',)
		verbose_name = 'نظر همکار'
		verbose_name_plural = 'نظرات همکاران'

	def __str__(self):
		return f'{self.author} درباره {self.recipient}'
