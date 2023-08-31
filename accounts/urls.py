from django.urls import path
from . import views

urlpatterns = [
    path('sign-up', views.signUp, name="sign-up"),
    path('sign-in', views.signIn, name="sign-in"),
    path('my-account', views.myAccount, name="my-account"),
    path('sign-out', views.signOut, name="sign-out")
]
