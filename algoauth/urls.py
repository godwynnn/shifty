import imp
from django.contrib import admin
from django.urls import path
from django.urls import include, re_path
from . import views as authviews
from rest_framework.routers import DefaultRouter



urlpatterns = [
    path('', authviews.Home.as_view(),name='home'),
    path('user', authviews.UserView.as_view(),name='user'),
    path('users', authviews.AllUserView.as_view(),name='users'),
    path('user/create', authviews.CreateUserView.as_view(),name='create_user'),
    path('user/delete', authviews.DeleteUserView.as_view(),name='delete_user'),
    path("auth/login", authviews.LoginView.as_view(), name="login"),
    path("auth/check-email", authviews.CheckEmail.as_view(), name="checkemail"),
    path("auth/change_password/request", authviews.RequestChangePasswordView.as_view(), name="request_change_password"),
    path("auth/change_password/confirm", authviews.VerifyPasswordRequestCode.as_view(), name="request_change_password_confirm"),
    path("auth/confirm-email", authviews.ConfirmEmail.as_view(), name="confirm_email"),
    path('auth/logout',authviews.LogoutView,name='logout')
]

