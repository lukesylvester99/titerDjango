from django.shortcuts import render
from django.http import HttpResponse
from main.models import Experiment

# Create your views here.
def home(request):
    experiments_dict = Experiment.objects.values('name') #fetching data from Experiments model, returns dict
    
    #sorted list of experiments. Stores just the exp name, rather than the dict format
    experiments_value = [exp['name'] for exp in experiments_dict]

    return render(request, "home.html", {"experiments":experiments_value})

def v1(response):
    return HttpResponse("This is V1")