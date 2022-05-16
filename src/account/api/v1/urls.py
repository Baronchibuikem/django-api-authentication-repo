from django.urls import path

from account.api.v1 import views

app_name = 'app_account_api'
urlpatterns = [
    path('register', views.UserRegistration.as_view(), name='api_registration'),
    path('login', views.UserLoginView.as_view(), name='api_login'),
    path('change-password', views.UserChangePasswordView.as_view(), name='api_change_password'),
    path('logout', views.UserLogoutView.as_view(), name='api_logout')
]