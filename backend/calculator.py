"""
Currently calculaets for transportation activities:
- Uber rides
- Lyft rides
- Uber Eats deliveries
- Doordash deliveries
- Air flights
Uber Eats, Doordash and Air Flights require Google API integration to calculate distances.
"""
import math
import os
import logging
import re
from typing import List, Dict, Any, Tuple, Optional, Union
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
    """Calculate emissions from Uber ride given distance in miles"""
    return miles * UBER_EMISSION_FACTOR

def calculate_lyft_emissions(miles: float) -> float:
    """Calculate emissions from Lyft ride given distance in miles"""
    return miles * LYFT_EMISSION_FACTOR

def calculate_food_delivery_emissions(miles: float) -> float:
    """Calculate emissions from food delivery given distance in miles"""
    return miles * FOOD_DELIVERY_EMISSION_FACTOR

def calculate_flight_emissions(miles: float) -> float:
    """Calculate emissions from flight given distance in miles"""
    return miles * FLIGHT_EMISSION_FACTOR

def geocode_airport(airport_code: str) -> Optional[Dict[str, Any]]:
    """Geocode an airport by its IATA code"""
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
                'code': airport_code,
                'status': 'OK'
            }
        else:
            logging.error(f"No results found for airport {airport_code}")
            return {
                'code': airport_code,
                'status': 'NOT_FOUND',
                'error': f"No results found for airport {airport_code}"
            }
    except Exception as e:
        logging.error(f"Error geocoding airport {airport_code}: {str(e)}")
        return {
            'code': airport_code,
            'status': 'ERROR',
            'error': str(e)
        }

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula"""
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

def calculate_flight_distance(origin: str, destination: str) -> Optional[Dict[str, Any]]:
    """Calculate distance between two airports using Haversine formula"""
    # Get coordinates for both airports
    origin_info = geocode_airport(origin)
    destination_info = geocode_airport(destination)
    
    if origin_info and destination_info and origin_info['status'] == 'OK' and destination_info['status'] == 'OK':
        # Calculate Haversine distance
        distance = haversine_distance(
            origin_info['lat'], origin_info['lng'],
            destination_info['lat'], destination_info['lng']
        )
        
        return {
            'distance_miles': distance,
            'origin_info': origin_info,
            'destination_info': destination_info,
            'status': 'OK'
        }
    else:
        errors = []
        if origin_info and origin_info['status'] != 'OK':
            errors.append(f"Origin ({origin}): {origin_info.get('error', 'Unknown error')}")
        if destination_info and destination_info['status'] != 'OK':
            errors.append(f"Destination ({destination}): {destination_info.get('error', 'Unknown error')}")
        if not origin_info:
            errors.append(f"Could not geocode origin airport ({origin})")
        if not destination_info:
            errors.append(f"Could not geocode destination airport ({destination})")
        
        error_message = "; ".join(errors)
        logging.error(f"Failed to calculate distance between {origin} and {destination}: {error_message}")
        
        return {
            'distance_miles': 0,
            'origin_info': {'code': origin} if origin_info is None else origin_info,
            'destination_info': {'code': destination} if destination_info is None else destination_info,
            'status': 'ERROR',
            'error': error_message
        }

def calculate_distance_between_addresses(origin: str, destination: str, client=None) -> Dict[str, Any]:
    """Calculate driving distance between two addresses using Google Maps API"""
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
        if len(origin.split(',')) == 1 and 'restaurant' not in origin.lower():
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
    
def calculate_food_delivery_distance(restaurant: str, delivery_address: str, gmaps_client=None) -> Dict[str, Any]:
    """Calculate driving distance for food delivery between restaurant and delivery address"""
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
            # Don't fall back to direct name search, return an error instead to prevent infinite loops
            logging.warning(f"Could not find specific location for {restaurant}. Error: {nearest_result.get('error')}.")
            return {
                'distance_miles': 0,
                'distance_exact': 0,
                'duration': 'unknown',
                'origin': restaurant,
                'destination': delivery_address,
                'status': nearest_result['status'],
                'error': nearest_result.get('error', "Could not find restaurant location")
            }
        
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
            
            logging.info(f"Driving distance from {restaurant_address} to {delivery_address} is {distance_value:.2f} miles")
            
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

def find_nearest_restaurant_location(restaurant_name: str, delivery_address: str, gmaps_client=None) -> Dict[str, Any]:
    """Find the nearest location of a restaurant to a delivery address"""
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
            if name_similarity < 0.1:  # Lowered threshold from 0.2 to 0.1 for more flexible matching
                logging.info(f"Skipping '{location_name}' - too dissimilar to '{restaurant_name}' (similarity: {name_similarity:.2f})")
                continue
                
            # Log what we're considering
            logging.info(f"Considering '{location_name}' as match for '{restaurant_name}' (similarity: {name_similarity:.2f})")
            
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
            earth_radius = 3963  # miles According to https://en.wikipedia.org/wiki/Earth_radius
            
            # Calculate distance
            distance = earth_radius * c
            
            logging.info(f"Location '{location_name}' is {distance:.2f} miles away (straight-line distance)")
            
            if distance < closest_distance:
                closest_distance = distance
                closest_restaurant = location
                matched_name = location_name
                logging.info(f"New closest: '{location_name}' at {distance:.2f} miles (straight-line distance)")
        
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

def generate_name_variations(restaurant_name: str) -> List[str]:
    """Generate variations of a restaurant name to improve search accuracy"""
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

def calculate_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two restaurant names"""
    # Normalize names by removing punctuation and converting to lowercase
    name1 = re.sub(r'[^\w\s]', '', name1.lower())
    name2 = re.sub(r'[^\w\s]', '', name2.lower())
    
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

