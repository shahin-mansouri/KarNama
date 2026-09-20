from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ('subject', 'name', 'email', 'recipient', 'created_at', 'is_read')
	search_fields = ('name', 'email', 'subject', 'message', 'recipient__username')
	list_filter = ('is_read', 'created_at')
	readonly_fields = ('created_at',)
from django.contrib import admin

# Register your models here.
