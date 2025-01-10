from django.urls import path
from . import views

urlpatterns = [
    path('process/<int:process_id>', views.get_process),
    path('tasks', views.tasks),
    path('tasks/<int:process_id>/<int:step_number>', views.tasks),
    path('processes', views.processes),
    path('recents', views.recents),
    path('searchprocesses', views.searchprocesses),
    path('teams', views.teams),
    path('process-associated-tasks-count/<int:parent_process_id>/<int:step_in_parent_process>',
         views.process_associated_task_count),
    path('move-task', views.move_task)
]
