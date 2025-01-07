from django.shortcuts import render
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Process, Task, Company, Team
from django.utils import timezone
from rest_framework import status, serializers
from json import loads, JSONDecodeError


class ProcessCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    teamId = serializers.IntegerField()
    steps = serializers.ListField(
        child=serializers.CharField(max_length=255),
        min_length=1
    )


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
        'targets': next_step,
        'teamId': parent_process.team.pk
    }


@api_view(['GET'])
def get_process(request, process_id):
    try:
        try:
            this_process = Process.objects.get(pk=process_id)
            this_process.last_opened = timezone.now()
            this_process.save()
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


@api_view(['GET', 'POST'])
def processes(request):
    try:
        if request.method == 'GET':
            company_pk = 1  # Hard coded for now
            company = Company.objects.get(pk=company_pk)
            teams = company.teams.all()
            processes = []
            for team in teams:
                team_processes_struct = []
                team_processes = team.processes.filter(is_primary=True)
                for process in team_processes:
                    team_processes_struct.append(
                        {'name': process.title, 'id': process.pk})
                processes.append(
                    {'team': team.name, 'team_processes': team_processes_struct})
            return Response({'data': {'processes': processes}})
        elif request.method == 'POST':
            try:
                try:
                    data = loads(request.body)
                except JSONDecodeError:
                    return Response(
                        {'error': 'Invalid JSON format'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Validate the data structure
                serializer = ProcessCreateSerializer(data=data)
                if not serializer.is_valid():
                    return Response(
                        {'error': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Validate team exists
                try:
                    team = Team.objects.get(pk=data['teamId'])
                except Team.DoesNotExist:
                    return Response(
                        {'error': 'Team not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                title = data['name']
                is_primary = data['isPrimary']
                team = Team.objects.get(pk=data['teamId'])
                process = Process(
                    title=title, is_primary=is_primary, team=team)
                try:
                    process.clean()
                    process.save()
                except ValidationError as e:
                    return Response(
                        {'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                processId = process.pk
                for index, step in enumerate(data['steps']):
                    task = Task(title=step, process=process,
                                step_number=index + 1)
                    try:
                        task.clean()
                        task.save()
                    except ValidationError as e:
                        process.delete()
                        return Response(
                            {'error': f'Invalid task data: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)
                if is_primary is False:
                    if 'parentProcessId' not in data or 'stepInParentProcess' not in data:
                        process.delete()
                        return Response(
                            {'error': 'Missing parentProcessId or stepInParentProcess'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    parent_process_id = data['parentProcessId']
                    task_step = data['stepInParentProcess']
                    try:
                        parent_process = Process.objects.get(
                            pk=parent_process_id)
                    except Process.DoesNotExist:
                        process.delete()
                        return Response(
                            {'error': 'Parent process does not exist'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    try:
                        previousProcessTask = Task.objects.get(
                            process=parent_process,
                            step_number=task_step
                        )
                    except Task.DoesNotExist:
                        process.delete()
                        return Response(
                            {'error': 'Parent process task not found for given step'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    previousProcessTask.is_leaf = False
                    previousProcessTask.linked_process = process
                    previousProcessTask.save()
                    return Response({'data': {'processId': parent_process_id, 'companyId': parent_process.team.company.pk, 'message': 'Process created successfully'}}, status=status.HTTP_200_OK)
                else:
                    return Response({'data': {'processId': processId, 'companyId': process.team.company.pk, 'message': 'Process created successfully'}}, status=status.HTTP_200_OK)
            except:
                return Response({'error': 'Server error'}, status=500)
        else:
            return Response({'error': 'Invalid request'}, status=400)
    except:
        return Response({'error': 'Server error'}, status=500)


@api_view(['GET'])
def searchprocesses(request):
    try:
        if request.method == 'GET':
            search_processes = []
            company_pk = 1  # hard coded for now
            company = Company.objects.get(pk=company_pk)
            processes = Process.objects.filter(
                team__company_id=company_pk,
                is_primary=True
            )
            for process in processes:
                search_processes.append({'name': process.title, 'companyId': company_pk,
                                        'processId': process.pk, 'lastOpened': process.last_opened})
            return Response({'data': {'searchProcesses': search_processes}})
        else:
            return Response({'error': 'Invalid request method'}, status=400)
    except:
        return Response({'error': 'Server error'}, status=500)


@api_view(['GET'])
def recents(request):
    try:
        recent_files = []
        if request.method == 'GET':
            recent_files_data = Process.objects.filter(
                last_opened__isnull=False, is_primary=True).order_by('-last_opened')[:5]
            for file in recent_files_data:
                recent_files.append({'id': file.pk, 'name': file.title, 'lastOpened': file.last_opened,
                                    'location': file.team.name, 'companyId': file.team.company.pk})
            return Response({'data': {'recentFiles': recent_files}})
        else:
            return Response({'error': 'Invalid reqeust method'}, status=400)
    except:
        return Response({'error': 'Server error'}, status=500)


@api_view(['GET'])
def teams(request):
    try:
        if request.method == 'GET':
            teams = []
            all_teams = Team.objects.all()
            for team in all_teams:
                teams.append(
                    {'name': team.name, 'companyId': team.company.id, 'id': team.pk})
            return Response({'data': {'teams': teams}})
        else:
            return Response({'error': 'Invalid request method'}, status=400)
    except:
        return Response({'error': 'Server error'}, status=500)


@api_view(['GET'])
def process_associated_task_count(request, parent_process_id, step_in_parent_process):
    try:
        parent_process = Process.objects.get(pk=parent_process_id)
        task_to_convert = Task.objects.get(
            process=parent_process, step_number=step_in_parent_process)

        if task_to_convert.linked_process:
            count = count_associated_tasks(task_to_convert.linked_process)
            return Response({'data': {'tasksToDeleteCount': count}})
        else:
            return Response({'error': 'Not a valid process to convert'}, status=status.HTTP_400_BAD_REQUEST)

    except:
        return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def count_associated_tasks(process):
    """Recursively counts all tasks associated with a process and its linked processes. Returns total count of tasks."""
    if not process:
        return 0

    total_count = 0

    # Count direct tasks
    for task in process.tasks.all():
        total_count += 1

        # If task links to another process, recursively count its tasks
        if not task.is_leaf and task.linked_process:
            total_count += count_associated_tasks(task.linked_process)

    return total_count
