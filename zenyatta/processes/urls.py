from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:process_id>', views.get_process),
    path('task/<int:process_id>/<int:step_number>', views.task),
    path('processes', views.processes),
    path('recents', views.recents),
    path('searchprocesses', views.searchprocesses),
    path('teams', views.teams)
]
