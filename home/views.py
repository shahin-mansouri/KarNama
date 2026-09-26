from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Case, IntegerField, Q, Value, When
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView

from account.models import UserCustom

from .models import BlogPost, Category


class Home(TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = BlogPost.objects.filter(is_published=True)[:3]
        context['blog_categories'] = Category.objects.all()
        context['successful_people'] = _resume_queryset()[:3]
        return context


class ResumeBank(TemplateView):
    template_name = "home/resume_bank.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        resume_users = _resume_queryset(query)
        paginator = Paginator(resume_users, 12)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['resume_users'] = page_obj.object_list
        context['resume_count'] = paginator.count
        context['search_query'] = query
        return context


def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True)
    paginator = Paginator(posts, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'home/blog.html', {
        'page_obj': page_obj,
        'blog_posts': page_obj.object_list,
        'blog_categories': Category.objects.all(),
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, 'home/blog_detail.html', {'post': post})


def robots_txt(request):
    content = "\n".join([
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /account/",
        "Disallow: /messages/",
        "Sitemap: https://karnamma.ir/sitemap.xml",
    ])
    return HttpResponse(content, content_type="text/plain")


def _resume_queryset(query=''):
    resume_users = (
        UserCustom.objects
        .filter(is_active=True, userprofile__isnull=False)
        .select_related('userprofile')
        .prefetch_related('skill_set')
    )

    if query:
        search_filter = (
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(userprofile__title__icontains=query)
            | Q(userprofile__bio__icontains=query)
            | Q(aboutme__about_me__icontains=query)
            | Q(skill__name__icontains=query)
            | Q(workexperience__position__icontains=query)
            | Q(workexperience__company_name__icontains=query)
            | Q(workexperience__description__icontains=query)
            | Q(project__name__icontains=query)
            | Q(project__technologies_used__icontains=query)
            | Q(project__description__icontains=query)
            | Q(project__field_of_activity__name__icontains=query)
            | Q(certificate__name__icontains=query)
            | Q(certificate__issuer__icontains=query)
            | Q(language__name__icontains=query)
            | Q(research__title__icontains=query)
            | Q(research__description__icontains=query)
            | Q(sociallink__platform__icontains=query)
        )
        resume_users = resume_users.filter(search_filter).distinct()
        resume_users = resume_users.annotate(
            relevance=(
                Case(When(username__iexact=query, then=Value(100)), default=Value(0), output_field=IntegerField())
                + Case(When(userprofile__title__icontains=query, then=Value(50)), default=Value(0), output_field=IntegerField())
                + Case(When(skill__name__icontains=query, then=Value(30)), default=Value(0), output_field=IntegerField())
                + Case(When(workexperience__position__icontains=query, then=Value(25)), default=Value(0), output_field=IntegerField())
                + Case(When(project__name__icontains=query, then=Value(20)), default=Value(0), output_field=IntegerField())
            )
        )
        return resume_users.order_by('-relevance', '-is_superuser', '-date_joined')

    return resume_users.order_by('-is_superuser', '-date_joined')
