from django.contrib import admin

# Register your models here.
from account.models import CustomUser, UserEmail

admin.site.register(CustomUser)
admin.site.register(UserEmail)
