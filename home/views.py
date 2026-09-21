from django.core.paginator import Paginator
from django.views.generic import TemplateView

from account.models import UserCustom

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


class ResumeBank(TemplateView):
    template_name = "home/resume_bank.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        resume_users = (
            UserCustom.objects
            .filter(is_active=True, userprofile__isnull=False)
            .select_related('userprofile')
            .order_by('-date_joined')
        )
        paginator = Paginator(resume_users, 12)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['resume_users'] = page_obj.object_list
        context['resume_count'] = paginator.count
        return context
