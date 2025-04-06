import os
import logging
import json
import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
from quickstart import process_email_info
from calculator import calculate_emissions
from dotenv import load_dotenv

load_dotenv()

# Set up logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Log to stdout for console output
    ]
)
logger = logging.getLogger('carbon_emissions')

# Check for Google API key
if not os.getenv('GOOGLE_MAPS'):
    logger.warning("GOOGLE_API_KEY not found in environment variables. "
                 "Distance calculations for Uber Eats, DoorDash, and flights will not work correctly.")
    logger.warning("Set the API key with: export GOOGLE_API_KEY='your-api-key'")

# Create app with explicit template folder path
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)

# Create data directory for storing calculations
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(DATA_DIR, 'calculations_history.json')

def save_calculation(input_data, results):
    """Save calculation to history file"""
    logger.info("Saving calculation to history")
    
    # Create entry with timestamp
    entry = {
        'timestamp': datetime.now().isoformat(),
        'inputs': input_data,
        'results': results
    }
    
    # Load existing data or create new list
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Could not parse {HISTORY_FILE}, creating new history")
            history = []
    else:
        history = []
    
    # Add new entry and save
    history.append(entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    logger.info(f"Calculation saved. History now contains {len(history)} entries")
    return len(history)

CORS(app)  # Enable CORS for all routes

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for web interface (simplified for testing with single entries)"""
    result = None
    
    if request.method == 'POST':
        logger.info("Received form submission")
        try:
            # Check which form was submitted
            if 'uber_distance' in request.form:
                # Distance form submission
                input_data = {
                    'uber_rides': [{
                        'distance': float(request.form.get('uber_distance', 0)),
                        'time': request.form.get('uber_time', "0 minutes")
                    }],
                    'lyft': [{
                        'distance': float(request.form.get('lyft_distance', 0)),
                        'time': request.form.get('lyft_time', "0 minutes")  
                    }],
                    'uber_eats': [{
                        'distance': float(request.form.get('uber_eats_distance', 0))
                        # For direct distance testing, not using address/ordered_from
                    }],
                    'doordash': [{
                        'distance': float(request.form.get('doordash_distance', 0))
                        # For direct distance testing, not using address/ordered_from
                    }],
                    'flights': [{
                        'distance': float(request.form.get('flight_distance', 0))
                        # For direct distance testing, not using airport codes
                    }]
                }
            elif 'restaurant' in request.form:
                # Address form submission
                input_data = {
                    'uber_eats': [{
                        'restaurant': request.form.get('restaurant', ''),
                        'delivery_address': request.form.get('delivery_address', '')
                    }] if request.form.get('restaurant') else [],
                    'doordash': [{
                        'restaurant': request.form.get('doordash_restaurant', ''),
                        'delivery_address': request.form.get('doordash_address', '')
                    }] if request.form.get('doordash_restaurant') else [],
                    'flights': [{
                        'airport_a': request.form.get('airport_a', ''),
                        'airport_b': request.form.get('airport_b', '')
                    }] if request.form.get('airport_a') else []
                }
            else:
                # No recognized form fields
                return render_template('index.html', error="No form data recognized")
            
            logger.info(f"Input data: {json.dumps(input_data)}")
            
            # Calculate emissions
            results = calculate_emissions(input_data)
            
            # Log detailed results to console
            log_detailed_results(results)
            
            # Add input data to results for display
            results.update({
                'input_data': input_data
            })
            
            # Save calculation
            history_count = save_calculation(input_data, results)
            logger.info(f"Calculation #{history_count} completed and saved")
            
            result = results
            
        except Exception as e:
            logger.error(f"Error processing form data: {str(e)}", exc_info=True)
            return render_template('index.html', error=str(e))
    
    return render_template('index.html', result=result)


def log_detailed_results(results):
    """Log detailed calculation results to console"""
    logger.info("*** DETAILED CALCULATION RESULTS ***")
    logger.info(f"Total emissions: {results['total_emissions']:.2f} kg CO₂")
    
    # Log Uber rides details
    if 'uber_emissions' in results:
        logger.info(f"\nUber rides: {results['uber_distance']:.2f} miles → {results['uber_emissions']:.2f} kg CO₂")
        for i, ride in enumerate(results['entry_details']['uber_rides']):
            logger.info(f"  Ride {i+1}: {ride['distance']:.2f} miles → {ride['emissions']:.2f} kg CO₂")
    
    # Log Lyft rides details
    if 'lyft_emissions' in results:
        logger.info(f"\nLyft rides: {results['lyft_distance']:.2f} miles → {results['lyft_emissions']:.2f} kg CO₂")
        for i, ride in enumerate(results['entry_details']['lyft']):
            logger.info(f"  Ride {i+1}: {ride['distance']:.2f} miles → {ride['emissions']:.2f} kg CO₂")
    
    # Log Uber Eats delivery details
    if 'uber_eats_emissions' in results:
        logger.info(f"\nUber Eats: {results['uber_eats_distance']:.2f} miles → {results['uber_eats_emissions']:.2f} kg CO₂")
        for i, delivery in enumerate(results['entry_details']['uber_eats']):
            if 'origin' in delivery and 'destination' in delivery:
                logger.info(f"  Delivery {i+1}: {delivery['origin']} → {delivery['destination']}")
                # Check if 'duration' exists before accessing it
                duration_info = f", Duration: {delivery['duration']}" if 'duration' in delivery else ""
                logger.info(f"    Distance: {delivery['distance']:.2f} miles{duration_info}")
                logger.info(f"    Emissions: {delivery['emissions']:.2f} kg CO₂")
                if 'status' in delivery and delivery['status'] != 'OK':
                    logger.warning(f"    Status: {delivery['status']}")
                    if 'error' in delivery:
                        logger.warning(f"    Error: {delivery['error']}")
            else:
                logger.info(f"  Delivery {i+1}: {delivery['distance']:.2f} miles → {delivery['emissions']:.2f} kg CO₂")
    
    # Log Doordash delivery details
    if 'doordash_emissions' in results:
        logger.info(f"\nDoordash: {results['doordash_distance']:.2f} miles → {results['doordash_emissions']:.2f} kg CO₂")
        for i, delivery in enumerate(results['entry_details']['doordash']):
            if 'origin' in delivery and 'destination' in delivery:
                logger.info(f"  Delivery {i+1}: {delivery['origin']} → {delivery['destination']}")
                # Check if 'duration' exists before accessing it
                duration_info = f", Duration: {delivery['duration']}" if 'duration' in delivery else ""
                logger.info(f"    Distance: {delivery['distance']:.2f} miles{duration_info}")
                logger.info(f"    Emissions: {delivery['emissions']:.2f} kg CO₂")
                if 'status' in delivery and delivery['status'] != 'OK':
                    logger.warning(f"    Status: {delivery['status']}")
                    if 'error' in delivery:
                        logger.warning(f"    Error: {delivery['error']}")
            else:
                logger.info(f"  Delivery {i+1}: {delivery['distance']:.2f} miles → {delivery['emissions']:.2f} kg CO₂")
    
    # Log Flight details
    if 'flight_emissions' in results:
        logger.info(f"\nFlights: {results['flight_distance']:.2f} miles → {results['flight_emissions']:.2f} kg CO₂")
        for i, flight in enumerate(results['entry_details']['flights']):
            if 'airport_a' in flight and 'airport_b' in flight:
                if isinstance(flight['airport_a'], dict) and isinstance(flight['airport_b'], dict):
                    airport_a = flight['airport_a'].get('code', 'Unknown')
                    airport_b = flight['airport_b'].get('code', 'Unknown')
                    airport_a_address = flight['airport_a'].get('formatted_address', '')
                    airport_b_address = flight['airport_b'].get('formatted_address', '')
                    
                    logger.info(f"  Flight {i+1}: {airport_a} → {airport_b}")
                    if airport_a_address:
                        logger.info(f"    Airport A: {airport_a_address}")
                    if airport_b_address:
                        logger.info(f"    Airport B: {airport_b_address}")
                    logger.info(f"    Distance: {flight['distance']:.2f} miles")
                    logger.info(f"    Emissions: {flight['emissions']:.2f} kg CO₂")
                    if 'status' in flight and flight['status'] != 'OK':
                        logger.warning(f"    Status: {flight['status']}")
                        if 'error' in flight:
                            logger.warning(f"    Error: {flight['error']}")
                else:
                    logger.info(f"  Flight {i+1}: {flight['distance']:.2f} miles → {flight['emissions']:.2f} kg CO₂")
            else:
                logger.info(f"  Flight {i+1}: {flight['distance']:.2f} miles → {flight['emissions']:.2f} kg CO₂")
    
    logger.info(f"\nContext Metrics:")
    logger.info(f"  Trees needed: {results['trees_needed']}")
    logger.info(f"  London-NY flight comparison: {results['london_ny_percentage']:.2f}%")
    logger.info("****************************")

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """API endpoint for calculations with multiple entries and distance calculations"""
    logger.info("Received API calculation request")
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            logger.warning("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
        
        logger.info(f"API input data received with {len(data.keys())} categories")
        
        # Log the count of entries for each category
        for category in data:
            if isinstance(data[category], list):
                logger.info(f"  {category}: {len(data[category])} entries")
            else:
                logger.info(f"  {category}: 1 entry (not in list format)")
        
        # Calculate emissions
        results = calculate_emissions(data)
        
        # Log detailed results to console
        log_detailed_results(results)
        
        # Save calculation
        history_count = save_calculation(data, results)
        logger.info(f"API calculation #{history_count} completed and saved")
        
        # Return JSON response (without entry_details to keep response smaller)
        response_data = {k: v for k, v in results.items() if k != 'entry_details'}
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/calculate-emissions', methods=['POST'])
def calculateEmissions():
    """Calculate emissions based on Gmail data using provided auth token."""
    # Get auth token from request body
    if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
    
    data = request.json
    print(data)
    # Now use data.get() instead of request.json.get()
    auth_token = {
        "access_token": data.get('access_token'),  # Ensure you have the access token
        "client_id": data.get('client_id'),  # Optional: if needed for further processing
        "client_secret": data.get('client_secret')  # Optional: if needed for further processing
    }
    
    if not auth_token:
        return jsonify({"error": "Missing auth_token in request body"}), 400
    
    result = process_email_info(auth_token)
    
    # Return result as JSON array
    if isinstance(result, list):
        return jsonify({'emissions': result}), 200
    else:
        return jsonify({'error': 'Calculation failed', 'details': result}), 500


if __name__ == '__main__':
    app.run(debug=True, port=3001)
