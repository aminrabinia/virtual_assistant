from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from google.auth import default
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv()) # read local .env file

json_path = 'per-assis.json'
# Check if the JSON file exists
if os.path.exists(json_path):
    # Load the credentials from the service account JSON file
    credentials = service_account.Credentials.from_service_account_file(json_path)
else:
    # JSON file exists, use it to obtain credentials
    credentials, project = default()

# Create a service client for the Google Docs API
service = build('docs', 'v1', credentials=credentials)

# Retrieve the document content
document_id  = os.environ['DOC_ID']
document = service.documents().get(documentId=document_id).execute()

# Access the document content
content = document['body']['content']

# Helper function to extract text from text elements
def extract_text(element):
    text = ''
    if 'textRun' in element:
        text_run = element['textRun']
        text += text_run['content']
    elif 'paragraph' in element:
        paragraph = element['paragraph']
        for element in paragraph['elements']:
            text += extract_text(element)
    elif 'table' in element:
        table = element['table']
        for row in table['tableRows']:
            for cell in row['tableCells']:
                for element in cell['content']:
                    text += extract_text(element)
                text += '\t'
    # Handle other element types here if needed
    return text

# Extract text from the document content
def read_my_doc():
    text_content = ''
    for element in content:
        text_content += extract_text(element)
    return text_content

# print(read_my_doc())

