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
    
    return {"type":"Uber Eats" ,"restaurant": restaurant, "delivery_address": address}

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
    
    return {"type": "Door Dash Order","restaurant": restaurant, "delivery_address": address}

def extract_uber_ride_info(email_text):
    """Extract uber rides start and end location using Uber Receipt"""
    subject_pattern = r"Subject: Your [A-Za-z]+ [A-Za-z]+ trip with Uber"

    if not re.search(subject_pattern, email_text, re.IGNORECASE):
        return {} 
    
    min_n_miles_pattern = r"[0-9]*\.[0-9]+ miles \| [0-9]+ min"
    min_n_miles_match = re.search(min_n_miles_pattern, email_text, re.IGNORECASE)
    if min_n_miles_match:
        split = min_n_miles_match.group(0).split()
        miles = split[0]
        mins = split[3]
        return {"type" : "Uber Ride", "distance": miles, "time": mins}
    return {} 

def extract_lyft_ride_info(email_text):
    """Extract Lyft ride info start and end location using Lyft Receipt"""
    subject_pattern = r"lyft"

    if not re.search(subject_pattern, email_text, re.IGNORECASE):
        return {}
    
    # Updated pickup pattern
    pickup_pattern = r"Pickup\s+(\d+:\d+\s+[AP]M)\s+(.*?(?:, [A-Za-z]{2})?)\s*(?=Drop-off|$)"
    pickup_match = re.search(pickup_pattern, email_text, re.DOTALL)
    
    # Add drop-off pattern shoutout regex pattern
    dropoff_pattern = r"Drop-off\s+(\d+:\d+\s+[AP]M)\s+(.*?(?:, [A-Za-z]{2})?)(?=\s*(?:Ride for work|This and every ride|$))"
    dropoff_match = re.search(dropoff_pattern, email_text, re.DOTALL)
    
    result = {}
    
    if pickup_match and dropoff_match:
    # Extract pickup and dropoff information
        result['type'] = 'Lyft Ride'
        result['pickup_location'] = pickup_match.group(2).strip()
        result['dropoff_location'] = dropoff_match.group(2).strip()
        
        # Parse times to calculate duration
        pickup_time_str = pickup_match.group(1)
        dropoff_time_str = dropoff_match.group(1)
        
        # Convert time strings to datetime objects
        from datetime import datetime
        
        # Parse time strings (e.g., "3:57 PM")
        pickup_time = datetime.strptime(pickup_time_str, "%I:%M %p")
        dropoff_time = datetime.strptime(dropoff_time_str, "%I:%M %p")
        
        # Handle rides that cross midnight
        if dropoff_time < pickup_time:
            dropoff_time = dropoff_time.replace(day=pickup_time.day + 1)
        
        # Calculate the time difference in minutes
        time_diff = dropoff_time - pickup_time
        total_minutes = int(time_diff.total_seconds() / 60)
    
        result['time'] = total_minutes    
    return result


def extract_flight_info(email_text):
    """Extract flight information from airline confirmation emails"""
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
    
    flight_data = {"type": "flight", "segments": []}
    
    for i in range(0, len(valid_codes) - 1):
        origin, destination = valid_codes[i], valid_codes[i+1]
        if origin != destination:
            segment = {"origin": origin, "destination": destination}
            if segment not in flight_data["segments"]:
                flight_data["segments"].append(segment)
    
    return flight_data

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
    elif "lyft" in email_text:
        return extract_lyft_ride_info(email_text)
    elif "Flight" in email_text:
        return extract_flight_info(email_text)
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

def process_email_info(auth_token):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    try:
        creds = Credentials(
            token=auth_token.get('access_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=auth_token.get('client_id'),
            client_secret=auth_token.get('client_secret'),
            scopes=SCOPES
        )

        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me").execute()
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return
            
        receipt_data = []
        for message in messages:
            # see https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages#Message
            result = service.users().messages().get(userId="me",id=message['id']).execute()
            # stuff is already in json but this should make more sense
            snippet = result['snippet'].lower() 
            
            #poggers regex
            if re.search(r'doordash|uber receipt|lyft|confirmation|booking',snippet):
                body_text = simple_get_body(result)
                info = extract_receipt_info(body_text)
                
                if info == {} or "error" in info:
                    continue
                    
                date_match = re.search(r'date: (?:(?:mon|tue|wed|thu|fri|sat|sun), )?(.*?)(?= at)', snippet, re.IGNORECASE)
                if date_match:
                    info['date'] = date_match.group(1).strip()
                
                receipt_data.append(info)
        
        return receipt_data
        
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
