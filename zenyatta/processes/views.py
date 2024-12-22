from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def get_processes(request):
    return Response({'data': {'tasks': [{'id': 'node-1', 'label': 'Verify Identification', 'targets': ['node-2']}, {'id': 'node-2', 'label': 'Run Credit Report', 'targets': ['node-3']}, {'id': 'node-3', 'label': 'Calculate Premium Fee', 'targets': ['node-4']}, {'id': 'node-4', 'label': 'Calculate Coverage Amount', 'targets': ['node-5']}, {'id': 'node-5', 'label': 'Issue Approval / Denial', 'targets': []}]}})
