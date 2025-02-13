from django.contrib import admin

from .models import (
    Achievement,
    Affiliation,
    Degree,
    Department,
    Doctor,
    LanguageSpoken,
    Schedule,
    Specialty,
)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(LanguageSpoken)
class LanguageSpokenAdmin(admin.ModelAdmin):
    search_fields = ['language']
    list_display = ["uid", "language"]

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    search_fields = ['doctor__user__username']

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Affiliation)
class AffiliationAdmin(admin.ModelAdmin):
    search_fields = ['title', 'hospital_name']
