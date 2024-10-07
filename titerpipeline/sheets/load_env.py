import os
from dotenv import  load_dotenv, dotenv_values
import gspread
from google.oauth2.service_account import Credentials
import json

load_dotenv()

#print(os.getenv("client_email"))

# Construct the service account information from environment variables
service_account_info = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace('\\n', '\n'), 
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
}

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
client = gspread.authorize(creds)


sheet_id = '12Cy2HZpVzzzu_erg2XMXCAd19XY88hfhDKUOA5MIDGs' #replace with real id once testing is done!!
sheet = client.open_by_key(sheet_id)

values_list = sheet.worksheets()

names = []
for worksheet in values_list:
    name = worksheet.title
    if name not in ["Instructions", "Experiment Template", "Experiments Summary", "Needs Extraction"]:
        names.append(name)

json_data = []
for name in names:
    worksheet = sheet.worksheet(name)
    all_records = worksheet.get_all_records()


    # Filter out rows where Column E ('Date Collected') is empty
    filtered_records = [row for row in all_records if row.get('Date Collected')] 

    json_string = json.dumps(filtered_records)
    json_data.append(json_string)


# Directory where json file will be saved.
output_dir = r'C:\Users\lukes\OneDrive\Documents\GitHub\titerDjango\titerpipeline\main\management\commands'
output_file = os.path.join(output_dir, 'cleaned_migration.json')

with open(output_file, 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

print(f"JSON data successfully saved to {output_file}")