from os import name
from django.urls import path
from .views import main_veiws, manager_veiws, hr_veiws

app_name = 'application'

urlpatterns = [
    path('applications/', main_veiws.ApplicationListView.as_view(), name='application_list'),
    path('application/create/', main_veiws.ApplicationCreateView.as_view(), name='application_create'),
    path('application/<int:pk>/detail/', main_veiws.ApplicationDetailView.as_view(), name='application_detail'),
    path('application/<int:pk>/update/', main_veiws.ApplicationUpdateView.as_view(), name='application_update'),
    path('application/<int:pk>/delete/', main_veiws.ApplicationDeleteView.as_view(), name='application_delete'),
    # 上司関連
    path('manager/applications/', manager_veiws.MnagerApplicationListView.as_view(), name='manager_application_list'),
    path('manager-application/<int:pk>/detail/', manager_veiws.ManagerApplicationDetailView.as_view(), name='manager_application_detail'),
    # 人事関連
    path('hr/applications/', hr_veiws.HrApplicationListView.as_view(), name='hr_application_list'),
    path('hr-application/<int:pk>/detail/', hr_veiws.HrApplicationDetailView.as_view(), name='hr_application_detail'),
]