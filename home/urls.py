from django.urls import path
from .views import Home, ResumeBank, blog_detail, blog_list


urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("resume-bank/", ResumeBank.as_view(), name="resume_bank"),
    path("blog/", blog_list, name="blog_list"),
    path("blog/<str:slug>/", blog_detail, name="blog_detail"),
]