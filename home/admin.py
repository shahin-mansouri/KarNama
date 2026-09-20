from django.contrib import admin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'published_at', 'is_published')
	list_filter = ('is_published', 'category', 'published_at')
	search_fields = ('title', 'excerpt', 'content', 'category')
	prepopulated_fields = {'slug': ('title',)}
from django.contrib import admin

# Register your models here.
