import shutil
import time
from datetime import date    
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]  # Scope for uploading files
def file(dir_name):
    
    output_filename = ("World backup " + date.today().isoformat())
    output_path = shutil.make_archive(output_filename, 'zip', dir_name)
    global zip_filepath
    global zip_filename
    zip_filepath = os.path.basename(output_path)
    zip_filename = output_filename
def authenticate():
    """ Authenticates and returns a service object to interact with Google Drive API. """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("drive", "v3", credentials=creds)

def upload_zip_file(service, zip_filepath, zip_filename):
    """ Uploads a ZIP file to Google Drive using resumable upload. """
    file_metadata = {
        'name': zip_filename,
        'mimeType': 'application/zip'
    }
    media = MediaFileUpload(zip_filepath, mimetype='application/zip', resumable=True)

    try:
        print("Upload starting")
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded")
        
        print(f"File '{zip_filename}' uploaded successfully. File ID: {response.get('id')}")

    except HttpError as e:
        error_content = e.content if e.content else e
        print(f"An error occurred while uploading file '{zip_filename}': {error_content}")
    except Exception as e:
        print(f"An unknown error occurred while uploading file '{zip_filename}': {str(e)}")
def timer():
    service = authenticate()
    days = int(input("How often should the backup run? (enter a number of days greater than 0) "))
    seconds = days * 24 * 60 * 60
    dir_name = str(input("enter the file path to backup (it must be a directory)"))
    while True:
        file(dir_name)
        upload_zip_file(service, zip_filepath, zip_filename)
        os.remove(zip_filepath)
        print("waiting", days,  "days")
        time.sleep(seconds)
def main():

   timer() 

if __name__ == "__main__":
    main()
