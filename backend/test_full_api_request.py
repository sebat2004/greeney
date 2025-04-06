#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
# Check if Google API key is set
if not os.getenv('GOOGLE_MAPS'):
    print("WARNING: GOOGLE_MAPS environment variable is not set!")
    print("Airport and address distance calculations may not work correctly.")
    print("Set it with: export GOOGLE_MAPS='your-api-key-here'\n")

# API endpoint (use environment variable if available, otherwise default)
API_URL = os.getenv('API_URL', "http://127.0.0.1:3001/calculate-emissions")

# Sample Gmail auth token (this should be replaced with your actual token)
auth_token = {
    "access_token": "your_access_token_here",
    "client_id": "your_client_id_here",
    "client_secret": "your_client_secret_here"
}

# Test data for direct API testing
test_data = {
    "flights": [
        {
            "segments": [
                {"origin": "PDX", "destination": "LAX"}  # Portland to Los Angeles
            ]
        },
        {
            "segments": [
                {"origin": "JFK", "destination": "LHR"}  # New York to London
            ]
        },
        # Multi-segment flight test
        {
            "segments": [
                {"origin": "PDX", "destination": "LAX"},
                {"origin": "LAX", "destination": "JFK"}
            ]
        }
    ]
}

def test_api_for_coordinates():
    """Test the API to check if coordinates are included in the response"""
    print("\n===== TESTING Flight Coordinates =====")
    try:
        # Make POST request to API (you could use either /calculate-emissions or /api/calculate)
        response = requests.post(
            os.getenv('API_URL', "http://127.0.0.1:3001/api/calculate"),
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            result = response.json()
            
            # Check if flights key exists and has the expected structure
            if 'flight_emissions' in result and 'flight_distance' in result:
                print("Basic flight data present in response:")
                print(f"- Flight distance: {result['flight_distance']:.2f} miles")
                print(f"- Flight emissions: {result['flight_emissions']:.2f} kg CO₂")
            else:
                print("❌ ERROR: Basic flight data not found in response")
                print(json.dumps(result, indent=2))
                return False

            # Check for enhanced API response with flight coordinates
            flights_data = None
            
            # Check result format to locate flights data
            if 'categories' in result and 'flights' in result['categories']:
                # New format with categories
                if 'flights' in result['categories']['flights']:
                    flights_data = result['categories']['flights']['flights']
            elif 'entry_details' in result and 'flights' in result['entry_details']:
                # Old format with entry_details
                flights_data = result['entry_details']['flights']
            
            if not flights_data:
                print("❌ ERROR: Flight segments data not found in response")
                print(json.dumps(result, indent=2))
                return False
            
            # Validate coordinates in segments
            coordinates_found = False
            
            for flight in flights_data:
                if 'segments' in flight:
                    for segment in flight['segments']:
                        origin = segment.get('origin', {})
                        destination = segment.get('destination', {})
                        
                        # Check if coordinates are present
                        if isinstance(origin, dict) and 'latitude' in origin and 'longitude' in origin:
                            coordinates_found = True
                            print(f"\n✅ Coordinates found in response!")
                            print(f"Origin: {origin.get('code')} ({origin.get('latitude')}, {origin.get('longitude')})")
                            print(f"Destination: {destination.get('code')} ({destination.get('latitude')}, {destination.get('longitude')})")
                            break
                
                if coordinates_found:
                    break
            
            if not coordinates_found:
                print("❌ ERROR: No coordinates found in flight segments")
                print("Flight data structure:")
                print(json.dumps(flights_data, indent=2))
                return False
            
            print("\nFull Response JSON:")
            print(json.dumps(result, indent=2))
            
            print("\n✅ SUCCESS: Flight coordinates are correctly included in the API response.")
            return True
            
        else:
            print(f"❌ ERROR: Request failed with status code {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("Flight Coordinates API Test")
    test_api_for_coordinates()