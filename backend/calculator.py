"""
Carbon Emission Calculator Module

This module calculates carbon emissions from various transportation activities:
- Uber rides
- Lyft rides
- Uber Eats deliveries
- Doordash deliveries
- Air flights

Some modes require Google API integration to calculate distances.
"""
import math
import os
import logging
from typing import List, Dict, Any, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()
# Initialize Google Maps client if API key is available
try:
    import googlemaps
    GOOGLE_API_KEY = os.getenv('GOOGLE_MAPS')
    if GOOGLE_API_KEY:
        gmaps = googlemaps.Client(key=GOOGLE_API_KEY)
    else:
        gmaps = None
        logging.warning("GOOGLE_API_KEY not found in environment variables. Distance calculations will not work.")
except ImportError:
    gmaps = None
    logging.warning("googlemaps library not installed. Please install with 'pip install googlemaps'")

# Emission factors
UBER_EMISSION_FACTOR = 0.4  # kg CO₂ per mile
LYFT_EMISSION_FACTOR = 0.4  # kg CO₂ per mile (same as Uber)
FOOD_DELIVERY_EMISSION_FACTOR = 0.4  # kg CO₂ per mile
FLIGHT_EMISSION_FACTOR = 0.25  # kg CO₂ per mile
TREE_SEQUESTRATION = 22  # kg CO₂ per tree per year
LONDON_NY_MILES = 3500  # miles

def calculate_uber_emissions(miles: float) -> float:

    return miles * UBER_EMISSION_FACTOR

def calculate_lyft_emissions(miles: float) -> float:
 
    return miles * LYFT_EMISSION_FACTOR

def calculate_food_delivery_emissions(miles: float) -> float:

    return miles * FOOD_DELIVERY_EMISSION_FACTOR

def calculate_flight_emissions(miles: float) -> float:

    return miles * FLIGHT_EMISSION_FACTOR

def geocode_airport(airport_code: str) -> Optional[Dict[str, Any]]:

    if not gmaps:
        logging.error("Google Maps client not initialized. Cannot geocode airport.")
        return None
    
    try:
        # Search for "<code> airport" to get more accurate results
        result = gmaps.geocode(f"{airport_code} airport")
        
        if result and len(result) > 0:
            # Extract coordinates from the first result
            location = result[0]['geometry']['location']
            formatted_address = result[0]['formatted_address']
            
            return {
                'lat': location['lat'],
                'lng': location['lng'],
                'formatted_address': formatted_address,
                'airport_code': airport_code,
                'status': 'OK'
            }
        else:
            logging.error(f"No results found for airport {airport_code}")
            return {
                'airport_code': airport_code,
                'status': 'NOT_FOUND',
                'error': f"No results found for airport {airport_code}"
            }
    except Exception as e:
        logging.error(f"Error geocoding airport {airport_code}: {str(e)}")
        return {
            'airport_code': airport_code,
            'status': 'ERROR',
            'error': str(e)
        }

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    # Convert coordinates from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    # Earth's radius in miles
    earth_radius = 3956  # miles
    
    # Calculate distance
    distance = earth_radius * c
    return distance

def calculate_flight_distance(airport_a: str, airport_b: str) -> Optional[Dict[str, Any]]:

    # Get coordinates for both airports
    airport_a_info = geocode_airport(airport_a)
    airport_b_info = geocode_airport(airport_b)
    
    if airport_a_info and airport_b_info and airport_a_info['status'] == 'OK' and airport_b_info['status'] == 'OK':
        # Calculate Haversine distance
        distance = haversine_distance(
            airport_a_info['lat'], airport_a_info['lng'],
            airport_b_info['lat'], airport_b_info['lng']
        )
        
        return {
            'distance_miles': distance,
            'airport_a': {
                'code': airport_a,
                'formatted_address': airport_a_info['formatted_address'],
                'lat': airport_a_info['lat'],
                'lng': airport_a_info['lng']
            },
            'airport_b': {
                'code': airport_b,
                'formatted_address': airport_b_info['formatted_address'],
                'lat': airport_b_info['lat'],
                'lng': airport_b_info['lng']
            },
            'status': 'OK'
        }
    else:
        errors = []
        if airport_a_info and airport_a_info['status'] != 'OK':
            errors.append(f"Airport A ({airport_a}): {airport_a_info.get('error', 'Unknown error')}")
        if airport_b_info and airport_b_info['status'] != 'OK':
            errors.append(f"Airport B ({airport_b}): {airport_b_info.get('error', 'Unknown error')}")
        if not airport_a_info:
            errors.append(f"Could not geocode Airport A ({airport_a})")
        if not airport_b_info:
            errors.append(f"Could not geocode Airport B ({airport_b})")
        
        error_message = "; ".join(errors)
        logging.error(f"Failed to calculate distance between {airport_a} and {airport_b}: {error_message}")
        
        return {
            'distance_miles': 0,
            'airport_a': {'code': airport_a},
            'airport_b': {'code': airport_b},
            'status': 'ERROR',
            'error': error_message
        }
    

