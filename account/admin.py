from django.contrib import admin

from .models import (
	AboutMe,
	Certificate,
	FieldOfActivity,
	Language,
	OTPCode,
	Project,
	Research,
	SocialLink,
	Skill,
	UserCustom,
	UserProfile,
	WorkExperience,
	WorkTechUse,
)


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
	list_display = ('id', 'phone_number', 'created_at', 'expires_at', 'attempts', 'used_at')
	search_fields = ('phone_number',)
	list_filter = ('used_at', 'created_at', 'expires_at')
	readonly_fields = ('code_hash', 'created_at', 'expires_at', 'attempts', 'used_at', 'session_key')
	list_per_page = 25


@admin.register(UserCustom)
class UserCustomAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'username', 'first_name', 'last_name', 'email', 'phone_number',
		'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
	)
	search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
	list_filter = ('is_staff', 'is_active', 'is_superuser')
	list_per_page = 10
	date_hierarchy = 'date_joined'
	ordering = ('-date_joined',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'user', 'title', 'bio', 'profile_picture', 'address', 'birth_date',
		'marital_status', 'military_status',
	)
	search_fields = ('user__username', 'user__first_name', 'user__last_name', 'title', 'bio', 'address')
	list_filter = ('marital_status', 'military_status')
	autocomplete_fields = ('user',)
	list_per_page = 10


@admin.register(AboutMe)
class AboutMeAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'about_me')
	search_fields = ('user__username', 'user__first_name', 'user__last_name', 'about_me')
	autocomplete_fields = ('user',)
	list_per_page = 10


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'user', 'proficiency')
	search_fields = ('name', 'user__username', 'user__first_name', 'user__last_name')
	list_filter = ('proficiency',)
	autocomplete_fields = ('user',)
	list_per_page = 10
	ordering = ('-proficiency', 'name')


@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'position', 'company_name', 'user', 'start_date', 'end_date',
		'description', 'address',
	)
	search_fields = (
		'position', 'company_name', 'user__username', 'user__first_name',
		'user__last_name', 'description',
	)
	list_filter = ('start_date', 'end_date')
	autocomplete_fields = ('user',)
	list_per_page = 10
	date_hierarchy = 'start_date'
	ordering = ('-start_date',)


@admin.register(WorkTechUse)
class WorkTechUseAdmin(admin.ModelAdmin):
	list_display = ('id', 'technology', 'work_experience')
	search_fields = ('technology', 'work_experience__position', 'work_experience__company_name')
	autocomplete_fields = ('work_experience',)
	list_per_page = 10


@admin.register(FieldOfActivity)
class FieldOfActivityAdmin(admin.ModelAdmin):
	list_display = ('id', 'name')
	search_fields = ('name',)
	list_per_page = 10


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = (
		'id', 'name', 'user', 'field_of_activity', 'technologies_used',
		'description', 'github_link', 'demo_link', 'project_picture',
	)
	search_fields = (
		'name', 'user__username', 'user__first_name', 'user__last_name',
		'technologies_used', 'description',
	)
	list_filter = ('field_of_activity',)
	autocomplete_fields = ('user', 'field_of_activity')
	list_per_page = 10


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'issuer', 'user', 'issue_date', 'certificate_link')
	search_fields = ('name', 'issuer', 'user__username', 'user__first_name', 'user__last_name')
	list_filter = ('issue_date',)
	autocomplete_fields = ('user',)
	list_per_page = 10
	date_hierarchy = 'issue_date'
	ordering = ('-issue_date',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'user', 'proficiency')
	search_fields = ('name', 'user__username', 'user__first_name', 'user__last_name')
	list_filter = ('proficiency',)
	autocomplete_fields = ('user',)
	list_per_page = 10
	ordering = ('-proficiency', 'name')


@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'user', 'description', 'year', 'link')
	search_fields = ('title', 'user__username', 'user__first_name', 'user__last_name', 'description')
	list_filter = ('year',)
	autocomplete_fields = ('user',)
	list_per_page = 10
	ordering = ('-year', '-id')


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
	list_display = ('id', 'platform', 'user', 'url')
	search_fields = ('user__username', 'user__first_name', 'user__last_name', 'url')
	list_filter = ('platform',)
	autocomplete_fields = ('user',)
	list_per_page = 10
