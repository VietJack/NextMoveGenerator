from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('nextmove', views.next_move_maker),
    path('obtain-auth-token/', obtain_auth_token),
]