from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    
    if request.method == 'POST':
        # Just receive the data (no processing yet)
        uber_miles = float(request.form.get('uber_miles', 0))
        doordash_deliveries = int(request.form.get('doordash_deliveries', 0))
        flight_miles = float(request.form.get('flight_miles', 0))
        
        # Store the received data in a dictionary to confirm receipt
        result = {
            'uber_miles': uber_miles,
            'doordash_deliveries': doordash_deliveries,
            'flight_miles': flight_miles
        }
    
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)