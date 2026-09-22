from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import (
    AboutMe, Certificate, FieldOfActivity, Project, Skill, UserCustom,
    Language, Research, SocialLink, UserProfile, WorkExperience, WorkTechUse,
)


class PhoneForm(forms.Form):
    phone_number = forms.CharField(label='شماره تماس', max_length=11)


class OTPForm(forms.Form):
    code = forms.CharField(label='کد تأیید', max_length=6, min_length=6)


class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = UserCustom
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'address')
        labels = {'username': 'نام کاربری', 'first_name': 'نام', 'last_name': 'نام خانوادگی', 'email': 'ایمیل', 'phone_number': 'شماره تماس', 'address': 'آدرس'}
        widgets = {'phone_number': forms.TextInput(attrs={'readonly': True})}


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('title', 'bio', 'profile_picture', 'address', 'birth_date', 'marital_status', 'military_status')
        labels = {'title': 'عنوان شغلی', 'bio': 'معرفی کوتاه', 'profile_picture': 'تصویر پروفایل', 'address': 'آدرس', 'birth_date': 'تاریخ تولد', 'marital_status': 'وضعیت تاهل', 'military_status': 'وضعیت سربازی'}
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}


class AboutMeForm(forms.ModelForm):
    class Meta:
        model = AboutMe
        fields = ('about_me',)
        labels = {'about_me': 'درباره من'}


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ('name', 'proficiency')
        labels = {'name': 'نام مهارت', 'proficiency': 'درصد تسلط'}


class ExperienceForm(forms.ModelForm):
    technologies = forms.CharField(label='فناوری‌ها', required=False, help_text='فناوری‌ها را با ویرگول جدا کنید.')

    class Meta:
        model = WorkExperience
        fields = ('position', 'company_name', 'start_date', 'end_date', 'description')
        labels = {'position': 'سمت شغلی', 'company_name': 'نام شرکت', 'start_date': 'تاریخ شروع', 'end_date': 'تاریخ پایان', 'description': 'توضیحات'}
        widgets = {'start_date': forms.DateInput(attrs={'type': 'date'}), 'end_date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['technologies'].initial = ', '.join(
                self.instance.worktechuse_set.values_list('technology', flat=True)
            )

    def save_with_technologies(self, user):
        experience = self.save(commit=False)
        experience.user = user
        experience.save()
        WorkTechUse.objects.filter(work_experience=experience).delete()
        for technology in self.cleaned_data.get('technologies', '').split(','):
            technology = technology.strip()
            if technology:
                WorkTechUse.objects.create(work_experience=experience, technology=technology)
        return experience


class ProjectForm(forms.ModelForm):
    field_name = forms.CharField(label='حوزه فعالیت', max_length=100)

    class Meta:
        model = Project
        fields = ('name', 'technologies_used', 'description', 'github_link', 'demo_link', 'project_picture')
        labels = {'name': 'نام پروژه', 'technologies_used': 'فناوری‌های استفاده‌شده', 'description': 'توضیحات', 'github_link': 'لینک گیت‌هاب', 'demo_link': 'لینک نسخه نمایشی', 'project_picture': 'تصویر پروژه'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.field_of_activity_id:
            self.fields['field_name'].initial = self.instance.field_of_activity.name

    def save_with_user(self, user):
        project = self.save(commit=False)
        project.user = user
        field, _ = FieldOfActivity.objects.get_or_create(name=self.cleaned_data['field_name'].strip())
        project.field_of_activity = field
        project.save()
        return project


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ('name', 'issuer', 'issue_date', 'certificate_link')
        labels = {'name': 'نام گواهینامه', 'issuer': 'صادرکننده', 'issue_date': 'تاریخ دریافت', 'certificate_link': 'لینک گواهینامه'}
        widgets = {'issue_date': forms.DateInput(attrs={'type': 'date'})}


class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ('name', 'proficiency')
        labels = {'name': 'نام زبان', 'proficiency': 'درصد تسلط'}


class ResearchForm(forms.ModelForm):
    class Meta:
        model = Research
        fields = ('title', 'description', 'year', 'link')
        labels = {'title': 'عنوان تحقیق', 'description': 'توضیحات تحقیق', 'year': 'سال تحقیق', 'link': 'لینک مراجعه به تحقیق'}


class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ('platform', 'url')
        labels = {'platform': 'شبکه اجتماعی', 'url': 'لینک صفحه'}


class SignUpForm(UserCreationForm):
    class Meta:
        model = UserCustom
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
