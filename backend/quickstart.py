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
import re

def extract_uber_eats_info(email_text):
    """Extract restaurant name and delivery address from Uber Eats receipts"""
    # Extract restaurant name
    restaurant_pattern = r"You ordered from (.+?)(?:\n|$)"
    restaurant_match = re.search(restaurant_pattern, email_text, re.IGNORECASE)
    restaurant = restaurant_match.group(1).strip() if restaurant_match else None
    
    # Extract delivery address
    address_pattern = r"[Dd]elivered to\s*\n(.*?)(?:\n\n|\n\[|$)"
    address_match = re.search(address_pattern, email_text, re.DOTALL)
    address = address_match.group(1).strip() if address_match else None
    
    return {"restaurant": restaurant, "delivery_address": address}

def extract_doordash_info(email_text):
    """Extract restaurant name and delivery address from DoorDash receipts"""
    # Extract restaurant name
    restaurant_pattern = r"Order Confirmation for .+ from (.+?)(?:\n|$|To)"
    restaurant_match = re.search(restaurant_pattern, email_text, re.IGNORECASE)
    restaurant = restaurant_match.group(1).strip() if restaurant_match else None
    
    # Extract delivery address using complicated regex lol
    address_pattern = r"your receipt\s*\n\s*(.+?)(?:,\s*[a-z]{2}\s*\d{5}.*?)(?:\n\n|\n[a-z]|$)"
    address_match = re.search(address_pattern, email_text, re.IGNORECASE | re.DOTALL)
    address = address_match.group(1).strip() if address_match else None
    
    return {"restaurant": restaurant, "delivery_address": address}

def extract_uber_ride_info(email_text):
    """Extract uber rides start and end location using Uber Receipt"""
    subject_pattern = r"Subject: Your [A-Za-z]+ [A-Za-z]+ trip with Uber"

    if not re.search(subject_pattern, email_text, re.IGNORECASE):
        return (None, None)
    
    min_n_miles_pattern = r"[0-9]*\.[0-9]+ miles \| [0-9]+ min"
    min_n_miles_match = re.search(min_n_miles_pattern, email_text, re.IGNORECASE)
    if min_n_miles_match:
        split = min_n_miles_match.group(0).split()
        miles = split[0]
        mins = split[3]
        return {"type" : "Uber Ride", "distance": miles, "time": mins}
    return (None, None)

def extract_receipt_info(email_text):
    """Determine email type and extract relevant information"""
    # Check if Uber Eats receipt
    if "You ordered from" in email_text:
        return extract_uber_eats_info(email_text)
    # Check if DoorDash receipt
    elif "Order Confirmation for" in email_text and "doordash" in email_text:
        return extract_doordash_info(email_text)
    # Check if Uber ride receipt
    elif "ride with Uber" in email_text:
        return extract_uber_ride_info(email_text)
    else:
        return {"error": "Unknown receipt type"}

    

def simple_get_body(msg):
    """A simpler approach to get the email body, might not work for all emails"""
    payload = msg.get('payload', {})
    
    # First, try directly from payload.body
    body = payload.get('body', {})
    if 'data' in body:
        return base64.urlsafe_b64decode(body['data']).decode('utf-8')
    
    # If not found, check first part (common for simple emails)
    parts = payload.get('parts', [])
    if parts and 'body' in parts[0]:
        body_data = parts[0]['body'].get('data')
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode('utf-8')
    
    return "No body text found in expected locations"

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
        #print(f"\n--- Message ID: {msg['id']} ---")
        #print(f"Snippet: {msg['snippet']}")
        
        # Try the simplified approach
        body_text = simple_get_body(msg)
        info = extract_receipt_info(body_text)
        print(info) 
  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()

