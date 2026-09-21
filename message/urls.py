from django.urls import path

from .views import add_testimonial, send_message

urlpatterns = [
	path('<str:username>/send/', send_message, name='send_message'),
	path('<str:username>/testimonial/', add_testimonial, name='add_testimonial'),
]


