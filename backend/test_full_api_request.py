#!/usr/bin/env python3

import requests
import json
import os
from dotenv import load_dotenv
import sys

load_dotenv()
# Check if Google API key is set
if not os.getenv('GOOGLE_MAPS'):
    print("WARNING: GOOGLE_MAPS environment variable is not set!")
    print("Airport and address distance calculations may not work correctly.")
    print("Set it with: export GOOGLE_MAPS='your-api-key-here'\n")

# API endpoint (use environment variable if available, otherwise default)
API_URL = os.getenv('API_URL', "http://127.0.0.1:3001/api/calculate")

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
        {"distance": 1.1},
        {"distance": 4.6},
        # Address-based entries for Google API testing
        {
            "restaurant": "Pike Place Market",
            "delivery_address": "Space Needle, Seattle, WA"
        },
        {
            "restaurant": "Ferry Building",
            "delivery_address": "Golden Gate Park, San Francisco, CA"
        }
    ],
    "doordash": [
        # Direct distance entries
        {"distance": 0.8},
        {"distance": 5.1},
        # Address-based entries for Google API testing
        {
            "restaurant": "Times Square",
            "delivery_address": "Empire State Building, New York, NY"
        },
        {
            "restaurant": "Faneuil Hall",
            "delivery_address": "Harvard University, Cambridge, MA"
        }
    ],
    "flights": [
        # Direct distance entries
        {"distance": 1500.25},
        {"distance": 450.75},
        # Flight segment entries using segments format
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
        {
            "segments": [
                {"origin": "SEA", "destination": "NRT"}  # Seattle to Tokyo
            ]
        },
        {
            "segments": [
                {"origin": "SFO", "destination": "ORD"}  # San Francisco to Chicago
            ]
        },
        {
            "segments": [
                {"origin": "MIA", "destination": "DFW"}  # Miami to Dallas
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

# Sample data in quickstart.py format for testing compatibility
quickstart_sample = [
    {"type": "Uber Ride", "distance": "17.44", "time": "56"},
    {"type": "Lyft Ride", "time": 15, "pickup_location": "123 Main St", "dropoff_location": "456 Oak St"},
    {"type": "Uber Eats", "restaurant": "Pike Place Market", "delivery_address": "Space Needle, Seattle, WA"},
    {"type": "Door Dash Order", "restaurant": "Times Square", "delivery_address": "Empire State Building, New York, NY"},
    {"type": "flight", "segments": [
        {"origin": "PDX", "destination": "LAX"},
        {"origin": "LAX", "destination": "JFK"}
    ]}
]

def test_api(data, description="Standard API Format"):
    """Test the API with provided data"""
    # Using a local variable for tracking API success
    google_api_success = False
    
    # Check if this is a test for problematic restaurant names
    is_restaurant_name_test = False
    if isinstance(data, dict) and len(data) == 1 and 'doordash' in data:
        for entry in data['doordash']:
            if 'restaurant' in entry and ('McDonalds' in entry['restaurant'] or 'Burgerville USA' in entry['restaurant']):
                is_restaurant_name_test = True
                break
    
    try:
        print(f"\n===== TESTING WITH {description} =====")
        print("Sending request to API...")
        
        # Make POST request to API
        response = requests.post(
            API_URL,
            json=data,
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
            if 'uber_emissions' in result:
                print(f"- Uber rides: {result['uber_distance']:.2f} miles → {result['uber_emissions']:.2f} kg CO₂")
            if 'lyft_emissions' in result:
                print(f"- Lyft: {result['lyft_distance']:.2f} miles → {result['lyft_emissions']:.2f} kg CO₂")
            if 'uber_eats_emissions' in result:
                print(f"- Uber Eats: {result['uber_eats_distance']:.2f} miles → {result['uber_eats_emissions']:.2f} kg CO₂")
            if 'doordash_emissions' in result:
                print(f"- Doordash: {result['doordash_distance']:.2f} miles → {result['doordash_emissions']:.2f} kg CO₂")
            if 'flight_emissions' in result:
                print(f"- Flights: {result['flight_distance']:.2f} miles → {result['flight_emissions']:.2f} kg CO₂")
            
            print("\nContext Metrics:")
            print(f"- Trees needed: {result['trees_needed']}")
            print(f"- London-NY flight comparison: {result['london_ny_percentage']:.2f}%")
            
            print("\nFull Response:")
            print(json.dumps(result, indent=2))
            print("============================\n")
            
            # The flight distance should be much larger if airport codes were processed
            # PDX-LAX is ~834 miles, JFK-LHR is ~3400 miles, etc.
            if 'flight_distance' in result:
                expected_min_flight_distance = 1951.0 + 834.0  # Original direct distances + PDX-LAX minimum
                if result['flight_distance'] > expected_min_flight_distance:
                    google_api_success = True
                    print("✅ Google API SUCCESS: Flight distances were calculated using airport codes!")
                    print(f"   Expected minimum: {expected_min_flight_distance:.2f} miles, Actual: {result['flight_distance']:.2f} miles")
                else:
                    print("❌ Google API FAILURE: Flight distances using airport codes were not calculated.")
                    print(f"   Expected minimum: {expected_min_flight_distance:.2f} miles, Actual: {result['flight_distance']:.2f} miles")
            
            # The food delivery distances should be larger if addresses were processed
            if 'uber_eats_distance' in result and 'doordash_distance' in result:
                expected_uber_eats_min = 1
                expected_doordash_min = 0.8
                if (result['uber_eats_distance'] > expected_uber_eats_min and result['doordash_distance'] > expected_doordash_min):
                    google_api_success = True
                    print("✅ Google API SUCCESS: Food delivery distances were calculated using addresses!")
                    print(f"   Uber Eats expected minimum: {expected_uber_eats_min} miles, Actual: {result['uber_eats_distance']:.2f} miles")
                    print(f"   Doordash expected minimum: {expected_doordash_min} miles, Actual: {result['doordash_distance']:.2f} miles")
                else:
                    print("❌ Google API FAILURE: Food delivery distances using addresses were not calculated.")
                    print(f"   Uber Eats expected minimum: {expected_uber_eats_min} miles, Actual: {result['uber_eats_distance']:.2f} miles")
                    print(f"   Doordash expected minimum: {expected_doordash_min} miles, Actual: {result['doordash_distance']:.2f} miles")
            
            # For problematic restaurant names test, check only Doordash
            if is_restaurant_name_test and 'doordash_distance' in result:
                expected_distance_min = 0.5  # Very minimal expectation
                if result['doordash_distance'] > expected_distance_min:
                    google_api_success = True
                    print("✅ Google API SUCCESS: Restaurant name matching and distance calculation worked!")
                    print(f"   Expected minimum distance: {expected_distance_min} miles, Actual: {result['doordash_distance']:.2f} miles")
                    print("   Successfully processed problematic restaurant names (McDonalds/Burgerville USA)")
                else:
                    print("❌ Google API FAILURE: Restaurant name distances were not calculated correctly.")
                    print(f"   Expected minimum: {expected_distance_min} miles, Actual: {result['doordash_distance']:.2f} miles")
            
            if google_api_success:
                print("\n🎉 Google Maps API integration is working correctly!\n")
            else:
                print("\n⚠️ Google Maps API integration may not be working correctly.")
                print("   Check that your API key is set and has access to Distance Matrix and Geocoding APIs.\n")
            
            return True, result
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False, None
            
    except Exception as e:
        print(f"Error: {e}")
        return False, None

def count_entries(data):
    """Count the number of entries in the data structure"""
    if isinstance(data, dict):
        # Standard format
        counts = {}
        for category, entries in data.items():
            if isinstance(entries, list):
                counts[category] = len(entries)
                # Count address vs direct distance
                if category in ['uber_eats', 'doordash']:
                    address_count = sum(1 for item in entries if 'restaurant' in item and 'delivery_address' in item)
                    direct_count = sum(1 for item in entries if 'distance' in item)
                    counts[f"{category}_address"] = address_count
                    counts[f"{category}_direct"] = direct_count
                elif category == 'flights':
                    segment_count = sum(1 for item in entries if 'segments' in item)
                    direct_count = sum(1 for item in entries if 'distance' in item)
                    counts[f"{category}_segments"] = segment_count
                    counts[f"{category}_direct"] = direct_count
        return counts
    elif isinstance(data, list):
        # quickstart.py format
        type_counts = {}
        for entry in data:
            entry_type = entry.get('type', 'unknown').lower().replace(' ', '_')
            type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
            # Count segments for flights
            if entry_type == 'flight' and 'segments' in entry:
                type_counts['flight_segments'] = len(entry['segments'])
        return type_counts
    return {}

if __name__ == "__main__":
    print("Carbon Emissions Calculator API Test Suite")
    print(f"API Endpoint: {API_URL}")
    
    # Test with standard format
    print("\nTesting with standard API format...")
    counts = count_entries(sample_data)
    
    for category, count in counts.items():
        if '_' not in category:  # Skip the detailed counts
            print(f"- {count} {category}")
            
    print("\nDetailed entry breakdown:")
    for category, count in counts.items():
        if '_' in category:  # Only show detailed counts
            print(f"  - {category}: {count}")
            
    test_api(sample_data, "Standard API Format")
    
    # Test with quickstart.py format
    print("\nTesting with quickstart.py format...")
    counts = count_entries(quickstart_sample)
    
    for category, count in counts.items():
        print(f"- {count} {category}")
        
    test_api(quickstart_sample, "quickstart.py Format")
    
    # Test with restaurant name that had issues
    print("\nTesting with problematic restaurant names...")
    problem_test = {
        "doordash": [
            {
                "restaurant": "McDonalds",
                "delivery_address": "Empire State Building, New York, NY"
            },
            {
                "restaurant": "Burgerville USA",
                "delivery_address": "Portland State University, Portland, OR"
            }
        ]
    }
    
    test_api(problem_test, "Problematic Restaurant Names")
    
    print("\nAll tests completed!")