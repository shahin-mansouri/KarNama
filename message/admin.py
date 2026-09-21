from django.contrib import admin

from .models import ContactMessage, Testimonial


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ('subject', 'name', 'email', 'recipient', 'created_at', 'is_read')
	search_fields = ('name', 'email', 'subject', 'message', 'recipient__username')
	list_filter = ('is_read', 'created_at')
	readonly_fields = ('created_at',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
	list_display = ('author', 'recipient', 'role', 'created_at', 'is_approved')
	search_fields = ('author__username', 'recipient__username', 'text', 'role')
	list_filter = ('is_approved', 'created_at')
	readonly_fields = ('created_at',)
from django.contrib import admin

# Register your models here.
