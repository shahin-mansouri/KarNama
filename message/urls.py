from django.urls import path

from .views import send_message

urlpatterns = [
	path('<str:username>/send/', send_message, name='send_message'),
]


