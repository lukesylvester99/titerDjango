from django.shortcuts import render, redirect,  get_object_or_404
from main.models import Experiment, Sample, Sample_Metadata, Read_Pair



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
            if key == 'Cell_Line':
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
    # Initialize an empty queryset for the Sample model
    samples = Sample.objects.all()  

    # Access the form data from POST request
    cell_line = request.POST.get('cell_line', None)
    start_date = request.POST.get('start_date', None)
    end_date = request.POST.get('end_date', None)
    infection_status = request.POST.get('infection_status', None)
    users = request.POST.get('users', None)
    plate_num = request.POST.get('plate_num', None)


    # Filtering by cell line from Sample_Metadata JSON field
    if cell_line:
        samples = samples.filter(sample_metadata__metadata__Cell_Line=cell_line) 

    # Filter by date range (assuming created_date is in Sample model)
    if start_date:
        samples = samples.filter(created_date__gte=start_date)

    if end_date:
        samples = samples.filter(created_date__lte=end_date)

    # Filtering by infection status from Sample_Metadata JSON field
    if infection_status:
        samples = samples.filter(sample_metadata__metadata__Infection=infection_status)

    # Filtering by user (assuming 'user' is a field in Sample or related model)
    if users:
        samples = samples.filter(sample_metadata__metadata__Initials=users)

    # Filtering by plate number from Read_Pair model
    if plate_num:
        samples = samples.filter(read_pair__plate_number=plate_num)

    # Render the filtered samples to the template
    return render(request, 'filtered_samples.html', {'samples': samples})