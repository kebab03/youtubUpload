import threading
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import random
import videoDetails
from oauth2client import client # Added
from oauth2client import tools # Added
from oauth2client.file import Storage # Added
import http.client
import httplib2
import time
import videoDetails

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (IOError, http.client.NotConnected, http.client.IncompleteRead,
                        http.client.ImproperConnectionState, http.client.CannotSendRequest,
                        http.client.CannotSendHeader, http.client.ResponseNotReady, http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = 'client_secrets.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

API_SERVICE_NAME = 'youtube'

API_VERSION = 'v3'

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')


def get_authenticated_service():
    credential_path = os.path.join('./', 'credential_sample.json')
    store = Storage(credential_path)
    credentials = store.get()

    print(f" credentials prma :=  ", credentials)
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRETS_FILE, SCOPES)
        print(f" flow  ",type(flow))
        #print(f" flow.keys()  ",  flow.keys())
        credentials = tools.run_flow(flow, store)

        print(f" credentials dpo  :=  ",credentials)

        print("Access token:", credentials.access_token)
        print("Refresh token:", credentials.refresh_token)
        print("Client ID:", credentials.client_id)
        print("Client secret:", credentials.client_secret)
        print("Token expiry:", credentials.token_expiry)

    #https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-module.html#build
        #Returns:
  #A Resource object with methods for interacting with the service.

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            #   è il comando che fa la Upload
            """    
build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
                .videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
                )
                    .next_chunk()
"""

            if response is not None:
                if 'id' in response:
                    print(f'Video id "{response["id"]}" was successfully uploaded.')
                else:
                    exit(f'The upload failed with an unexpected response: {response}')
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f'A retriable HTTP error {e.resp.status} occurred:\n{e.content}'
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f'A retriable error occurred: {e}'

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('No longer attempting to retry.')

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print(f'Sleeping {sleep_seconds} seconds and then retrying...')
            time.sleep(sleep_seconds)

numer =0
def initialize_upload(youtube, file_path, description, category, keywords, privacyStatus, semaphore):
    # Acquisire il semaforo per evitare che più thread eseguano upload contemporaneamente
    global numer
    print("Sono  in  initialize_upload  numer = ",numer)
    print(f" in initialize_upload file_path =====", file_path)
    with semaphore:
        tags = None
        if keywords:
            tags = keywords.split(',')

        body = dict(
            snippet=dict(
                title=os.path.splitext(os.path.basename(file_path))[0],  # Usa il nome del file senza estensione
                description=description,
                tags=tags,
                categoryId=category
            ),
            status=dict(
                privacyStatus=privacyStatus
            )
        )

        insert_request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )
        numer += 1
        resumable_upload(insert_request)


# Funzione per iterare sui file nella directory ed eseguire un thread alla volta
def upload_videos_from_directory(youtube, directory, description, category, keywords, privacyStatus):
    # Creare un semaforo che permette a un solo thread di eseguire alla volta
    semaphore = threading.Semaphore(1)

    for file in os.listdir(directory):
        if file.endswith(".mp4"):  # Filtra i file con estensione .mp4
            file_path = os.path.join(directory, file)
            print(f" upl   file_path =====",file_path)
            # Creare un thread per ciascun upload
            thread = threading.Thread(target=initialize_upload, args=(youtube, file_path, description, category, keywords, privacyStatus, semaphore))
            thread.start()
            thread.join()  # Attendere che il thread finisca prima di avviare il prossimo




if __name__ == '__main__':
    args = videoDetails.Video
    youtube = get_authenticated_service()

    try:
        # Passiamo la directory e i dettagli del video
        upload_videos_from_directory(youtube, "I:\\MVideos", args.description, args.category, args.keywords, args.privacyStatus)
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
