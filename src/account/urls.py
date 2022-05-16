from django.urls import path, include

from account import views

app_name = 'app_account'
urlpatterns = [
    path('api/', include('account.api.v1.urls', namespace='app_account_api'))
]
