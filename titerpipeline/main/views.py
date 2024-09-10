from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, "home.html")

def v1(response):
    return HttpResponse("This is V1")