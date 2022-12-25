
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [

    path('admin/users',AllUsersView.as_view(),name='staffs'),
    path('admin/shifts', ShiftView.as_view(),name='shifts'),
    path('admin/staff/create', CreateStaffView.as_view(),name='create_staff'),
    path('admin/staff', StaffView.as_view(),name='staff'),
    path('admin/shift/assign', AssignShiftView.as_view(),name='assign_shift'),
    path('admin/staff/account', AccountView.as_view(),name='staff_account'),
    path('admin/attendance', AllAttendanceView.as_view(),name='all_attendance'),
    path('admin/staff/attendance', AttendanceDetailView.as_view(),name='staff_attendance'),
    path('admin/attendance/delete', DeleteAttendanceView.as_view(),name='delete_attendance'),
    path('admin/attendance/create', CreateAttendanceView.as_view(),name='create_attendance'),
    path('admin/shifts/delete', DeleteShiftView.as_view(),name='delete_shift'),
    path('admin/shifts/edit', EditShiftView.as_view(),name='edit_shift'),
    path('admin/attendance/delete/all', DeleteAllAttendanceView.as_view(),name='delete_all_attendance'),
    path('admin/shifts/delete/all', DeleteAllShiftView.as_view(),name='delete_all_shifts'),

    path('admin/staff/send_schedule', SendSchedule.as_view(),name='staff_send_schedule'),
    path('admin/staff/create_send_schedule', CreateSendSchedule.as_view(),name='staff_create_send_schedule'),
    
    path('admin/staff/attended', AttendedView.as_view(),name='staff_account'),
    path('admin/staffs/reassign', ReAssignStaffsToShiftView.as_view(),name='staff_reassign'),
    path('admin/shifts/attendance/delete', DeleteAllShiftAttendanceView.as_view(),name='staff_reassign'),
    path('admin/facility', FacilityView.as_view(),name='facility'),
    path('admin/facility/staff/assign', AssignStaffToFacilityView.as_view(),name='assign_facility'),
        
    path('facility/staff/remove',RemoveStaffFacilityView.as_view(), name='facility_users_remove'),
    path('admin/attendance/filter',AttendanceFilterView.as_view(), name='attendance_filter'),


]