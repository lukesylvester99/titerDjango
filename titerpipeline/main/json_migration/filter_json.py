import json
from ..models import Experiment, Sample, Sample_Metadata, Read_Pair  

# Load JSON data from file
with open('./cleaned_migration.json', 'r') as file:  
    data = json.load(file)

for item in data:
    #filter json obj to get the fields I want/need
    experiment_name = item.get('Experiment ID')  
    sample_id = item.get('Sample ID')            
    created_date = item.get('Date Collected')    
    sample_label = item.get('Sample Label')      
    metadata = {
        "Cell Line": item.get('Cell Line'),
        "Infection": item.get('Infection'),
        "Initials": item.get('Initials'),
        "Split (DDMMRep)": item.get('Split (DDMMRep)')
    }  
    read1_path = f"/path/to/read1_{sample_id}.fastq" 
    read2_path = f"/path/to/read2_{sample_id}.fastq"  
    plate_number = 1  

    #create exp
    experiment, created = Experiment.objects.get_or_create(name=experiment_name) 
    if created:
        print(f"Already Created Experiment: {experiment.name}")

    #create Sample
    sample, created = Sample.objects.get_or_create(
        sample_id=sample_id,
        created_date=created_date,
        experiment=experiment
    )
    if created:
        print(f"Already Created Sample: {sample.sample_id}")

    #create metadata
    sample_metadata, created = Sample_Metadata.objects.get_or_create(
        sample=sample,
        metadata=metadata
    )
    if created:
        print(f"Already Created Metadata for Sample: {sample.sample_id}")

    #create Read Pair Path
    read_pair, created = Read_Pair.objects.get_or_create(
        read1_path=read1_path,
        read2_path=read2_path,
        sample=sample,
        plate_number=plate_number
    )
    if created:
        print(f"Created Read Pair for Sample: {sample.sample_id}")
