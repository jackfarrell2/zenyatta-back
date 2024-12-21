from django.urls import path
from . import views

urlpatterns = [
    path('processes', views.get_processes)
]
