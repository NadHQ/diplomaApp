from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import *


# Register your models here.
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ('name', 'second_name', 'third_name', "profession", "licence")
    list_display_links = ('licence',)
    search_fields = ("name", 'second_name', 'third_name')


class LicenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'is_used')
    search_fields = ('number',)


class ResearchAdmin(admin.ModelAdmin):
    list_display = ("doctor", 'patient', "date_research", "file", "report")
    search_fields = ('date_research',)


class PatientAdmin(admin.ModelAdmin):
    list_display = ("name", "second_name", "third_name", "pass_number")
    search_fields = ('name', "second_name", "third_name", "pass_number")


class ImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'masked', 'research')


admin.site.register(get_user_model())
admin.site.register(Doctors, DoctorsAdmin)
admin.site.register(Research, ResearchAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Images, ImageAdmin)
