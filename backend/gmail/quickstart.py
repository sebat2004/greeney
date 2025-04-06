import os.path
import base64
import json
import re
import quopri

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def extract_uber_eats_info(email_text):
    """Extract restaurant name and delivery address from Uber Eats receipts"""
    restaurant_pattern = r"You ordered from (.+?)(?:\n|$)"
    restaurant_match = re.search(restaurant_pattern, email_text, re.IGNORECASE)
    restaurant = restaurant_match.group(1).strip() if restaurant_match else None

    address_pattern = r"[Dd]elivered to\s*\n(.*?)(?:\n\n|\n\[|$)"
    address_match = re.search(address_pattern, email_text, re.DOTALL)
    address = address_match.group(1).strip() if address_match else None

    return {"restaurant": restaurant, "delivery_address": address}

def extract_doordash_info(email_text):
    """Extract restaurant name and delivery address from DoorDash receipts"""
    restaurant_pattern = r"Order Confirmation for .+ from (.+?)(?:\n|$|To)"
    restaurant_match = re.search(restaurant_pattern, email_text, re.IGNORECASE)
    restaurant = restaurant_match.group(1).strip() if restaurant_match else None

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

def extract_flight_info(email_text):
    """Extract flight information from airline confirmation emails"""
    flight_segments = []
    VALID_AIRPORTS = {
        'ATL', 'LAX', 'ORD', 'DFW', 'DEN', 'JFK', 'SFO', 'SEA', 'LAS', 'MCO',
        'MIA', 'PHX', 'EWR', 'IAH', 'BOS', 'MSP', 'DTW', 'PHL', 'LGA', 'CLT',
        'BWI', 'SLC', 'SAN', 'IAD', 'DCA', 'MDW', 'TPA', 'PDX', 'HOU', 'BNA',
        'AUS', 'STL', 'OAK', 'MCI', 'RDU', 'SJC', 'SMF', 'IND', 'CLE', 'PIT',
        'SAT', 'CVG', 'CMH', 'SNA', 'MKE', 'BDL', 'JAX', 'RSW', 'BUF', 'PVD',
        'OMA', 'CHS', 'MSY', 'TUL', 'ABQ', 'ALB', 'ROC', 'DAL', 'SDF', 'SYR',
        'GRR', 'BHM', 'PBI', 'ORF', 'BOI', 'OKC', 'RIC', 'LIT', 'ONT', 'MHT',
        'PSP', 'FLL', 'DAY', 'GSO', 'FAT', 'ELP', 'TUS', 'ICT', 'BUR', 'ISP',
        'LBB', 'COS', 'GEG', 'MSN', 'HSV', 'CID', 'CAE', 'PNS', 'DSM', 'SAV',
        'SBA', 'TYS', 'PWM', 'ECP', 'MYR', 'BZN', 'EUG', 'LGB', 'XNA', 'BTR',
    }

    valid_codes = []
    for code in re.findall(r'\b([A-Z]{3})\b', email_text):
        if code in VALID_AIRPORTS:
            valid_codes.append(code)

    for i in range(0, len(valid_codes) - 1):
        origin, destination = valid_codes[i], valid_codes[i+1]
        if origin != destination:
            segment = {"origin": origin, "destination": destination}
            if segment not in flight_segments:
                flight_segments.append(segment)

    return flight_segments

def extract_receipt_info(email_text):
    """Determine email type and extract relevant information"""
    if "You ordered from" in email_text:
        return extract_uber_eats_info(email_text)
    elif "Order Confirmation for" in email_text and "doordash" in email_text.lower():
        return extract_doordash_info(email_text)
    elif "ride with Uber" in email_text:
        return extract_uber_ride_info(email_text)
    elif "Flight" in email_text:
        return extract_flight_info(email_text)
    else:
        return {"error": "Unknown receipt type"}

def simple_get_body(msg):
    payload = msg.get('payload', {})
    body = payload.get('body', {})
    if 'data' in body:
        return base64.urlsafe_b64decode(body['data']).decode('utf-8')
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
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                data = part['body'].get('data')
                if data:
                    text = base64.urlsafe_b64decode(data).decode('utf-8')
                    return quopri.decodestring(text).decode('utf-8', errors='ignore')
    elif 'body' in payload:
        data = payload['body'].get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
    return None

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
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
            # print(snippet) 
            #poggers regex
            if re.search(r'doordash|uber receipt|confirmation|booking', snippet, re.IGNORECASE):
                valid.append(result)

        for msg in valid:
            body_text = simple_get_body(msg)
            info = extract_receipt_info(body_text)
            print(info)

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
