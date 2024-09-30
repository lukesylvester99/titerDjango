from django.shortcuts import render, redirect,  get_object_or_404
from main.models import Experiment, Sample, Sample_Metadata, Read_Pair
from .forms import SampleFilterForm
from django.db.models import Q


def home(request):
    #fetching data from Experiments model, returns dict
    experiments_dict = Experiment.objects.values('name') 
        #sorted list of experiments. Stores just the exp name, rather than the dict format
    experiments_value = [exp['name'] for exp in experiments_dict]

    #get meta data so that I can extract the obj later in html form
    metadata = Sample_Metadata.objects.all()
    
    # Collect unique infection values from metadata
    unique_infections = set()
    for meta in metadata:
        for key, value in meta.metadata.items():
            if key == 'Infection':
                unique_infections.add(value)
    
     # Collect unique Cell Lines values from metadata
    unique_cell_lines = set()
    for meta in metadata:
        for key, value in meta.metadata.items():
            if key == 'Cell Line':
                unique_cell_lines.add(value)
    
     # Collect unique Users from metadata
    unique_users = set()
    for meta in metadata:
        for key, value in meta.metadata.items():
            if key == 'Initials':
                unique_users.add(value)

    #holds plate numbers in data
    plate_num_dict = Read_Pair.objects.values("plate_number")
    plate_num_value = [num['plate_number'] for num in plate_num_dict] 
    unique_plate_num_value = list(set(plate_num_value))#filters so each num is only represented once
   
    vars = {
        "experiments":experiments_value,
        'infections':unique_infections, 
        'cell_lines':unique_cell_lines,
        "users":unique_users,
        "plate_num":unique_plate_num_value }

    return render(request, "home.html", vars)

def samples_by_experiment(request):
    if request.method == 'POST':
        experiment_ID = request.POST.get('exp_selection') #get form selection from homepage
        experiment = get_object_or_404(Experiment, name=experiment_ID) #get experiment obj from db

        samples = Sample.objects.filter(experiment=experiment) #get samples associated with that exp
        metadata = Sample_Metadata.objects.filter(sample_id__in=samples)

        return render(request, "samples_list.html", {'experiment': experiment, 'samples': samples, 'metadata':metadata})
    else:
            return redirect('home')
    

def filter_samples(request):
    form = SampleFilterForm(request.POST or None)

    # Start with a basic query, get all samples
    samples = Sample.objects.all()

    if request.method == 'POST' and form.is_valid():
        cell_type = form.cleaned_data['cell_type']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        infection_status = form.cleaned_data['infection_status']

        # Build the filter dynamically
        query = Q()

        if cell_type:
            query &= Q(metadata__cell_line=cell_type)

        if start_date and end_date:
            query &= Q(created_date__range=[start_date, end_date])

        if infection_status:
            query &= Q(metadata__infection=infection_status)

        # Apply the filter to the samples queryset
        samples = samples.filter(query)

    # Render the page with the form and filtered samples
    return render(request, 'filtered_samples.html', {
        'form': form,
        'samples': samples,
    })