def calculate_distance_between_addresses(origin, destination, client=None):

    if not client and gmaps:
        client = gmaps
        
    if not client:
        logging.error("Google Maps client not initialized. Cannot calculate distance.")
        return {
            'distance_miles': 0,
            'distance_exact': 0,
            'duration': 'unknown',
            'origin': origin,
            'destination': destination,
            'status': 'ERROR',
            'error': "Google Maps client not initialized."
        }
    
    try:
        # If this looks like a food delivery (origin might be a restaurant name),
        # use the specialized restaurant finder
        if len(origin.split(',')) == 1 and 'restaurant' in origin.lower():
            logging.info(f"Origin '{origin}' appears to be a restaurant name. Using restaurant finder.")
            return calculate_food_delivery_distance(origin, destination, client)
            
        # Standard distance calculation using Distance Matrix API
        result = client.distance_matrix(
            origins=[origin],
            destinations=[destination],
            mode="driving",
            units="imperial"  # Get results in miles
        )
        
        # Check if we got a valid result
        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            # Extract distance in miles
            distance_text = result['rows'][0]['elements'][0]['distance']['text']
            distance_value = result['rows'][0]['elements'][0]['distance']['value'] / 1609.34  # meters to miles
            
            # Extract duration
            duration_text = result['rows'][0]['elements'][0]['duration']['text']
            
            return {
                'distance_miles': float(distance_text.split()[0]),
                'distance_exact': distance_value,
                'duration': duration_text,
                'origin': origin,
                'destination': destination,
                'status': 'OK'
            }
        else:
            error_status = result['status'] if result['status'] != 'OK' else result['rows'][0]['elements'][0]['status']
            logging.error(f"Error calculating distance: {error_status}")
            return {
                'distance_miles': 0,
                'distance_exact': 0,
                'duration': 'unknown',
                'origin': origin,
                'destination': destination,
                'status': error_status,
                'error': f"Could not calculate distance: {error_status}"
            }
    except Exception as e:
        logging.error(f"Error in Google API call: {str(e)}")
        return {
            'distance_miles': 0,
            'distance_exact': 0,
            'duration': 'unknown',
            'origin': origin,
            'destination': destination,
            'status': 'ERROR',
            'error': str(e)
        }
    
