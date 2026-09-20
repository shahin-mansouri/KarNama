from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from account.models import (
    AboutMe,
    Certificate,
    Project,
    Skill,
    UserCustom,
    UserProfile,
    WorkExperience,
    WorkTechUse,
)


class Index(TemplateView):
    template_name = "index/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        owner = get_object_or_404(UserCustom, username__iexact=self.kwargs['username'])

        skills = Skill.objects.filter(user=owner)
        experiences = WorkExperience.objects.filter(user=owner).prefetch_related('worktechuse_set')
        projects = Project.objects.filter(user=owner).select_related('field_of_activity')
        certificates = Certificate.objects.filter(user=owner).order_by('-issue_date', '-id')
        profile = UserProfile.objects.filter(user=owner).first()
        about = AboutMe.objects.filter(user=owner).first()
        experience_data = []
        for experience in experiences:
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
        context['portfolio_data'] = {
            'personal': {
                'name': owner.get_full_name() or owner.username,
                'title': profile.title if profile else 'توسعه‌دهنده نرم‌افزار',
                'bio': profile.bio if profile else '',
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
                for project in projects
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
            'stats': {
                'projects': projects.count(),
                'experience': experiences.count(),
                'technologies': WorkTechUse.objects.filter(work_experience__user=owner).count(),
                'certifications': certificates.count(),
            },
        }
        return context


# class Home(TemplateView):
#     template_name = "index/home.html"

