from django.urls import path
from .views import Home, ResumeBank


urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("resume-bank/", ResumeBank.as_view(), name="resume_bank"),
]