def calculate_food_delivery_distance(restaurant, delivery_address, gmaps_client=None):

    import logging
    
    if not gmaps_client:
        logging.error("Google Maps client not initialized. Cannot calculate distance.")
        return {
            'distance_miles': 0,
            'distance_exact': 0,
            'duration': 'unknown',
            'origin': restaurant,
            'destination': delivery_address,
            'status': 'ERROR',
            'error': "Google Maps client not initialized."
        }
    
    try:
        # Step 1: Find the nearest restaurant location
        nearest_result = find_nearest_restaurant_location(restaurant, delivery_address, gmaps_client)
        
        if nearest_result['status'] != 'OK':
            # If we couldn't find a specific location, fall back to the original method
            # This preserves backward compatibility
            logging.warning(f"Could not find specific location for {restaurant}. Error: {nearest_result.get('error')}. Falling back to direct name search.")
            return calculate_distance_between_addresses(restaurant, delivery_address, gmaps_client)
        
        # Step 2: Use the specific restaurant address to calculate the driving distance
        restaurant_address = nearest_result['restaurant_address']
        
        logging.info(f"Found nearest {restaurant} location at {restaurant_address} to {delivery_address}")
        
        # Calculate driving distance using Distance Matrix API
        result = gmaps_client.distance_matrix(
            origins=[restaurant_address],
            destinations=[delivery_address],
            mode="driving",
            units="imperial"  # Get results in miles
        )
        
        # Check if we got a valid result
        if result['status'] == 'OK' and result['rows'][0]['elements'][0]['status'] == 'OK':
            # Extract distance in miles
            distance_text = result['rows'][0]['elements'][0]['distance']['text']
            distance_value = result['rows'][0]['elements'][0]['distance']['value'] / 1609.34  # meters to miles
            
            # Extract duration
            duration_text = result['rows'][0]['elements'][0]['duration']['text']
            
            return {
                'distance_miles': float(distance_text.split()[0]),
                'distance_exact': distance_value,
                'duration': duration_text,
                'origin': restaurant_address,  # Use the specific restaurant address
                'origin_name': restaurant,  # Keep original restaurant name for reference
                'destination': delivery_address,
                'status': 'OK',
                'nearest_restaurant_details': nearest_result  # Include details about the nearest location found
            }
        else:
            error_status = result['status'] if result['status'] != 'OK' else result['rows'][0]['elements'][0]['status']
            logging.error(f"Error calculating distance: {error_status}")
            return {
                'distance_miles': 0,
                'distance_exact': 0,
                'duration': 'unknown',
                'origin': restaurant_address,
                'origin_name': restaurant,
                'destination': delivery_address,
                'status': error_status,
                'error': f"Could not calculate distance: {error_status}",
                'nearest_restaurant_details': nearest_result
            }
    except Exception as e:
        logging.error(f"Error in food delivery distance calculation: {str(e)}")
        return {
            'distance_miles': 0,
            'distance_exact': 0,
            'duration': 'unknown',
            'origin': restaurant,
            'destination': delivery_address,
            'status': 'ERROR',
            'error': str(e)
        }

