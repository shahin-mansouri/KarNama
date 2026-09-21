from django import forms

from .models import ContactMessage, Testimonial


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ('text', 'role')
        widgets = {
            'text': forms.Textarea(attrs={'maxlength': 600}),
        }