def parse_time_string(time_str: Union[str, int, float]) -> int:
    """Parse a time string to extract minutes"""
    # If already a number, return it as is
    if isinstance(time_str, (int, float)):
        return int(time_str)
    
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
    
    # If it's just a number without units, assume minutes
    if total_minutes == 0 and time_str.strip().isdigit():
        total_minutes = int(time_str.strip())
    
    return total_minutes

def process_food_delivery(delivery: Dict[str, Any], delivery_type: str="uber_eats") -> Tuple[float, Dict[str, Any]]:
    """Process food delivery data to calculate distance and emissions"""
    if not delivery or 'error' in delivery:  # Skip empty or error entries
        return 0, {
            'distance': 0,
            'emissions': 0,
            'error': delivery.get('error', 'Empty delivery entry') if delivery else 'Empty delivery entry'
        }
            
    # Check if distance is directly provided
    if 'distance' in delivery:
        distance = float(delivery.get('distance', 0))
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
    """Calculate emissions from various transportation activities"""
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
    
    # Check for direct entries via quickstart.py format (entries with 'type' field)
    if isinstance(data, list) and len(data) > 0 and 'type' in data[0]:
        # List of entries in quickstart.py format
        processed_data = process_quickstart_data(data)
        return calculate_emissions(processed_data)
    elif 'type' in data:
        # Single entry in quickstart.py format
        processed_data = process_quickstart_data([data])
        return calculate_emissions(processed_data)
    
    # Process Uber rides
    uber_total_distance = 0
    uber_total_emissions = 0
    if 'uber_rides' in data and data['uber_rides']:
        uber_rides = data['uber_rides'] if isinstance(data['uber_rides'], list) else [data['uber_rides']]
        for ride in uber_rides:
            if ride:  # Skip empty entries
                # Handle string or numeric distance
                distance = ride.get('distance', 0)
                if isinstance(distance, str):
                    try:
                        distance = float(distance)
                    except ValueError:
                        distance = 0
                
                time = ride.get('time', '0 minutes')
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
                # Check if distance is provided
                if 'distance' in ride:
                    distance = ride.get('distance', 0)
                    if isinstance(distance, str):
                        try:
                            distance = float(distance)
                        except ValueError:
                            distance = 0
                # If no distance but pickup/dropoff locations are available, calculate distance
                elif 'pickup_location' in ride and 'dropoff_location' in ride and gmaps:
                    try:
                        distance_result = calculate_distance_between_addresses(
                            ride['pickup_location'],
                            ride['dropoff_location'],
                            gmaps
                        )
                        if distance_result and distance_result['status'] == 'OK':
                            distance = distance_result['distance_exact']
                        else:
                            # If distance calculation failed, estimate based on time
                            time_minutes = parse_time_string(ride.get('time', 0))
                            # Assume average speed of 30 mph
                            distance = (time_minutes / 60) * 30
                    except Exception as e:
                        logging.error(f"Error calculating Lyft distance: {str(e)}")
                        # Estimate based on time
                        time_minutes = parse_time_string(ride.get('time', 0))
                        distance = (time_minutes / 60) * 30
                else:
                    # Estimate based on time if available
                    time_minutes = parse_time_string(ride.get('time', 0))
                    # Assume average speed of 30 mph
                    distance = (time_minutes / 60) * 30
                
                time_minutes = parse_time_string(ride.get('time', 0))
                
                emissions = calculate_lyft_emissions(distance)
                lyft_total_distance += distance
                lyft_total_emissions += emissions
                
                # Add entry details
                details = {
                    'distance': distance,
                    'time_minutes': time_minutes,
                    'emissions': emissions
                }
                
                # Add pickup/dropoff locations if available
                if 'pickup_location' in ride:
                    details['pickup_location'] = ride['pickup_location']
                if 'dropoff_location' in ride:
                    details['dropoff_location'] = ride['dropoff_location']
                
                results['entry_details']['lyft'].append(details)
        
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
    
    # Process flights - prioritizing segments format
    flight_total_distance = 0
    flight_total_emissions = 0
    if 'flights' in data and data['flights']:
        flights = data['flights'] if isinstance(data['flights'], list) else [data['flights']]
        for flight in flights:
            if not flight:  # Skip empty entries
                continue
                
            # Check if segments array is provided (primary format)
            if 'segments' in flight and isinstance(flight['segments'], list):
                total_segment_distance = 0
                segment_details = []
                
                for segment in flight['segments']:
                    if 'origin' in segment and 'destination' in segment:
                        distance_result = calculate_flight_distance(
                            segment['origin'],
                            segment['destination']
                        )
                        
                        if distance_result and distance_result['status'] == 'OK':
                            segment_distance = distance_result['distance_miles']
                            segment_detail = {
                                'distance': segment_distance,
                                'emissions': calculate_flight_emissions(segment_distance),
                                'origin': segment['origin'],
                                'destination': segment['destination'],
                                'origin_info': distance_result['origin_info'],
                                'destination_info': distance_result['destination_info'],
                                'status': 'OK'
                            }
                            logging.info(f"Flight segment {segment['origin']} to {segment['destination']}: {segment_distance:.2f} miles")
                        else:
                            # Error in distance calculation
                            segment_distance = 0
                            segment_detail = {
                                'distance': 0,
                                'emissions': 0,
                                'origin': segment.get('origin', 'Unknown'),
                                'destination': segment.get('destination', 'Unknown'),
                                'status': 'ERROR',
                                'error': distance_result.get('error', 'Failed to calculate distance') if distance_result else 'Failed to calculate distance'
                            }
                        
                        total_segment_distance += segment_distance
                        segment_details.append(segment_detail)
                
                distance = total_segment_distance
                detail = {
                    'distance': distance,
                    'emissions': calculate_flight_emissions(distance),
                    'segments': segment_details,
                    'segment_count': len(segment_details)
                }
                logging.info(f"Total flight distance across {len(segment_details)} segments: {distance:.2f} miles")
                
            # Check if legacy airport_a/airport_b format is provided (convert to segments format)
            elif 'airport_a' in flight and 'airport_b' in flight:
                # Convert to segments format
                origin = flight['airport_a']
                destination = flight['airport_b']
                
                distance_result = calculate_flight_distance(origin, destination)
                
                if distance_result and distance_result['status'] == 'OK':
                    distance = distance_result['distance_miles']
                    segment_detail = {
                        'distance': distance,
                        'emissions': calculate_flight_emissions(distance),
                        'origin': origin,
                        'destination': destination,
                        'origin_info': distance_result['origin_info'],
                        'destination_info': distance_result['destination_info'],
                        'status': 'OK'
                    }
                    
                    detail = {
                        'distance': distance,
                        'emissions': calculate_flight_emissions(distance),
                        'segments': [segment_detail],
                        'segment_count': 1
                    }
                    logging.info(f"Flight from {origin} to {destination}: {distance:.2f} miles")
                else:
                    # Error in distance calculation
                    distance = 0
                    detail = {
                        'distance': 0,
                        'emissions': 0,
                        'segments': [],
                        'segment_count': 0,
                        'status': distance_result['status'] if distance_result else 'ERROR',
                        'error': distance_result.get('error', 'Unknown error') if distance_result else 'Failed to calculate distance'
                    }
            # Check if distance is directly provided
            elif 'distance' in flight:
                distance = float(flight.get('distance', 0))
                detail = {
                    'distance': distance,
                    'emissions': calculate_flight_emissions(distance),
                    'direct_distance': True,
                    'segments': [],
                    'segment_count': 0
                }
            else:
                distance = 0
                detail = {
                    'distance': 0,
                    'emissions': 0,
                    'error': 'No distance or flight information provided',
                    'segments': [],
                    'segment_count': 0
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

def process_quickstart_data(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process data from quickstart.py format into calculator format"""
    # Initialize data structure
    processed_data = {
        'uber_rides': [],
        'lyft': [],
        'uber_eats': [],
        'doordash': [],
        'flights': []
    }
    
    for entry in entries:
        entry_type = entry.get('type', '').lower()
        
        if entry_type == 'uber ride':
            processed_data['uber_rides'].append({
                'distance': entry.get('distance', 0),
                'time': entry.get('time', 0)
            })
        elif entry_type == 'lyft ride':
            lyft_entry = {
                'time': entry.get('time', 0)
            }
            
            # Add optional fields if available
            if 'pickup_location' in entry:
                lyft_entry['pickup_location'] = entry['pickup_location']
            if 'dropoff_location' in entry:
                lyft_entry['dropoff_location'] = entry['dropoff_location']
            if 'distance' in entry:
                lyft_entry['distance'] = entry['distance']
                
            processed_data['lyft'].append(lyft_entry)
        elif entry_type == 'uber eats':
            processed_data['uber_eats'].append({
                'restaurant': entry.get('restaurant', ''),
                'delivery_address': entry.get('delivery_address', '')
            })
        elif entry_type == 'door dash order':
            processed_data['doordash'].append({
                'restaurant': entry.get('restaurant', ''),
                'delivery_address': entry.get('delivery_address', '')
            })
        elif entry_type == 'flight':
            # Pass through as is, maintaining segments format
            processed_data['flights'].append(entry)
    
    return processed_data

def process_flight_segments(flight_entry):
    """
    Process flight segments and extract detailed information including coordinates.
    """
    enhanced_flight = {
        'segments': [],
        'total_distance': flight_entry.get('distance', 0),
        'total_emissions': flight_entry.get('emissions', 0)
    }
    
    # Process segments if they exist
    if 'segments' in flight_entry and flight_entry['segments']:
        for segment in flight_entry['segments']:
            segment_detail = {
                'origin': {
                    'code': segment.get('origin', ''),
                },
                'destination': {
                    'code': segment.get('destination', ''),
                },
                'distance': segment.get('distance', 0),
                'emissions': segment.get('emissions', 0)
            }
            
            # Add coordinates if available
            if 'origin_info' in segment and segment['origin_info']:
                origin_info = segment['origin_info']
                if 'lat' in origin_info and 'lng' in origin_info:
                    segment_detail['origin']['latitude'] = origin_info['lat']
                    segment_detail['origin']['longitude'] = origin_info['lng']
            
            if 'destination_info' in segment and segment['destination_info']:
                dest_info = segment['destination_info']
                if 'lat' in dest_info and 'lng' in dest_info:
                    segment_detail['destination']['latitude'] = dest_info['lat']
                    segment_detail['destination']['longitude'] = dest_info['lng']
            
            enhanced_flight['segments'].append(segment_detail)
            
    # If no segments but has origin/destination info directly
    elif 'origin_info' in flight_entry and 'destination_info' in flight_entry:
        segment_detail = {
            'origin': {
                'code': flight_entry.get('origin', ''),
            },
            'destination': {
                'code': flight_entry.get('destination', ''),
            },
            'distance': flight_entry.get('distance', 0),
            'emissions': flight_entry.get('emissions', 0)
        }
        
        # Add coordinates
        origin_info = flight_entry['origin_info']
        dest_info = flight_entry['destination_info']
        
        if 'lat' in origin_info and 'lng' in origin_info:
            segment_detail['origin']['latitude'] = origin_info['lat']
            segment_detail['origin']['longitude'] = origin_info['lng']
            
        if 'lat' in dest_info and 'lng' in dest_info:
            segment_detail['destination']['latitude'] = dest_info['lat']
            segment_detail['destination']['longitude'] = dest_info['lng']
            
        enhanced_flight['segments'].append(segment_detail)
        
    return enhanced_flight

def calculate_trees_needed(total_emissions: float) -> int:
    """Calculate number of trees needed to offset emissions"""
    # One mature tree sequesters approximately 22 kg CO₂ per year
    trees = total_emissions / TREE_SEQUESTRATION
    return round(trees)  # Round to nearest whole number of trees

def calculate_london_ny_comparison(total_emissions: float) -> float:
    """Calculate emissions as percentage of London-NY flight"""
    # London to New York is approximately 3,500 miles
    # Emissions for this flight: 3,500 * 0.25 = 875 kg CO₂
    london_ny_emissions = LONDON_NY_MILES * FLIGHT_EMISSION_FACTOR
    
    return (total_emissions / london_ny_emissions) * 100