def find_nearest_restaurant_location(restaurant_name, delivery_address, gmaps_client=None):

    import logging
    
    if not gmaps_client:
        logging.error("Google Maps client not initialized. Cannot find nearest restaurant location.")
        return {
            'status': 'ERROR',
            'error': 'Google Maps client not initialized',
            'restaurant_name': restaurant_name,
            'delivery_address': delivery_address
        }
    
    try:
        # First geocode the delivery address to get its coordinates
        geocode_result = gmaps_client.geocode(delivery_address)
        if not geocode_result:
            logging.error(f"Could not geocode delivery address: {delivery_address}")
            return {
                'status': 'ERROR',
                'error': f"Could not geocode delivery address: {delivery_address}",
                'restaurant_name': restaurant_name,
                'delivery_address': delivery_address
            }
        
        delivery_location = geocode_result[0]['geometry']['location']
        delivery_lat = delivery_location['lat']
        delivery_lng = delivery_location['lng']
        
        # Generate name variations to try (primary logic for fixing "Burgerville USA" issue)
        name_variations = generate_name_variations(restaurant_name)
        logging.info(f"Trying with name variations: {name_variations}")
        
        # Define search radii to try (in meters), progressively larger
        # Starting with 14000m (~8.7 miles), then adding ~10 miles increments
        search_radii = [14000, 30000, 46000]  # ~8.7 miles, ~18.6 miles, ~28.6 miles
        
        # Stores all restaurant locations found across all attempts
        all_restaurant_locations = []
        
        # Try each name variation with each search radius until we find something
        for name_var in name_variations:
            for radius in search_radii:
                if all_restaurant_locations:
                    break  # Stop if we've already found locations
                
                logging.info(f"Searching for '{name_var}' within {radius/1609:.1f} miles of {delivery_address}")
                
                # Try Places Nearby API first (more specific to location)
                try:
                    places_result = gmaps_client.places_nearby(
                        location=(delivery_lat, delivery_lng),
                        radius=radius,
                        keyword=name_var,
                        # Removed type filter to get more results
                    )
                    
                    results = places_result.get('results', [])
                    if results:
                        logging.info(f"Found {len(results)} places for '{name_var}' within {radius/1609:.1f} miles")
                        all_restaurant_locations.extend(results)
                        break
                    else:
                        logging.info(f"No results from Places Nearby for '{name_var}' within {radius/1609:.1f} miles")
                except Exception as e:
                    logging.warning(f"Error in Places Nearby search: {str(e)}")
                
                # If Places Nearby failed, try Text Search (more flexible with names)
                if not all_restaurant_locations:
                    try:
                        places_result = gmaps_client.places(
                            query=f"{name_var} near {delivery_address}"
                        )
                        
                        results = places_result.get('results', [])
                        if results:
                            logging.info(f"Found {len(results)} places from text search for '{name_var}'")
                            all_restaurant_locations.extend(results)
                            break
                        else:
                            logging.info(f"No results from text search for '{name_var}'")
                    except Exception as e:
                        logging.warning(f"Error in text search: {str(e)}")
            
            if all_restaurant_locations:
                break  # Found locations with this name variation, no need to try others
        
        # If we still don't have results after trying all variations and radii
        if not all_restaurant_locations:
            logging.warning(f"No locations found for any variation of '{restaurant_name}' near {delivery_address}")
            return {
                'status': 'NOT_FOUND',
                'error': f"Restaurant '{restaurant_name}' could not be found. It might have closed or been removed from Google Maps.",
                'restaurant_name': restaurant_name,
                'delivery_address': delivery_address
            }
        
        # Find the closest restaurant using flexible name matching
        closest_restaurant = None
        closest_distance = float('inf')
        matched_name = None
        
        for location in all_restaurant_locations:
            location_name = location.get('name', '')
            
            # Skip locations with very low name similarity instead of strict matching
            name_similarity = calculate_name_similarity(restaurant_name, location_name)
            if name_similarity < 0.2:  # Threshold for minimum similarity
                logging.info(f"Skipping '{location_name}' - too dissimilar to '{restaurant_name}'")
                continue
                
            # Log what we're considering
            logging.info(f"Considering '{location_name}' as match for '{restaurant_name}'")
            
            restaurant_lat = location['geometry']['location']['lat']
            restaurant_lng = location['geometry']['location']['lng']
            
            # Calculate straight-line distance using the haversine formula
            import math
            
            # Convert coordinates from degrees to radians
            lat1_rad = math.radians(delivery_lat)
            lon1_rad = math.radians(delivery_lng)
            lat2_rad = math.radians(restaurant_lat)
            lon2_rad = math.radians(restaurant_lng)
            
            # Haversine formula
            dlon = lon2_rad - lon1_rad
            dlat = lat2_rad - lat1_rad
            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            # Earth's radius in miles
            earth_radius = 3958.8  # miles
            
            # Calculate distance
            distance = earth_radius * c
            
            logging.info(f"Location '{location_name}' is {distance:.2f} miles away")
            
            if distance < closest_distance:
                closest_distance = distance
                closest_restaurant = location
                matched_name = location_name
                logging.info(f"New closest: '{location_name}' at {distance:.2f} miles")
        
        if not closest_restaurant:
            logging.warning(f"No suitable location found for '{restaurant_name}' near '{delivery_address}'")
            return {
                'status': 'NOT_FOUND',
                'error': f"No suitable location matching '{restaurant_name}' found near '{delivery_address}'",
                'restaurant_name': restaurant_name,
                'delivery_address': delivery_address
            }
        
        # Get the full address of the closest restaurant
        place_details = gmaps_client.place(
            place_id=closest_restaurant['place_id'],
            fields=['name', 'formatted_address', 'geometry']
        )
        
        restaurant_details = place_details.get('result', {})
        restaurant_address = restaurant_details.get('formatted_address', 
                                                  closest_restaurant.get('vicinity', 'Unknown address'))
        
        logging.info(f"Selected restaurant: {matched_name} at {restaurant_address}")
        
        return {
            'status': 'OK',
            'restaurant_name': restaurant_name,
            'found_name': matched_name,  # Store the actual name found
            'restaurant_address': restaurant_address,
            'restaurant_place_id': closest_restaurant['place_id'],
            'restaurant_lat': closest_restaurant['geometry']['location']['lat'],
            'restaurant_lng': closest_restaurant['geometry']['location']['lng'],
            'delivery_address': delivery_address,
            'delivery_lat': delivery_lat,
            'delivery_lng': delivery_lng,
            'straight_line_distance': closest_distance  # in miles
        }
        
    except Exception as e:
        logging.error(f"Error finding nearest restaurant location: {str(e)}")
        return {
            'status': 'ERROR',
            'error': str(e),
            'restaurant_name': restaurant_name,
            'delivery_address': delivery_address
        }

