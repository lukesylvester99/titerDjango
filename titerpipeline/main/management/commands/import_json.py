import json
import os
from main.models import Experiment, Sample, Sample_Metadata, Read_Pair  
from django.core.management.base import BaseCommand
from datetime import datetime 
import random #for plate num. Delete once ready to deploy

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Determine the correct path to the JSON file
        base_dir = os.path.dirname(os.path.abspath(__file__))  # was having trouble with the path to the json file so I used this instead of a direct path
        json_file_path = os.path.join(base_dir, 'cleaned_migration.json')

        # Load JSON data from file
        with open(json_file_path, 'r') as file:  
            data = json.load(file)

        #filter json obj to get the fields I want/need
        for item in data:
            experiment_name = item.get('Experiment ID')  
            sample_id = item.get('Sample ID')    

            created_date_str = item.get('Date Collected')

            # Check if 'Date Collected' exists and is in a valid format
            if created_date_str:
                try: # From sheet migration, the 'Date Collected' field is incorrect and needs to be in YYYY-MM-DD format
                    created_date = datetime.strptime(created_date_str, '%Y-%m-%dT%H:%M:%S.%fZ').date() 
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Invalid date format for sample '{sample_id}': {created_date_str}"))
                    created_date = None  #in case there isnt an extraction/created date
            else:
                created_date = None  #in case there isnt an extraction/created date


            sample_label = item.get('Sample Label')      
            metadata = {
                "Cell_Line": item.get('Cell Line'),
                "Infection": item.get('Infection'),
                "Initials": item.get('Initials'),
                "Split (DDMMRep)": item.get('Split (DDMMRep)')
            }  
            read1_path = f"/path/to/read1_{sample_id}.fastq" 
            read2_path = f"/path/to/read2_{sample_id}.fastq"  
            plate_number = random.randint(1, 4)  

            #create exp
            experiment, created = Experiment.objects.get_or_create(name=experiment_name) 
            if created:
                self.stdout.write(f"Already Created Experiment: {experiment.name}")

            #create Sample
            sample, created = Sample.objects.get_or_create(
                sample_id=sample_id,
                created_date=created_date,
                experiment=experiment,
                sample_label=sample_label
            )
            if created:
                print(f"Already Created Sample: {sample.sample_id}")

            #create metadata
            sample_metadata, created = Sample_Metadata.objects.get_or_create(
                sample_id=sample,
                metadata=metadata
            )
            if created:
                self.stdout.write(f"Already Created Metadata for Sample: {sample.sample_id}")

            #create Read Pair Path
            read_pair, created = Read_Pair.objects.get_or_create(
                read1_path=read1_path,
                read2_path=read2_path,
                sample_id=sample,
                plate_number=plate_number
            )
            if created:
                self.stdout.write(f"Already Created Read Pair for Sample: {sample.sample_id}")






