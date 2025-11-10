from ast import main
from django.urls import path

from attendance.views import manager_views
from .views import main_views, hr_views

app_name = 'attendance'

urlpatterns = [
    # トップページ
    path('', main_views.Index.as_view(), name='index'),
    # 勤怠記録
    path('attendance/dashboard/', main_views.AttendanceDashboardView.as_view(), name='dashboard'),
    path('attendances/', main_views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/<int:pk>/detail/', main_views.AttendanceDetailView.as_view(), name='attendance_detail'),
    # 人事権限
    path('hr/attendances/', hr_views.HrAttendanceListView.as_view(), name='hr_attendance_list'),
    path('hr/attendance/create/', hr_views.HrAttendanceCreateView.as_view(), name='hr_attendance_create'),
    path('hr/attendance/<int:pk>/detail/', hr_views.HrAttendanceDetailView.as_view(), name='hr_attendance_detail'),
    path('hr/attendance/<int:pk>/update/', hr_views.HrAttendanceUpdateView.as_view(), name='hr_attendance_update'),
    path('hr/attendance/<int:pk>/delete/', hr_views.HrAttendanceDeleteView.as_view(), name='hr_attendance_delete'),
    # 上司権限
    path('manager/attendances/', manager_views.ManagerAttendanceListView.as_view(), name='manager_attendance_list'),
]