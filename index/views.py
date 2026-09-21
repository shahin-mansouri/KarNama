from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from account.models import (
    AboutMe,
    Certificate,
    Language,
    Project,
    Research,
    SocialLink,
    Skill,
    UserCustom,
    UserProfile,
    WorkExperience,
    WorkTechUse,
)
from message.models import Testimonial


class Index(TemplateView):
    template_name = "index/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        owner = get_object_or_404(UserCustom, username__iexact=self.kwargs['username'])

        skills = Skill.objects.filter(user=owner)
        experiences = WorkExperience.objects.filter(user=owner).prefetch_related('worktechuse_set')
        projects = Project.objects.filter(user=owner).select_related('field_of_activity')
        certificates = Certificate.objects.filter(user=owner).order_by('-issue_date', '-id')
        languages = Language.objects.filter(user=owner)
        researches = Research.objects.filter(user=owner)
        social_links = SocialLink.objects.filter(user=owner)
        profile = UserProfile.objects.filter(user=owner).first()
        about = AboutMe.objects.filter(user=owner).first()
        testimonials = Testimonial.objects.filter(
            recipient=owner,
            is_approved=True,
        ).select_related('author')[:12]
        experience_data = []
        for experience in experiences[::-1]:
            experience_data.append({
                'position': experience.position,
                'company': experience.company_name,
                'location': owner.address or '',
                'start': experience.start_date.year,
                'end': experience.end_date.year if experience.end_date else 'اکنون',
                'desc': experience.description or '',
                'techs': list(experience.worktechuse_set.values_list('technology', flat=True)),
            })

        context['profile'] = profile
        context['owner'] = owner
        context['portfolio_data'] = {
            'personal': {
                'name': owner.get_full_name() or owner.username,
                'title': profile.title if profile else 'توسعه‌دهنده نرم‌افزار',
                'bio': profile.bio if profile else '',
                'address': profile.address if profile and profile.address else owner.address or '',
                'birth_date': profile.birth_date.isoformat() if profile and profile.birth_date else '',
                'marital_status': profile.get_marital_status_display() if profile and profile.marital_status else '',
                'military_status': profile.get_military_status_display() if profile and profile.military_status else '',
            },
            'about': about.about_me if about else (profile.bio if profile else ''),
            'skills': [
                {'name': skill.name, 'level': skill.proficiency}
                for skill in skills
            ],
            'experience': experience_data,
            'projects': [
                {
                    'id': project.id,
                    'title': project.name,
                    'desc': project.description or '',
                    'tech': project.technologies_used,
                    'category': project.field_of_activity.name,
                    'github': project.github_link or '#',
                    'demo': project.demo_link or '#',
                    'project_picture': project.project_picture.url if project.project_picture else '/static/index/images/project-placeholder.png',
                }
                for project in projects[::-1]
            ],
            'certificates': [
                {
                    'name': certificate.name,
                    'issuer': certificate.issuer,
                    'date': certificate.issue_date.year if certificate.issue_date else '',
                    'link': certificate.certificate_link or '#',
                }
                for certificate in certificates
            ],
            'languages': [
                {'name': language.name, 'level': language.proficiency}
                for language in languages
            ],
            'researches': [
                {'title': research.title, 'description': research.description or '', 'year': research.year, 'link': research.link or '#'}
                for research in researches
            ],
            'social_links': [
                {'platform': social.platform, 'label': social.get_platform_display(), 'url': social.url}
                for social in social_links
            ],
            'stats': {
                'projects': projects.count(),
                'experience': experiences.count(),
                'technologies': WorkTechUse.objects.filter(work_experience__user=owner).count(),
                'certifications': certificates.count(),
            },
            'testimonials': [
                {
                    'author': testimonial.author.get_full_name() or testimonial.author.username,
                    'role': testimonial.role,
                    'text': testimonial.text,
                }
                for testimonial in testimonials
            ],
        }
        return context


# class Home(TemplateView):
#     template_name = "index/home.html"