def generate_name_variations(restaurant_name):

    variations = [restaurant_name]  # Always include the original name
    
    # Split the name into words
    words = restaurant_name.split()
    
    # Add just the first word if it's different from the original
    if len(words) > 1 and words[0] != restaurant_name:
        variations.append(words[0])
    
    # Add the first two words if there are at least 3 words
    if len(words) > 2:
        variations.append(f"{words[0]} {words[1]}")
    
    # If name ends with common suffixes like "USA", try without them
    common_suffixes = ['USA', 'Inc', 'Inc.', 'Restaurant', 'Restaurants']
    for suffix in common_suffixes:
        if restaurant_name.endswith(f" {suffix}"):
            variations.append(restaurant_name[:-len(suffix)-1])  # Remove suffix and space
    
    # Remove duplicates and return
    return list(dict.fromkeys(variations))  # Preserves order while removing duplicates

def calculate_name_similarity(name1, name2):
 
    # Convert to lowercase for comparison
    name1 = name1.lower()
    name2 = name2.lower()
    
    # Method 1: Check if one is a prefix of the other
    if name1.startswith(name2) or name2.startswith(name1):
        return 0.9  # Strong match if one is a prefix of the other
    
    # Method 2: Check if one contains the other
    if name1 in name2 or name2 in name1:
        return 0.8
    
    # Method 3: Check word overlap
    words1 = set(name1.split())
    words2 = set(name2.split())
    
    # Remove common filler words
    filler_words = {'the', 'and', 'of', 'a', 'an', '&'}
    words1 = words1 - filler_words
    words2 = words2 - filler_words
    
    if not words1 or not words2:
        return 0
    
    # Calculate Jaccard similarity (intersection over union)
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    jaccard = intersection / union if union > 0 else 0
    
    # Method 4: Check first word match (often the brand name)
    first_word_match = list(words1)[0] == list(words2)[0] if words1 and words2 else False
    
    # Calculate overall similarity score
    if first_word_match:
        similarity = max(jaccard, 0.7)  # First word match is important
    else:
        similarity = jaccard
    
    return similarity


def parse_time_string(time_str: str) -> int:

    if not isinstance(time_str, str):
        return 0
        
    time_str = time_str.lower()
    total_minutes = 0
    
    # Check for hours
    if "hour" in time_str:
        hour_parts = time_str.split("hour")[0].strip().split()
        if hour_parts:
            hours = int(hour_parts[-1])
            total_minutes += hours * 60
    
    # Check for minutes
    if "minute" in time_str:
        minute_parts = time_str.split("minute")[0].strip().split()
        if minute_parts:
            minutes = int(minute_parts[-1])
            total_minutes += minutes
    
    return total_minutes

