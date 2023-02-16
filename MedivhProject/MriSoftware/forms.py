from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from .models import *


class AddUserPatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}),
            'second_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}),
            'third_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}),
            'pass_number': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}),
        }


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}))
    password1 = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'floatingPassword'}))
    password2 = forms.CharField(label='Повторите пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'floatingPassword'}))
    id_linecse = forms.CharField(label='Номер Лицензии',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingPassword'}))

    class Meta:
        model = User
        fields = ('username', 'password1')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'id': 'floatingPassword'})
        }

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data["username"]
        user.set_password(self.cleaned_data["password1"])
        try:
            objection = License.objects.get(number=self.cleaned_data["id_linecse"], is_used=False)
            user.linecse = objection
            objection.is_used = True
            objection.save()
            doctor = Doctors(name='Name', second_name='SecondName', third_name='ThirdName', profession='Proffesion',
                             licence=objection)
            doctor.save()
        except ObjectDoesNotExist:
            return user
        if commit:
            user.save()
        return user


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'floatingPassword'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Doctors
        fields = "__all__"
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}),
            'second_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}),
            'third_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'}),
            'licence': forms.TextInput(attrs={'class': 'form-control', 'id': 'floatingInput'})
        }


class ImageInputForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = '__all__'
