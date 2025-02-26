from django.contrib import admin

from .models import User, RegistrationSession

admin.site.register(User)
admin.site.register(RegistrationSession)
