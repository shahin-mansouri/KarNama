from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from account.models import UserCustom

from .forms import ContactMessageForm


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
