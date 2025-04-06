#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
# Check if Google API key is set
if not os.getenv('GOOGLE_MAPS'):
    print("WARNING: GOOGLE_API_KEY environment variable is not set!")
    print("Airport and address distance calculations may not work correctly.")
    print("Set it with: export GOOGLE_API_KEY='your-api-key-here'\n")

# API endpoint
API_URL = "http://127.0.0.1:5000/api/calculate"

# Sample data with multiple entries including airport codes and addresses
sample_data = {
    "uber_rides": [
        {"distance": 17.44, "time": "56 minutes"},
        {"distance": 5.2, "time": "15 minutes"}
    ],
    "lyft": [
        {"distance": 12.3, "time": "30 minutes"}
    ],
    "uber_eats": [
        # Direct distance entries
        {"distance": 5.8},
        {"distance": 3.7},
        # Address-based entries for Google API testing
        {
            "ordered_from": "Pike Place Market, Seattle, WA",
            "address": "Space Needle, Seattle, WA"
        },
        {
            "ordered_from": "Ferry Building, San Francisco, CA",
            "address": "Golden Gate Park, San Francisco, CA"
        }
    ],
    "doordash": [
        # Direct distance entries
        {"distance": 4.5},
        {"distance": 6.7},
        # Address-based entries for Google API testing
        {
            "ordered_from": "Times Square, New York, NY",
            "address": "Empire State Building, New York, NY"
        },
        {
            "ordered_from": "Faneuil Hall, Boston, MA",
            "address": "Harvard University, Cambridge, MA"
        }
    ],
    "flights": [
        # Direct distance entries
        {"distance": 1500.25},
        {"distance": 450.75},
        # Airport code entries for Google API testing
        {"airport_a": "PDX", "airport_b": "LAX"},  # Portland to Los Angeles
        {"airport_a": "JFK", "airport_b": "LHR"},  # New York to London
        {"airport_a": "SEA", "airport_b": "NRT"},  # Seattle to Tokyo
        {"airport_a": "SFO", "airport_b": "ORD"},  # San Francisco to Chicago
        {"airport_a": "MIA", "airport_b": "DFW"}   # Miami to Dallas
    ]
}

def test_api():
    """Test the API with sample data"""
    try:
        print("Sending request to API...")
        # Make POST request to API
        response = requests.post(
            API_URL,
            json=sample_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse JSON response
            result = response.json()
            
            # Print formatted results
            print("\n===== API TEST RESULTS =====")
            print(f"STATUS: Success (200 OK)")
            print(f"TOTAL EMISSIONS: {result['total_emissions']:.2f} kg CO₂")
            
            print("\nCategory Breakdown:")
            print(f"- Uber rides: {result['uber_distance']:.2f} miles → {result['uber_emissions']:.2f} kg CO₂")
            print(f"- Lyft: {result['lyft_distance']:.2f} miles → {result['lyft_emissions']:.2f} kg CO₂")
            print(f"- Uber Eats: {result['uber_eats_distance']:.2f} miles → {result['uber_eats_emissions']:.2f} kg CO₂")
            print(f"- Doordash: {result['doordash_distance']:.2f} miles → {result['doordash_emissions']:.2f} kg CO₂")
            print(f"- Flights: {result['flight_distance']:.2f} miles → {result['flight_emissions']:.2f} kg CO₂")
            
            print("\nContext Metrics:")
            print(f"- Trees needed: {result['trees_needed']}")
            print(f"- London-NY flight comparison: {result['london_ny_percentage']:.2f}%")
            
            print("\nFull Response:")
            print(json.dumps(result, indent=2))
            print("============================\n")
            
            # Check if Google API distances were calculated
            google_api_test = False
            
            # The flight distance should be much larger if airport codes were processed
            # PDX-LAX is ~834 miles, JFK-LHR is ~3400 miles, etc.
            expected_min_flight_distance = 1951.0 + 834.0  # Original direct distances + PDX-LAX minimum
            if result['flight_distance'] > expected_min_flight_distance:
                google_api_test = True
                print("✅ Google API SUCCESS: Flight distances were calculated using airport codes!")
                print(f"   Expected minimum: {expected_min_flight_distance:.2f} miles, Actual: {result['flight_distance']:.2f} miles")
            else:
                print("❌ Google API FAILURE: Flight distances using airport codes were not calculated.")
                print(f"   Expected minimum: {expected_min_flight_distance:.2f} miles, Actual: {result['flight_distance']:.2f} miles")
            
            # The food delivery distances should be larger if addresses were processed
            expected_min_food_distance = 9.5 + 11.2  # Original direct distances
            if (result['uber_eats_distance'] > 9.5 and result['doordash_distance'] > 11.2):
                google_api_test = True
                print("✅ Google API SUCCESS: Food delivery distances were calculated using addresses!")
                print(f"   Uber Eats expected minimum: 9.50 miles, Actual: {result['uber_eats_distance']:.2f} miles")
                print(f"   Doordash expected minimum: 11.20 miles, Actual: {result['doordash_distance']:.2f} miles")
            else:
                print("❌ Google API FAILURE: Food delivery distances using addresses were not calculated.")
                print(f"   Uber Eats expected minimum: 9.50 miles, Actual: {result['uber_eats_distance']:.2f} miles")
                print(f"   Doordash expected minimum: 11.20 miles, Actual: {result['doordash_distance']:.2f} miles")
            
            if google_api_test:
                print("\n🎉 Google Maps API integration is working correctly!\n")
            else:
                print("\n⚠️ Google Maps API integration may not be working correctly.")
                print("   Check that your API key is set and has access to Distance Matrix and Geocoding APIs.\n")
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Carbon Emissions Calculator API with Google Maps API integration...")
    print(f"Sending request to: {API_URL}")
    print(f"Sample data contains:")
    print(f"- {len(sample_data['uber_rides'])} Uber rides with direct distances")
    print(f"- {len(sample_data['lyft'])} Lyft rides with direct distances")
    
    # Count addresses vs direct distances
    uber_eats_addresses = sum(1 for item in sample_data['uber_eats'] if 'address' in item)
    uber_eats_direct = sum(1 for item in sample_data['uber_eats'] if 'distance' in item)
    print(f"- {len(sample_data['uber_eats'])} Uber Eats deliveries ({uber_eats_direct} with direct distances, {uber_eats_addresses} with addresses)")
    
    doordash_addresses = sum(1 for item in sample_data['doordash'] if 'address' in item)
    doordash_direct = sum(1 for item in sample_data['doordash'] if 'distance' in item)
    print(f"- {len(sample_data['doordash'])} Doordash deliveries ({doordash_direct} with direct distances, {doordash_addresses} with addresses)")
    
    flight_airports = sum(1 for item in sample_data['flights'] if 'airport_a' in item)
    flight_direct = sum(1 for item in sample_data['flights'] if 'distance' in item)
    print(f"- {len(sample_data['flights'])} Flights ({flight_direct} with direct distances, {flight_airports} with airport codes)")
    
    print("\nTesting airport codes: PDX, LAX, JFK, LHR, SEA, NRT, SFO, ORD, MIA, DFW")
    print("Testing landmark addresses in Seattle, San Francisco, New York, Boston")
    print()
    
    test_api()
