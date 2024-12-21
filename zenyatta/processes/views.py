from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def get_processes(request):
    return Response({'data': {'tasks': [{'id': 'node-1', 'type': 'task', 'position': {x: 0, y: 0}}]}})
