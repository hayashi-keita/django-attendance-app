from django.urls import path
from .views import main_veiws

app_name = 'application'

urlpatterns = [
    path('applications/', main_veiws.ApplicationListView.as_view(), name='application_list'),
    path('application/create/', main_veiws.ApplicationCreateView.as_view(), name='application_create'),
]