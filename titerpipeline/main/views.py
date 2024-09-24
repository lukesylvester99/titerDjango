from django.shortcuts import render, redirect,  get_object_or_404
from django.http import HttpResponse
from main.models import Experiment, Sample, Sample_Metadata

# Create your views here.
def home(request):
    experiments_dict = Experiment.objects.values('name') #fetching data from Experiments model, returns dict
    
    #sorted list of experiments. Stores just the exp name, rather than the dict format
    experiments_value = [exp['name'] for exp in experiments_dict]

    return render(request, "home.html", {"experiments":experiments_value})

def samples_by_experiment(request):
    if request.method == 'POST':
        experiment_ID = request.POST.get('exp_selection') #get form selection from homepage
        experiment = get_object_or_404(Experiment, name=experiment_ID) #get experiment obj from db

        samples = Sample.objects.filter(experiment=experiment) #get samples associated with that exp
        metadata = Sample_Metadata.objects.filter(sample_id__in=samples)

        return render(request, "samples_list.html", {'experiment': experiment, 'samples': samples, 'metadata':metadata})
    else:
            return redirect('home')