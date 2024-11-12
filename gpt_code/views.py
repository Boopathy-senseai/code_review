from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
import json
from django.http import HttpResponse,JsonResponse

class about(generics.GenericAPIView):
    def get(self, request):
        data = {
            'Name': 'Boopathy',
            'Role': 'backend developer',
            'org':'Sense7ai',
            'yoe':1.5,
            'devops':'aws',
            'goal':'SRE',
            'skills':'python,terraform,aws,azure',
            'container':'good in dockerize the application with kubernete',
            'iac':'Ansible automation and well in redhat'
        }
        return JsonResponse(data)
class career(generics.GenericAPIView):
    def get(self, request):
        data = {
            'career': 'Junior software developer',
            'Role': 'backend developer',
            'drop out':'aeronautical engineer',
           'education':'mechanical engineer'
        }
        return JsonResponse(data)