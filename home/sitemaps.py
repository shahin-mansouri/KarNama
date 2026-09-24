from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from account.models import UserCustom
from .models import BlogPost


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "resume_bank",
            "blog_list",
        ]

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def location(self, item):
        return reverse("blog_detail", kwargs={"slug": item.slug})


class ProfileSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return UserCustom.objects.filter(is_active=True).order_by("username")

    def location(self, item):
        return reverse("profile", kwargs={"username": item.username})