from django.contrib import admin

from .models import (
	AboutMe,
	Certificate,
	FieldOfActivity,
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


@admin.register(UserCustom)
class UserCustomAdmin(admin.ModelAdmin):
	list_display = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff')
	search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
	list_filter = ('is_staff', 'is_active', 'is_superuser')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'title', 'birth_date', 'marital_status', 'military_status')
	search_fields = ('user__username', 'title')


@admin.register(AboutMe)
class AboutMeAdmin(admin.ModelAdmin):
	list_display = ('user',)
	search_fields = ('user__username', 'about_me')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'proficiency')
	search_fields = ('name', 'user__username')
	list_filter = ('proficiency',)


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
	list_display = ('position', 'company_name', 'user', 'start_date', 'end_date')
	search_fields = ('position', 'company_name', 'user__username')
	list_filter = ('start_date', 'end_date')


@admin.register(WorkTechUse)
class WorkTechUseAdmin(admin.ModelAdmin):
	list_display = ('technology', 'work_experience')
	search_fields = ('technology', 'work_experience__position')


@admin.register(FieldOfActivity)
class FieldOfActivityAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'field_of_activity')
	search_fields = ('name', 'user__username', 'technologies_used')
	list_filter = ('field_of_activity',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
	list_display = ('name', 'issuer', 'user', 'issue_date')
	search_fields = ('name', 'issuer', 'user__username')
	list_filter = ('issue_date',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'proficiency')
	search_fields = ('name', 'user__username')


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
	list_display = ('title', 'user', 'year')
	search_fields = ('title', 'user__username')
	list_filter = ('year',)


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
	list_display = ('platform', 'user', 'url')
	search_fields = ('user__username', 'url')