# Update the food delivery processing in calculate_emissions function
def process_food_delivery(delivery, delivery_type="uber_eats"):
 
    if not delivery or 'error' in delivery:  # Skip empty or error entries
        return 0, {
            'distance': 0,
            'emissions': 0,
            'error': delivery.get('error', 'Empty delivery entry') if delivery else 'Empty delivery entry'
        }
            
    # Check if distance is directly provided
    if 'distance' in delivery:
        distance = delivery.get('distance', 0)
        detail = {
            'distance': distance,
            'emissions': calculate_food_delivery_emissions(distance),
            'direct_distance': True
        }
        return distance, detail
        
    # Check if restaurant and delivery_address are provided (new format)
    elif 'restaurant' in delivery and 'delivery_address' in delivery:
        distance_result = calculate_food_delivery_distance(
            delivery['restaurant'], 
            delivery['delivery_address'],
            gmaps
        )
        
        if distance_result and distance_result['status'] == 'OK':
            distance = distance_result['distance_exact']
            detail = {
                'distance': distance,
                'emissions': calculate_food_delivery_emissions(distance),
                'origin': distance_result.get('origin_name', delivery['restaurant']),
                'origin_address': distance_result.get('origin', delivery['restaurant']),
                'destination': delivery['delivery_address'],
                'duration': distance_result['duration'],
                'status': 'OK'
            }
            # Add restaurant details if available
            if 'nearest_restaurant_details' in distance_result:
                detail['restaurant_details'] = distance_result['nearest_restaurant_details']
                
            return distance, detail
        else:
            # Error in distance calculation
            distance = 0
            detail = {
                'distance': 0,
                'emissions': 0,
                'origin': delivery.get('restaurant', 'Unknown'),
                'destination': delivery.get('delivery_address', 'Unknown'),
                'status': distance_result['status'] if distance_result else 'ERROR',
                'error': distance_result.get('error', 'Unknown error') if distance_result else 'Failed to calculate distance'
            }
            return distance, detail
            
    # Otherwise check if address and ordered_from are provided (old format)
    elif 'address' in delivery and 'ordered_from' in delivery:
        # Use the same approach for the old format
        distance_result = calculate_food_delivery_distance(
            delivery['ordered_from'], 
            delivery['address'],
            gmaps
        )
        
        if distance_result and distance_result['status'] == 'OK':
            distance = distance_result['distance_exact']
            detail = {
                'distance': distance,
                'emissions': calculate_food_delivery_emissions(distance),
                'origin': distance_result.get('origin_name', delivery['ordered_from']),
                'origin_address': distance_result.get('origin', delivery['ordered_from']),
                'destination': delivery['address'],
                'duration': distance_result['duration'],
                'status': 'OK'
            }
            # Add restaurant details if available
            if 'nearest_restaurant_details' in distance_result:
                detail['restaurant_details'] = distance_result['nearest_restaurant_details']
                
            return distance, detail
        else:
            # Error in distance calculation
            distance = 0
            detail = {
                'distance': 0,
                'emissions': 0,
                'origin': delivery.get('ordered_from', 'Unknown'),
                'destination': delivery.get('address', 'Unknown'),
                'status': distance_result['status'] if distance_result else 'ERROR',
                'error': distance_result.get('error', 'Unknown error') if distance_result else 'Failed to calculate distance'
            }
            return distance, detail
    else:
        distance = 0
        detail = {
            'distance': 0,
            'emissions': 0,
            'error': 'No distance or address information provided'
        }
        return distance, detail

