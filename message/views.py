from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from account.models import UserCustom

from .forms import ContactMessageForm, TestimonialForm
from .models import ContactMessage


@login_required
def message_list(request):
	messages = ContactMessage.objects.filter(recipient=request.user)
	return render(request, 'message/message.html', {'messages': messages})


@login_required
def message_detail(request, pk):
	contact_message = get_object_or_404(
		ContactMessage,
		pk=pk,
		recipient=request.user,
	)
	if not contact_message.is_read:
		contact_message.is_read = True
		contact_message.save(update_fields=('is_read',))
	return render(request, 'message/message_detail.html', {'message': contact_message})


@require_POST
def send_message(request, username):
	recipient = get_object_or_404(UserCustom, username__iexact=username)
	form = ContactMessageForm(request.POST)

	if not form.is_valid():
		return JsonResponse({'success': False, 'errors': form.errors}, status=400)

	contact_message = form.save(commit=False)
	contact_message.recipient = recipient
	contact_message.save()

	return JsonResponse({
		'success': True,
		'message': 'پیام شما با موفقیت ارسال شد.',
	})


@login_required
@require_POST
def add_testimonial(request, username):
	recipient = get_object_or_404(UserCustom, username__iexact=username)
	form = TestimonialForm(request.POST)

	if not form.is_valid():
		return JsonResponse({'success': False, 'errors': form.errors}, status=400)

	testimonial = form.save(commit=False)
	testimonial.recipient = recipient
	testimonial.author = request.user
	testimonial.save()

	return JsonResponse({
		'success': True,
		'message': 'نظر شما با موفقیت ثبت شد.',
		'testimonial': {
			'author': request.user.get_full_name() or request.user.username,
			'role': testimonial.role,
			'text': testimonial.text,
		},
	})
