import os.path
import base64
import json
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_door_dash(msg):
    vals = re.findall("DoorDash Order",msgs)


def get_email_body(msg):
    if 'payload' not in msg:
        return None
    
    payload = msg['payload']
    
    if 'parts' in payload:
        # Handle multipart messages
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                data = part['body'].get('data')
                if data:
                    # First decode base64
                    text = base64.urlsafe_b64decode(data).decode('utf-8')
                    # Then decode quoted-printable if needed
                    return quopri.decodestring(text).decode('utf-8', errors='ignore')
    elif 'body' in payload:
        # Handle single part messages
        data = payload['body'].get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
    
    return None

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
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

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me").execute()
    messages = results.get("messages", [])

    if not messages:
      print("No messages found.")
      return
    print("Messages:")
    valid = [] 
    for message in messages:
        # see https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages#Message
        result = service.users().messages().get(userId="me",id=message['id']).execute()
        # stuff is already in json but this should make more sense
        snippet = result['snippet'].lower() 
        #poggers regex
        if re.search(r'doordash|uber receipt',snippet):
            valid.append(result)
    for msg in valid:
        print(msg['snippet'])
  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
