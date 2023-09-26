from django.urls import path
from . import views

urlpatterns = [
    path('sign-up', views.signUp, name="sign-up"),
    path('sign-in', views.signIn, name="sign-in"),
    path('my-account', views.myAccount, name="my-account"),
    path('my-account/order/<int:order_id>', views.myOrder, name="my-order"),
    path('sign-out', views.signOut, name="sign-out"),
    path('forgot-password', views.forgotPassword, name="forgot-password"),
    path('check-email', views.checkEmail, name='check-email'),
    ###
    path('activate-account/<uidb64>/<token>', views.activateAccount, name="activate-account"),
    path('reset-password/<uidb64>/<token>', views.resetPassword, name="reset-password")
]
