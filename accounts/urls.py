from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    # 部署関連
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('department/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('department/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('department/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    # 課関連
    path('teams/', views.TeamListView.as_view(), name='team_list'),
    path('team/create/', views.TeamCreateView.as_view(), name='team_create'),
    path('team/<int:pk>/update/', views.TeamUpdateView.as_view(), name='team_update'),
    path('team/<int:pk>/delete/', views.TeamDeleteView.as_view(), name='team_delete'),
    # アカウント関連
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', views.CustomUserLoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('hr-signup/', views.HrSignUpView.as_view(), name='hr_signup'),
    path('profiles/', views.CustomUserListView.as_view(), name='profile_list'),
    path('profile/<int:pk>/approve/', views.UserApproveView.as_view(), name='user_approve'),
    path('profile/<int:pk>/detail/', views.CustomUserDetailView.as_view(), name='profile_detail'),
    path('profile/<int:pk>/update/', views.CustomUserUpdateView.as_view(), name='profile_update'),
    path('profile/<int:pk>/delete/', views.CustomUserDeleteView.as_view(), name='profile_delete'),
    # パスワード関連
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change_done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]