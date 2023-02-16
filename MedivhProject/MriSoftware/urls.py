from django.urls import path
from .views import *
urlpatterns = [
    path('', LoginUser.as_view(), name='login'),
    path('registration/', RegisterUser.as_view(), name='registration'),
    path('main/', research, name='research'),
    path('archive/', archive, name='archive'),
    path('report/', report, name='report'),
    path('start/', start, name='start'),
    path('profile/', open_profile, name='profile'),
    path('about/', about, name='about'),
    # path('login')
]
