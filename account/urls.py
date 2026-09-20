from django.contrib.auth import views as auth_views
from django.urls import path

from .views import SignUp, dashboard, onboarding, phone_login

urlpatterns = [
    path('login/', phone_login, name='login'),
    path('signup/', SignUp.as_view(), name='signup'),
    path('onboarding/', onboarding, name='onboarding'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # سایر URLها
]