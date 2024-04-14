import os
import csv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_thread_by_subject(service, user_id, subject):
    try:
        # Search for the thread
        response = service.users().messages().list(userId=user_id, q='subject:"{}"'.format(subject)).execute()
        messages = response.get('messages', [])
        
        if not messages:
            return None
        else:
            # Assuming the first message is part of the required thread
            thread_id = messages[0]['threadId']
            return service.users().threads().get(userId=user_id, id=thread_id).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def save_thread_to_csv(thread, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'From', 'To', 'Subject', 'Snippet', 'Message ID', 'Thread ID'])
        
        for message in thread['messages']:
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            writer.writerow([
                headers.get('Date', ''),
                headers.get('From', ''),
                headers.get('To', ''),
                headers.get('Subject', ''),
                message.get('snippet', ''),
                message.get('id', ''),
                message.get('threadId', '')
            ])

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
USER_ID = 'me'
SUBJECT = '[crx] "Third-party cookie will be blocked" message'
FILENAME = 'third_party_cookie_thread_sample.csv'

if __name__ == '__main__':
    service = get_gmail_service()
    thread = get_thread_by_subject(service, USER_ID, SUBJECT)
    if thread:
        save_thread_to_csv(thread, FILENAME)
        print(f"Thread saved to {FILENAME}.")
    else:
        print("No thread found with the specified subject.")
