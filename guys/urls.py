from django.urls import path
from . import views

app_name = 'guys'

urlpatterns = [
    path('', views.index, name='index'),
]