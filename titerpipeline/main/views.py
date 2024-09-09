from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(response):
    return HttpResponse("Hello World")

def v1(response):
    return HttpResponse("This is V1")