from django.urls import path
from .views import Index# , Home


urlpatterns = [
    # path("", Home.as_view(), name="home"),
    path("<str:username>/", Index.as_view(), name="profile"),
]

