import os
from dotenv import  load_dotenv, dotenv_values
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

#print(os.getenv("client_email"))

# Construct the service account information from environment variables
service_account_info = {
    "type": os.getenv("GOOGLE_TYPE"),
    "project_id": os.getenv("GOOGLE_PROJECT_ID"),
    "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'), 
    "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
    "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
    "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
}

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
client = gspread.authorize(creds)


sheet_id = '12Cy2HZpVzzzu_erg2XMXCAd19XY88hfhDKUOA5MIDGs' #replace with real id once testing is done!!
sheet = client.open_by_key(sheet_id)

values_list = sheet.sheet6.row_values(1)
print(values_list)