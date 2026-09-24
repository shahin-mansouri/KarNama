from django.urls import path

from .views import add_testimonial, message_detail, message_list, send_message

urlpatterns = [
	path('', message_list, name='message_list'),
	path('<int:pk>/', message_detail, name='message_detail'),
	path('<str:username>/send/', send_message, name='send_message'),
	path('<str:username>/testimonial/', add_testimonial, name='add_testimonial'),
]


