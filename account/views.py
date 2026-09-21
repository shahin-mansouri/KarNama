import secrets
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import (
	AboutMeForm, CertificateForm, ExperienceForm, OTPForm, PhoneForm,
	LanguageForm, ProjectForm, ResearchForm, SignUpForm, SkillForm,
	SocialLinkForm, UserDetailsForm, UserProfileForm,
)
from .models import AboutMe, Certificate, Language, Research, Skill, SocialLink, UserCustom, UserProfile, WorkExperience


def normalize_phone(value):
	return value.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')).replace(' ', '').replace('-', '')


def phone_login(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	step = request.session.get('otp_step', 'phone')
	if request.method == 'POST':
		if step == 'phone':
			form = PhoneForm(request.POST)
			if form.is_valid():
				phone = normalize_phone(form.cleaned_data['phone_number'])
				code = f'{secrets.randbelow(1000000):06d}'
				request.session['otp_phone'] = phone
				request.session['otp_code'] = code
				request.session['otp_expires'] = (timezone.now() + timedelta(minutes=5)).isoformat()
				request.session['otp_step'] = 'verify'
				print(f'[KarNama OTP] {phone}: {code}')
				messages.success(request, 'کد تأیید ارسال شد. در محیط توسعه کد در console نمایش داده می‌شود.')
				return redirect('login')
		else:
			form = OTPForm(request.POST)
			if form.is_valid():
				expires = request.session.get('otp_expires', '')
				valid_time = expires and timezone.now() < timezone.datetime.fromisoformat(expires)
				if form.cleaned_data['code'] == request.session.get('otp_code') and valid_time:
					phone = request.session['otp_phone']
					user = UserCustom.objects.filter(phone_number=phone).first()
					for key in ('otp_code', 'otp_expires', 'otp_step'):
						request.session.pop(key, None)
					if user:
						login(request, user)
						return redirect('dashboard')
					request.session['onboarding_phone'] = phone
					return redirect('onboarding')
				form.add_error('code', 'کد واردشده نادرست یا منقضی شده است.')
	else:
		form = OTPForm() if step == 'verify' else PhoneForm()
	return render(request, 'registration/login.html', {'form': form, 'otp_step': step, 'otp_phone': request.session.get('otp_phone')})


def onboarding(request):
	if not request.session.get('onboarding_phone'):
		return redirect('dashboard')
	step = int(request.session.get('onboarding_step', 0))
	if step > 0 and not request.user.is_authenticated:
		return redirect('login')
	forms = [UserDetailsForm, UserProfileForm, AboutMeForm, SkillForm, ExperienceForm, ProjectForm, CertificateForm, LanguageForm, ResearchForm, SocialLinkForm]
	form_class = forms[step]
	if request.method == 'POST':
		data = request.POST.copy()
		if step == 0:
			data['phone_number'] = request.session['onboarding_phone']
		form = form_class(data, request.FILES, instance=request.user if step == 0 and request.user.is_authenticated else None)
		if form.is_valid():
			if step == 0:
				user = form.save(commit=False)
				user.phone_number = request.session['onboarding_phone']
				user.set_unusable_password()
				user.save()
				login(request, user)
			elif step == 1:
				UserProfile.objects.update_or_create(user=request.user, defaults=form.cleaned_data)
			elif step == 2:
				AboutMe.objects.update_or_create(user=request.user, defaults=form.cleaned_data)
			elif step == 3:
				skill = form.save(commit=False)
				skill.user = request.user
				skill.save()
			elif step == 4:
				form.save_with_technologies(request.user)
			elif step == 5:
				form.save_with_user(request.user)
			elif step == 6:
				obj = form.save(commit=False)
				obj.user = request.user
				obj.save()
			else:
				obj = form.save(commit=False)
				obj.user = request.user
				obj.save()
			if step == len(forms) - 1:
				request.session.pop('onboarding_phone', None)
				request.session.pop('onboarding_step', None)
				return redirect('dashboard')
			request.session['onboarding_step'] = step + 1
			return redirect('onboarding')
	else:
		if step == 0 and not request.user.is_authenticated:
			form = form_class(initial={'phone_number': request.session['onboarding_phone']})
		else:
			form = form_class(instance=request.user if step == 0 else None)
	return render(request, 'account/onboarding.html', {'form': form, 'step': step + 1, 'total_steps': len(forms)})


@login_required
def dashboard(request):
	forms = {
		'user_form': UserDetailsForm(instance=request.user),
		'profile_form': UserProfileForm(instance=UserProfile.objects.filter(user=request.user).first()),
		'about_form': AboutMeForm(instance=AboutMe.objects.filter(user=request.user).first()),
		'skill_form': SkillForm(), 'experience_form': ExperienceForm(),
		'project_form': ProjectForm(), 'certificate_form': CertificateForm(),
		'language_form': LanguageForm(), 'research_form': ResearchForm(), 'social_form': SocialLinkForm(),
	}
	if request.method == 'POST':
		action = request.POST.get('action')
		form_map = {'user': ('user_form', UserDetailsForm), 'profile': ('profile_form', UserProfileForm), 'about': ('about_form', AboutMeForm), 'skill': ('skill_form', SkillForm), 'experience': ('experience_form', ExperienceForm), 'project': ('project_form', ProjectForm), 'certificate': ('certificate_form', CertificateForm), 'language': ('language_form', LanguageForm), 'research': ('research_form', ResearchForm), 'social': ('social_form', SocialLinkForm)}
		if action in form_map:
			key, form_class = form_map[action]
			instance = forms[key].instance if action in ('user', 'profile', 'about') else None
			form = form_class(request.POST, request.FILES, instance=instance)
			if form.is_valid():
				if action == 'user':
					form.save()
				elif action == 'profile':
					form.save()
				elif action == 'about':
					form.save()
				elif action == 'experience':
					form.save_with_technologies(request.user)
				elif action == 'project':
					form.save_with_user(request.user)
				elif action in ('language', 'research', 'social'):
					obj = form.save(commit=False)
					obj.user = request.user
					obj.save()
				else:
					obj = form.save(commit=False)
					obj.user = request.user
					obj.save()
				messages.success(request, 'اطلاعات با موفقیت ذخیره شد.')
				return redirect('dashboard')
			forms[key] = form
	return render(request, 'account/dashboard.html', {
		**forms,
		'skills': Skill.objects.filter(user=request.user),
		'experiences': WorkExperience.objects.filter(user=request.user),
		'certificates': Certificate.objects.filter(user=request.user),
		'languages': Language.objects.filter(user=request.user),
		'researches': Research.objects.filter(user=request.user),
		'social_links': SocialLink.objects.filter(user=request.user),
	})


class SignUp(CreateView):
	form_class = SignUpForm
	template_name = 'registration/signup.html'
	success_url = reverse_lazy('login')
