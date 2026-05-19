from django.urls import path
from . import views

app_name = 'guys'

urlpatterns = [
    path('', views.index, name='index'),
    path('load/', views.load, name='load'),
    path('random/', views.random_guy, name='random'),
    path('<int:user_id>/', views.detail, name='detail'),
]