#!/usr/bin/env python3
"""
Simple test script to verify if your Google Maps API key is working correctly.
This tests both the Distance Matrix API and the Geocoding API.
"""
import os
import sys

try:
    import googlemaps
except ImportError:
    print("Error: googlemaps library not installed.")
    print("Install it with: pip install googlemaps")
    sys.exit(1)

def test_api_key():
    """Test if the Google Maps API key is valid and has access to required APIs"""
    # Get API key from environment variable
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Set it with: export GOOGLE_API_KEY='your-api-key-here'")
        return False
    
    try:
        # Initialize Google Maps client
        print(f"Initializing Google Maps client with API key: {api_key[:6]}...{api_key[-4:]}")
        gmaps = googlemaps.Client(key=api_key)
        
        # Test Geocoding API with an airport code
        print("\nTesting Geocoding API with 'JFK airport'...")
        geocode_result = gmaps.geocode("JFK airport")
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            print(f"✅ Success! Got coordinates: {location['lat']}, {location['lng']}")
        else:
            print("❌ Failed to get geocoding results.")
            return False
        
        # Test Distance Matrix API with two addresses
        print("\nTesting Distance Matrix API with addresses...")
        distance_result = gmaps.distance_matrix(
            origins=["Times Square, New York, NY"],
            destinations=["Empire State Building, New York, NY"],
            mode="driving",
            units="imperial"
        )
        
        if (distance_result['status'] == 'OK' and 
            distance_result['rows'][0]['elements'][0]['status'] == 'OK'):
            distance = distance_result['rows'][0]['elements'][0]['distance']['text']
            duration = distance_result['rows'][0]['elements'][0]['duration']['text']
            print(f"✅ Success! Got distance: {distance}, duration: {duration}")
        else:
            print("❌ Failed to get distance matrix results.")
            return False
        
        print("\n🎉 Your Google Maps API key is working correctly!")
        print("It has access to both the Geocoding API and Distance Matrix API.")
        return True
        
    except Exception as e:
        print(f"❌ Error testing API key: {str(e)}")
        return False

if __name__ == "__main__":
    print("Google Maps API Key Verification Tool")
    test_api_key()