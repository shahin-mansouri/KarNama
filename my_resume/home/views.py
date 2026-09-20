from django.views.generic import TemplateView

from .models import BlogPost


class Home(TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = BlogPost.objects.filter(is_published=True)[:3]
        context['blog_categories'] = (
            BlogPost.objects.filter(is_published=True)
            .values_list('category', flat=True)
            .distinct()[:6]
        )
        return context