def calculate_emissions(data: Dict[str, Any]) -> Dict[str, Any]:
 
    # Initialize results dictionary
    results = {
        'entry_details': {
            'uber_rides': [],
            'lyft': [],
            'uber_eats': [],
            'doordash': [],
            'flights': []
        }
    }
    
    # Process Uber rides
    uber_total_distance = 0
    uber_total_emissions = 0
    if 'uber_rides' in data and data['uber_rides']:
        uber_rides = data['uber_rides'] if isinstance(data['uber_rides'], list) else [data['uber_rides']]
        for ride in uber_rides:
            if ride:  # Skip empty entries
                distance = ride.get('distance', 0)
                time = ride.get('time', '0 minutes')
                if isinstance(time, (int, float)):
                    time_minutes = int(time)
                else:
                    time_minutes = parse_time_string(time)
                
                emissions = calculate_uber_emissions(distance)
                uber_total_distance += distance
                uber_total_emissions += emissions
                
                # Add entry details
                results['entry_details']['uber_rides'].append({
                    'distance': distance,
                    'time_minutes': time_minutes,
                    'emissions': emissions
                })
        
        results['uber_distance'] = uber_total_distance
        results['uber_emissions'] = uber_total_emissions
    
    # Process Lyft rides
    lyft_total_distance = 0
    lyft_total_emissions = 0
    if 'lyft' in data and data['lyft']:
        lyft_rides = data['lyft'] if isinstance(data['lyft'], list) else [data['lyft']]
        for ride in lyft_rides:
            if ride:  # Skip empty entries
                distance = ride.get('distance', 0)
                time = ride.get('time', '0 minutes')
                if isinstance(time, (int, float)):
                    time_minutes = int(time)
                else:
                    time_minutes = parse_time_string(time)
                
                emissions = calculate_lyft_emissions(distance)
                lyft_total_distance += distance
                lyft_total_emissions += emissions
                
                # Add entry details
                results['entry_details']['lyft'].append({
                    'distance': distance,
                    'time_minutes': time_minutes,
                    'emissions': emissions
                })
        
        results['lyft_distance'] = lyft_total_distance
        results['lyft_emissions'] = lyft_total_emissions
    
    # Process Uber Eats deliveries
    uber_eats_total_distance = 0
    uber_eats_total_emissions = 0
    if 'uber_eats' in data and data['uber_eats']:
        uber_eats_deliveries = data['uber_eats'] if isinstance(data['uber_eats'], list) else [data['uber_eats']]
        for delivery in uber_eats_deliveries:
            distance, detail = process_food_delivery(delivery, "uber_eats")
            uber_eats_total_distance += distance
            uber_eats_total_emissions += detail['emissions']
            
            # Add entry details
            results['entry_details']['uber_eats'].append(detail)
        
        results['uber_eats_distance'] = uber_eats_total_distance
        results['uber_eats_emissions'] = uber_eats_total_emissions
    
    # Process Doordash deliveries
    doordash_total_distance = 0
    doordash_total_emissions = 0
    if 'doordash' in data and data['doordash']:
        doordash_deliveries = data['doordash'] if isinstance(data['doordash'], list) else [data['doordash']]
        for delivery in doordash_deliveries:
            distance, detail = process_food_delivery(delivery, "doordash")
            doordash_total_distance += distance
            doordash_total_emissions += detail['emissions']
            
            # Add entry details
            results['entry_details']['doordash'].append(detail)
        
        results['doordash_distance'] = doordash_total_distance
        results['doordash_emissions'] = doordash_total_emissions
    
    # Process flights
    flight_total_distance = 0
    flight_total_emissions = 0
    if 'flights' in data and data['flights']:
        flights = data['flights'] if isinstance(data['flights'], list) else [data['flights']]
        for flight in flights:
            if not flight:  # Skip empty entries
                continue
                
            # Check if distance is directly provided
            if 'distance' in flight:
                distance = flight.get('distance', 0)
                detail = {
                    'distance': distance,
                    'emissions': calculate_flight_emissions(distance),
                    'direct_distance': True
                }
            # Check if airport codes are provided
            elif 'airport_a' in flight and 'airport_b' in flight:
                distance_result = calculate_flight_distance(
                    flight['airport_a'], 
                    flight['airport_b']
                )
                
                if distance_result and distance_result['status'] == 'OK':
                    distance = distance_result['distance_miles']
                    detail = {
                        'distance': distance,
                        'emissions': calculate_flight_emissions(distance),
                        'airport_a': distance_result['airport_a'],
                        'airport_b': distance_result['airport_b'],
                        'status': 'OK'
                    }
                else:
                    # Error in distance calculation
                    distance = 0
                    detail = {
                        'distance': 0,
                        'emissions': 0,
                        'airport_a': {'code': flight.get('airport_a', 'Unknown')},
                        'airport_b': {'code': flight.get('airport_b', 'Unknown')},
                        'status': distance_result['status'] if distance_result else 'ERROR',
                        'error': distance_result.get('error', 'Unknown error') if distance_result else 'Failed to calculate distance'
                    }
            else:
                distance = 0
                detail = {
                    'distance': 0,
                    'emissions': 0,
                    'error': 'No distance or airport information provided'
                }
                
            flight_total_distance += distance
            flight_total_emissions += calculate_flight_emissions(distance)
            
            # Add entry details
            results['entry_details']['flights'].append(detail)
        
        results['flight_distance'] = flight_total_distance
        results['flight_emissions'] = flight_total_emissions
    
    # Calculate total emissions from all categories
    total_emissions = (
        uber_total_emissions + 
        lyft_total_emissions + 
        uber_eats_total_emissions + 
        doordash_total_emissions + 
        flight_total_emissions
    )
    results['total_emissions'] = total_emissions
    
    # Calculate additional context metrics
    results['trees_needed'] = calculate_trees_needed(total_emissions)
    results['london_ny_percentage'] = calculate_london_ny_comparison(total_emissions)
    
    return results

def calculate_trees_needed(total_emissions):

    # One mature tree sequesters approximately 22 kg CO₂ per year
    trees = total_emissions / TREE_SEQUESTRATION
    return round(trees)  # Round to nearest whole number of trees

def calculate_london_ny_comparison(total_emissions):

    # London to New York is approximately 3,500 miles
    # Emissions for this flight: 3,500 * 0.25 = 875 kg CO₂
    london_ny_emissions = LONDON_NY_MILES * FLIGHT_EMISSION_FACTOR
    
    return (total_emissions / london_ny_emissions) * 100
