import imp
from django.contrib import admin
from django.urls import path
from django.urls import include, re_path
from . import views as authviews
from rest_framework.routers import DefaultRouter
from .views import *

# routers = DefaultRouter()
# routers.register('users',authviews.UserList,basename= "users")
# routers.register('users/paginate',authviews.UserListPaginated,basename= "users_paginated")

urlpatterns = [

    path('staff/attendance/',AttendanceView.as_view(),name='staff_attendance'),
    path('staff/shift/<str:pk>/',ShiftsDetailView.as_view(),name='staff_notes'),
    path('staff/dashboard',StaffDashBoardView.as_view(),name='staff_dashboard'),

    # Note: Staff profile url using same view as dashboard url, just get only profile credentials
    # path('staff/profle',StaffDashBoardView.as_view(),name='staff_dashboard'),

    path('staff/attendance',AttendanceView.as_view(),name='staff_attendance'),
    path('staff/past-shift',PastShiftsView.as_view(),name='past_shift'),
    path('staff/account',AccountView.as_view(),name='account'),
    path('staff/start/attendance',TakeStartAttendanceView.as_view(),name='start_attendance'),
    path('staff/end/attendance',TakeEndAttendanceView.as_view(),name='end_attendance'),
    path('staff/profile/update',UpdateProfileView.as_view(),name='update_profile'),
    path('staff/facilities',FacilitiesView.as_view(),name='facilities'),


]

