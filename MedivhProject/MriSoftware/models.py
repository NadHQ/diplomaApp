import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    linecse = models.ForeignKey('License', on_delete=models.CASCADE, null=True)


def upload_link(instance):
    return 'user_{0}/{1}/{2}'.format(instance.research.doctor.licence.number,
                                                    instance.research.patient.pass_number, filename)


def upload_imageMasked(instance):
    return 'user_{0}/{1}/masked/{2}'.format(instance.research.doctor.licence.number,
                                                    instance.research.patient.pass_number, filename)


def upload_imageOriginal(instance, filename):
    print(instance)
    print(filename)
    return 'user_{0}/{1}/original/{2}'.format(instance.research.doctor.licence.number,
                                           instance.research.patient.pass_number, filename)


class Doctors(models.Model):
    name = models.CharField(max_length=40)
    second_name = models.CharField(max_length=40)
    third_name = models.CharField(max_length=40)
    profession = models.CharField(max_length=40)
    licence = models.ForeignKey('License', on_delete=models.CASCADE)

    class Meta:
        ordering = ['name', 'second_name', 'profession']

class Research(models.Model):
    doctor = models.ForeignKey('Doctors', on_delete=models.PROTECT)
    patient = models.ForeignKey('Patient', on_delete=models.PROTECT)
    date_research = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=upload_link, null=True, max_length=200)
    report = models.FileField(upload_to=upload_link, null=True, max_length=200)

    class Meta:
        ordering = ['date_research', 'doctor']

class License(models.Model):
    number = models.UUIDField(default=uuid.uuid4, editable=False)
    is_used = models.BooleanField(default=False)


class Patient(models.Model):
    name = models.CharField(max_length=40)
    second_name = models.CharField(max_length=40)
    third_name = models.CharField(max_length=40)
    pass_number = models.CharField(max_length=40)
    class Meta:
        ordering = ['name', 'second_name', 'pass_number']

class Images(models.Model):
    research = models.ForeignKey('Research', on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to=upload_imageOriginal, max_length=200)
    masked = models.ImageField(upload_to=upload_imageMasked, max_length=200)
