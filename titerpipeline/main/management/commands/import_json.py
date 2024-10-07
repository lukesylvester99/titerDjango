import json
import os
from main.models import Experiment, Sample, Sample_Metadata, Read_Pair  
from django.core.management.base import BaseCommand
from datetime import datetime 


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
            '''The experiments are saved as acronyms, but I want the full exp name to be
            saved to the db. The next few lines coelate the acronym to the exp name so that can be 
            saved to the db instead'''
            experiment_id = item.get('Experiment ID')  
            exp_names = {'SI': "Stable Infection", 'RMF': "Riv84 Merill23", 'MW': 'Mixed wMel-wWil'} 

            # Check if the experiment ID exists in the dictionary and get the full name
            if experiment_id in exp_names:
                experiment_name = exp_names[experiment_id]
            else:
                experiment_name = experiment_id  # Fallback if initials not found

            sample_id = item.get('Sample ID')    

            created_date_str = item.get('Date Collected')

             # Check if 'Date Collected' exists and is in a valid format
            created_date = None  # Default value in case no date is found
            if created_date_str:
                try:
                    # Since the Google Sheet now has the correct format, assume 'YYYY-MM-DD'
                    created_date = datetime.strptime(created_date_str, '%Y-%m-%d').date()  
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Invalid date format for sample '{sample_id}': {created_date_str}"))

            # Extract metadata fields
            sample_label = item.get('Sample Label')      
            metadata = {
                "Cell_Line": item.get('Cell Line'),
                "Infection": item.get('Infection'),
                "Initials": item.get('Initials'),
                "Split (DDMMRep)": item.get('Split (DDMMRep)'),
                "Species":item.get('Species'),
                'Replicate':item.get('Pellet Replicate'),
                "Extraction Date":item.get('Extraction Date'),
                "Timepoint":item.get('Timepoint'),
                'gDNA Conc':item.get('gDNA Conc'),
            }  
            read1_path = f"/path/to/read1_{sample_id}.fastq" 
            read2_path = f"/path/to/read2_{sample_id}.fastq"  
            plate_number = item.get('Plate Number', '0') # Default to '0' if Plate Number is not found

            #create exp
            experiment, created = Experiment.objects.get_or_create(name=experiment_name) 
            if created:
                self.stdout.write(f"Already Created Experiment: {experiment.name}")

            #create Sample
            sample, created = Sample.objects.get_or_create(
                sample_id=sample_id,
                defaults={
                    'created_date': created_date,
                    'experiment': experiment,
                    'sample_label': sample_label
                }
            )
            if created:
                print(f"Already Created Sample: {sample.sample_id}")
            else:
                sample.created_date = created_date
                sample.sample_label = sample_label
                sample.save()

            #create metadata
            sample_metadata, created = Sample_Metadata.objects.get_or_create(
                sample_id=sample,
                defaults={'metadata': metadata}
            )
            if created:
                self.stdout.write(f"Already Created Metadata for Sample: {sample.sample_id}")
            else:
                sample_metadata.metadata = metadata
                sample_metadata.save()

            #create Read Pair Path
            read_pair, created = Read_Pair.objects.get_or_create(
                read1_path=read1_path,
                sample_id=sample,
                defaults={
                    'read2_path': read2_path,
                    'plate_number': plate_number
                }
            )
            if created:
                self.stdout.write(f"Already Created Read Pair for Sample: {sample.sample_id}")
            else:
                read_pair.plate_number = plate_number
                read_pair.save()






