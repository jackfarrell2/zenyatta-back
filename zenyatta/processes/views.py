from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Process, Task


def get_task_data(task, index=0):
    """
    Recursively get task data inlucding all nested sub-tasks.

    Args:
        task: Task object
        index: current index for node ID (default: 0)

    Returns:
        dict: Task data including nested sub-tasks
    """
    sub_tasks = []
    if not task.is_leaf:
        this_task_process = task.linked_process
        linked_process_tasks = this_task_process.tasks.all()

        # Recursively get data for each sub-task
        for sub_index, sub_task in enumerate(linked_process_tasks):
            sub_task_data = get_task_data(sub_task, sub_index)
            sub_tasks.append(sub_task_data)

    return {
        'id': f'node-{index}',
        'label': task.title,
        'isLeaf': task.is_leaf,
        'subTasks': sub_tasks
    }


@api_view(['GET'])
def get_processes(request):
    this_process = Process.objects.get(title='Process Application')
    this_process_tasks = this_process.tasks.all()
    tasks = []

    for index, task in enumerate(this_process_tasks):
        task_data = get_task_data(task, index)
        task_data['targets'] = [
            f'node-{index + 1}'] if index < len(this_process_tasks) - 1 else []
        tasks.append(task_data)
    return Response({'data': {'tasks': tasks}})
