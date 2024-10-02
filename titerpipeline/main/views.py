from django.shortcuts import render, redirect,  get_object_or_404
from main.models import Experiment, Sample, Sample_Metadata, Read_Pair
import csv
from django.http import HttpResponse


"""home page that contains the form for selecting samples associated 
with an experiment, as well as the custom filter"""

def home(request):
    #fetching data from Experiments model, returns dict
    experiments_dict = Experiment.objects.values('name') 
        #sorted list of experiments. Stores just the exp name, rather than the dict format
    experiments_value = [exp['name'] for exp in experiments_dict]

    """Code below this is for populating the custom query/filter form. 
    I need each value saved in its own variable so that they can be passed to the html pg"""
    #get all meta data so that I can extract the obj I want
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
    unique_plate_num_value = list(set(plate_num_value)) #filters so each num is only represented once
    
    #passed to html form
    vars = {
        "experiments":experiments_value,
        'infections':unique_infections, 
        'cell_lines':unique_cell_lines,
        "users":unique_users,
        "plate_num":unique_plate_num_value }

    return render(request, "home.html", vars)


"""After a user selects an exp in the homepage, they are directed to this page which lists all the 
samples associated with that experiment"""

def samples_by_experiment(request):
    if request.method == 'POST':
        experiment_ID = request.POST.get('exp_selection') #get form selection from homepage
        experiment = get_object_or_404(Experiment, name=experiment_ID) #get experiment obj from db

        samples = Sample.objects.filter(experiment=experiment) #get samples associated with that exp
        metadata = Sample_Metadata.objects.filter(sample_id__in=samples)

        return render(request, "samples_list.html", {'experiment': experiment, 'samples': samples, 'metadata':metadata})
    else:
            return redirect('home')
    
"""If a user wants to create a custom filter, they can do so on the homepage. This route lists out 
the information of the filtered samples"""

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

    # Filtering by user/lab member
    if users:
        samples = samples.filter(sample_metadata__metadata__Initials=users)

    # Filtering by plate number from Read_Pair model
    if plate_num:
        samples = samples.filter(read_pair__plate_number=plate_num)

    # Get all related metadata and read pairs for the filtered samples
    #have to filter the models by sample_id since that is the foreign key in the models
    sample_ids = samples.values_list('id', flat=True) 
    metadata = Sample_Metadata.objects.filter(sample_id__in=sample_ids) 
    read_pairs = Read_Pair.objects.filter(sample_id__in=sample_ids)

    #passed to html form
    vars = {
        #holds sample information from the filter that was created on homepage
        "samples": samples,
        "metadata": metadata,  
        "read_pairs": read_pairs,
        
        #copy the filter criteria from the homepage and post it to the hidden form. 
        #this is needed for the export_csv route, so that it can reapply the same filter for the csv file
        'cell_line':cell_line, 
        'start_date':start_date,
        'end_date':end_date,
        "infection":infection_status,
        "users":users,
        "plate_num":plate_num,

        }

    return render(request, 'filtered_samples.html', vars)



def export_csv(request):
    # Get filter criteria from the GET request
    cell_line = request.GET.get('cell_line', None)
    infection_status = request.GET.get('infection_status', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    users = request.GET.get('users', None)
    plate_num = request.GET.get('plate_num', None)

    """Repeating filter that was applied on homepage"""
    # Initialize the samples QuerySet
    samples = Sample.objects.all()

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

    # Filtering by user/lab member (Initials field in metadata)
    if users:
        samples = samples.filter(sample_metadata__metadata__Initials=users)

    # Filtering by plate number from Read_Pair model
    if plate_num:
        samples = samples.filter(read_pair__plate_number=plate_num)

    # Get all related metadata and read pairs for the filtered samples
    sample_ids = samples.values_list('id', flat=True)
    metadata = Sample_Metadata.objects.filter(sample_id__in=sample_ids)
    read_pairs = Read_Pair.objects.filter(sample_id__in=sample_ids)

    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="filtered_samples.csv"'

    writer = csv.writer(response)
    writer.writerow(['Sample ID', 'Cell Line', 'Infection Status', 'Created Date', 'Plate Number', 'Read 1 Path', 'Read 2 Path'])

    # Write each row of data
    for sample in samples:
        # Accessing metadata and related read pair info for the sample
        metadata_instance = metadata.filter(sample_id=sample.id).first()
        read_pair_instance = read_pairs.filter(sample_id=sample.id).first()

        # Extracting the JSON fields from the metadata object
        cell_line = metadata_instance.metadata.get("Cell_Line", "") if metadata_instance else ""
        infection = metadata_instance.metadata.get("Infection", "") if metadata_instance else ""

        # Extracting read pair information
        plate_number = read_pair_instance.plate_number if read_pair_instance else ''
        read1_path = read_pair_instance.read1_path if read_pair_instance else ''
        read2_path = read_pair_instance.read2_path if read_pair_instance else ''

        writer.writerow([sample.sample_id, cell_line, infection, sample.created_date, plate_number, read1_path, read2_path])

    return response