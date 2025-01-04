from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Process, Task


def get_task_data(task):
    """
    Recursively get task data including all nested sub-tasks.

    Args:
        task: Task object
        index: current index for node ID (default: 0)

    Returns:
        dict: Task data including nested sub-tasks
    """

    sub_tasks = []
    linked_process_id = None
    if not task.is_leaf:
        this_task_process = task.linked_process
        linked_process_id = this_task_process.pk
        linked_process_tasks = this_task_process.tasks.all()

        # Recursively get data for each sub-task
        for sub_task in linked_process_tasks:
            sub_task_data = get_task_data(sub_task)
            sub_tasks.append(sub_task_data)

    parent_process = task.process
    try:
        next_step = [
            f'node-{Task.objects.get(process=parent_process, step_number=task.step_number + 1).pk}']
    except:
        next_step = []

    return {
        'id': f'node-{task.pk}',
        'stepNumber': task.step_number,
        'label': task.title,
        'isLeaf': task.is_leaf,
        'subTasks': sub_tasks,
        'linkedProcessId': linked_process_id,
        'parentProcessId': parent_process.id,
        'targets': next_step
    }


@api_view(['GET'])
def get_process(request, process_id):
    try:
        try:
            this_process = Process.objects.get(pk=process_id)
        except:
            return Response({'error': 'Invalid process Id'}, status=500)
        this_process_tasks = this_process.tasks.all()
        tasks = []

        for task in this_process_tasks:
            task_data = get_task_data(task)
            tasks.append(task_data)
        return Response({'data': {'title': this_process.title, 'tasks': tasks}})
    except:
        return Response({'error': 'Server error'}, status=500)


@api_view(['GET', 'PUT'])
def task(request, process_id, step_number):
    if request.method == 'GET':
        try:
            tasks_process = Process.objects.get(pk=process_id)
            task = tasks_process.tasks.get(step_number=step_number)
            return Response({'data': {'title': 'title', 'content': task.content}})
        except:
            return Response({'error': 'Server error'}, status=500)
    elif request.method == 'PUT':
        try:
            tasks_process = Process.objects.get(pk=process_id)
            task = tasks_process.tasks.get(step_number=step_number)
            task.content = request.data['content']
            task.save()
            return Response({'message': 'Task updated successfully'})
        except:
            return Response({'error': 'Server error'}, status=500)
    else:
        return Response({'error': 'Invalid request method'}, status=400)
