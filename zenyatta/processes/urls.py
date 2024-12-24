from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:process_id>', views.get_process)
]
