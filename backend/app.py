import os
import logging
import json
import sys
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
from quickstart import process_email_info
from calculator import calculate_emissions, process_quickstart_data
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
    logger.warning("GOOGLE_MAPS api key not found in environment variables. "
                 "Distance calculations for Uber Eats, DoorDash, and flights will not work correctly.")
    logger.warning("Set the API key with: creating .env file and putting in GOOGLE_MAPS = 'your-api-key'")

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
    """Main route for web interface with unified form for all transportation types"""
    result = None
    
    if request.method == 'POST':
        logger.info("Received form submission")
        try:
            # Initialize input data structure
            input_data = {
                'uber_rides': [],
                'lyft': [],
                'uber_eats': [],
                'doordash': [],
                'flights': []
            }
            
            # Process Uber ride inputs
            if request.form.get('uber_distance') and request.form.get('uber_time'):
                input_data['uber_rides'].append({
                    'distance': float(request.form.get('uber_distance', 0)),
                    'time': request.form.get('uber_time', "0")
                })
            
            # Process Lyft ride inputs
            if request.form.get('lyft_distance') and request.form.get('lyft_time'):
                input_data['lyft'].append({
                    'distance': float(request.form.get('lyft_distance', 0)),
                    'time': request.form.get('lyft_time', "0")
                })
            
            # Process Uber Eats inputs
            if request.form.get('restaurant') and request.form.get('delivery_address'):
                input_data['uber_eats'].append({
                    'restaurant': request.form.get('restaurant', ''),
                    'delivery_address': request.form.get('delivery_address', '')
                })
            
            # Process Doordash inputs
            if request.form.get('doordash_restaurant') and request.form.get('doordash_address'):
                input_data['doordash'].append({
                    'restaurant': request.form.get('doordash_restaurant', ''),
                    'delivery_address': request.form.get('doordash_address', '')
                })
            
            # Process Flight inputs - using segments format
            if request.form.get('airport_a') and request.form.get('airport_b'):
                input_data['flights'].append({
                    'segments': [
                        {
                            'origin': request.form.get('airport_a', ''),
                            'destination': request.form.get('airport_b', '')
                        }
                    ]
                })
            
            # Log basic input information
            logger.info(f"Processing form data with {sum(len(v) for v in input_data.values())} total entries")
            
            # Calculate emissions
            results = calculate_emissions(input_data)
            
            # Save calculation
            history_count = save_calculation(input_data, results)
            logger.info(f"Calculation #{history_count} completed")
            
            result = results
            
        except Exception as e:
            logger.error(f"Error processing form data: {str(e)}", exc_info=True)
            return render_template('index.html', error=str(e))
    
    return render_template('index.html', result=result)

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    """API endpoint for calculations with multiple entries"""
    logger.info("Received API calculation request")
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            logger.warning("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
        
        # Check if data is a list (quickstart.py format) or dictionary (standard format)
        if isinstance(data, list):
            logger.info(f"Processing API request with {len(data)} entries (quickstart.py format)")
            # Convert list to dictionary using process_quickstart_data
            data = process_quickstart_data(data)
        else:
            logger.info(f"Processing API request with {len(data.keys())} categories (standard format)")
        
        # Calculate emissions
        results = calculate_emissions(data)
        
        # Save calculation
        history_count = save_calculation(data, results)
        logger.info(f"API calculation #{history_count} completed")
        
        # Return JSON response (without entry_details to keep response smaller)
        response_data = {k: v for k, v in results.items() if k != 'entry_details'}
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.route('/calculate-emissions', methods=['POST'])
def calculate_emissions_from_gmail():
    """Calculate emissions based on Gmail data using provided auth token."""
    logger.info("Received request to calculate emissions from Gmail data")
    
    # Get auth token from request body
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    data = request.json
    # Extract auth token information
    auth_token = {
        "access_token": data.get('access_token'),
        "client_id": data.get('client_id'),
        "client_secret": data.get('client_secret')
    }
    
    if not auth_token.get('access_token'):
        return jsonify({"error": "Missing access_token in request body"}), 400
    
    try:
        # Process Gmail data
        email_data = process_email_info(auth_token)
        
        if not email_data or not isinstance(email_data, list):
            return jsonify({"error": "No valid transportation data found in emails"}), 404
        
        logger.info(f"Extracted {len(email_data)} transportation entries from Gmail")
        
        # Use process_quickstart_data to convert to standard format
        categorized_data = process_quickstart_data(email_data)
        
        # Log summary of categorized data
        for category, entries in categorized_data.items():
            if entries:
                logger.info(f"Found {len(entries)} {category} entries")
        
        # Calculate emissions
        if any(len(entries) > 0 for entries in categorized_data.values()):
            results = calculate_emissions(categorized_data)
            
            # Save calculation
            save_calculation(categorized_data, results)
            
            # Return results
            return jsonify({
                'success': True,
                'total_emissions': results.get('total_emissions', 0),
                'categories': {
                    'uber_rides': {
                        'distance': results.get('uber_distance', 0),
                        'emissions': results.get('uber_emissions', 0)
                    },
                    'lyft': {
                        'distance': results.get('lyft_distance', 0),
                        'emissions': results.get('lyft_emissions', 0)
                    },
                    'uber_eats': {
                        'distance': results.get('uber_eats_distance', 0),
                        'emissions': results.get('uber_eats_emissions', 0)
                    },
                    'doordash': {
                        'distance': results.get('doordash_distance', 0),
                        'emissions': results.get('doordash_emissions', 0)
                    },
                    'flights': {
                        'distance': results.get('flight_distance', 0),
                        'emissions': results.get('flight_emissions', 0)
                    }
                },
                'context': {
                    'trees_needed': results.get('trees_needed', 0),
                    'london_ny_percentage': results.get('london_ny_percentage', 0)
                }
            })
        else:
            return jsonify({"error": "No transportation data could be processed"}), 404
            
    except Exception as e:
        logger.error(f"Error processing Gmail data: {str(e)}", exc_info=True)
        return jsonify({'error': f"Failed to process Gmail data: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=3001)