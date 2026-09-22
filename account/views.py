from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from django.urls import reverse, reverse_lazy

from .sms_sender import SMS
from .forms import (
	AboutMeForm, CertificateForm, ExperienceForm, OTPForm, PhoneForm,
	LanguageForm, ProjectForm, ResearchForm, SignUpForm, SkillForm,
	SocialLinkForm, UserDetailsForm, UserProfileForm,
)
from .models import AboutMe, Certificate, Language, OTPCode, Project, Research, Skill, SocialLink, UserCustom, UserProfile, WorkExperience


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
				request.session.cycle_key()
				otp, code = OTPCode.issue(phone, request.session.session_key)
				try:
					response = SMS().send_code(phone, code)
					if not 200 <= response.status_code < 300:
						raise RuntimeError(f'SMS service returned HTTP {response.status_code}')
				except Exception:
					otp.delete()
					messages.error(request, 'ارسال کد تأیید انجام نشد. لطفاً دوباره تلاش کنید.')
				else:
					request.session['otp_id'] = otp.pk
					request.session['otp_step'] = 'verify'
					messages.success(request, 'کد تأیید ارسال شد.')
					return redirect('login')
		else:
			form = OTPForm(request.POST)
			if form.is_valid():
				otp = OTPCode.objects.filter(pk=request.session.get('otp_id')).first()
				if otp and otp.verify(form.cleaned_data['code'], request.session.session_key):
					phone = otp.phone_number
					user = UserCustom.objects.filter(phone_number=phone).first()
					for key in ('otp_id', 'otp_step'):
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
				request.session.pop('onboarding_phone', None)
				request.session.pop('onboarding_step', None)
				return redirect('dashboard')
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


DASHBOARD_STEPS = ('user', 'profile', 'about', 'skill', 'experience', 'project', 'certificate', 'language', 'research', 'social')
DASHBOARD_ITEMS = {
	'skill': Skill,
	'experience': WorkExperience,
	'project': Project,
	'certificate': Certificate,
	'language': Language,
	'research': Research,
	'social': SocialLink,
}


def _owned_item(user, kind, item_id):
	model = DASHBOARD_ITEMS.get(kind)
	if not model or not item_id:
		return None
	return model.objects.filter(pk=item_id, user=user).first()


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
	current_step = request.GET.get('step', 'user')
	edit_item_id = request.GET.get('edit')
	form_map = {'user': ('user_form', UserDetailsForm), 'profile': ('profile_form', UserProfileForm), 'about': ('about_form', AboutMeForm), 'skill': ('skill_form', SkillForm), 'experience': ('experience_form', ExperienceForm), 'project': ('project_form', ProjectForm), 'certificate': ('certificate_form', CertificateForm), 'language': ('language_form', LanguageForm), 'research': ('research_form', ResearchForm), 'social': ('social_form', SocialLinkForm)}
	if request.method == 'POST':
		action = request.POST.get('action')
		if action == 'delete':
			kind = request.POST.get('item_type')
			obj = _owned_item(request.user, kind, request.POST.get('item_id'))
			if obj:
				obj.delete()
				messages.success(request, 'مورد انتخاب‌شده حذف شد.')
			return redirect(f"{reverse('dashboard')}?step={kind if kind in DASHBOARD_STEPS else 'user'}")
		if action in form_map:
			current_step = action
			key, form_class = form_map[action]
			item = _owned_item(request.user, action, request.POST.get('item_id'))
			instance = item if item is not None else (forms[key].instance if action in ('user', 'profile', 'about') else None)
			if item is not None:
				edit_item_id = str(item.pk)
			form = form_class(request.POST, request.FILES, instance=instance)
			if form.is_valid():
				if action == 'user':
					form.save()
				elif action == 'profile':
					profile = form.save(commit=False)
					profile.user = request.user
					profile.save()
				elif action == 'about':
					about = form.save(commit=False)
					about.user = request.user
					about.save()
				elif action == 'experience':
					form.save_with_technologies(request.user)
				elif action == 'project':
					form.save_with_user(request.user)
				else:
					obj = form.save(commit=False)
					obj.user = request.user
					obj.save()
				messages.success(request, 'اطلاعات با موفقیت ذخیره شد.')
				return redirect(f"{reverse('dashboard')}?step={action}")
			forms[key] = form
	if current_step not in DASHBOARD_STEPS:
		current_step = 'user'
	if current_step in DASHBOARD_ITEMS and edit_item_id and request.method != 'POST':
		item = _owned_item(request.user, current_step, edit_item_id)
		if item:
			key, form_class = form_map[current_step]
			forms[key] = form_class(instance=item)
			edit_item_id = str(item.pk)
		else:
			edit_item_id = None
	elif request.method != 'POST':
		edit_item_id = None

	skills = Skill.objects.filter(user=request.user)
	experiences = WorkExperience.objects.filter(user=request.user).prefetch_related('worktechuse_set')
	projects = Project.objects.filter(user=request.user)
	certificates = Certificate.objects.filter(user=request.user)
	languages = Language.objects.filter(user=request.user)
	researches = Research.objects.filter(user=request.user)
	social_links = SocialLink.objects.filter(user=request.user)
	profile = UserProfile.objects.filter(user=request.user).first()
	about = AboutMe.objects.filter(user=request.user).first()
	filled = [
		bool(request.user.first_name and request.user.last_name),
		bool(profile and profile.title),
		bool(about and about.about_me),
		skills.exists(),
		experiences.exists(),
		projects.exists(),
		certificates.exists(),
		languages.exists(),
		researches.exists(),
		social_links.exists(),
	]
	return render(request, 'account/dashboard.html', {
		**forms,
		'skills': skills,
		'experiences': experiences,
		'projects': projects,
		'certificates': certificates,
		'languages': languages,
		'researches': researches,
		'social_links': social_links,
		'current_step': current_step,
		'edit_item_id': edit_item_id,
		'completion_percent': int(sum(filled) / len(filled) * 100),
		'total_steps': len(DASHBOARD_STEPS),
	})


class SignUp(CreateView):
	form_class = SignUpForm
	template_name = 'registration/signup.html'
	success_url = reverse_lazy('login')
