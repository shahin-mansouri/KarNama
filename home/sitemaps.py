from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from account.models import UserCustom


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "resume_bank",
        ]

    def location(self, item):
        return reverse(item)


class ProfileSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return UserCustom.objects.filter(is_active=True).order_by("username")

    def location(self, item):
        return reverse("profile", kwargs={"username": item.username})