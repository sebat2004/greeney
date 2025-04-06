_Objective: Answer question_
What is the carbon emission impact of my Uber, Doordash, Air flights.

A Flask-based API service that calculates carbon emissions from transportation activities. This service functions as a data processor between the scraping team and front end, handling multiple entries and integrating with Google APIs for distance calculations.

# Features

**Processes multiple entries for all transportation categories:**

- Uber rides
- Lyft rides
- Uber Eats deliveries
- Doordash deliveries
- Air flights

# Google API integration for distance calculations

- Distance Matrix API for road distances (Uber Eats, Doordash)
- Geocoding API for airport coordinates (flights)
- Haversine formula for flight distances

- Detailed console logging
- Simple web interface for testing
- RESTful API for integration with frontend
- Calculation history storage

- venv - for setting up virtual enviroment (or conda?)
- flask - for running a server
- python (3.9+) - for computation

# Packages

Flask==2.0.1
Werkzeug==2.0.1
Jinja2==3.0.1
itsdangerous==2.0.1
click==8.0.1
googlemaps==4.10.0
python-dotenv==0.19.0

# Setup for Virtual Enviroment

- `python -m venv pyenv`
- `cd pyenv`
- `source bin/activate` #activate env within backend dir
- `cd ..`
- `pip install --upgrade pip`
- `pip install -r requirements.txt`

# Set up .env file

- touch .env
- vim/nano .env
- Add this line: `GOOGLE_MAPS={your_google_map_key}`

# Run the flask backend

- `python app.py`

# How to kill virtual env

- Exit the current environment deactivate
  deactivate
- Remove the environment rm -rf ~/backend_env

# key attributes

- net power consumption (kwh)
- net carbon equivalent (kg. eq. CO2)
- miles driven (miles)

# extra

- carbon footprint (same as net carbon eq. carbon dioxide equivalent" (CO2e) measures the global warming potential of a mixture of greenhouse gases.)
- energy consumption (same as new power consumption)
- carbon sequestration (it's the amount of CO2 sequestered by a tree in a month)
- % of the flight from London to NY

C = Carbon Intensity of the electricity consumed for computation: quantified as g of CO₂ emitted per kilowatt-hour of electricity.

E = Energy Consumed by the computational infrastructure: quantified as kilowatt-hours.

Carbon dioxide emissions (CO₂eq) can then be calculated as C \* E

# Acknowledgments

Lannelongue, L., Grealey, J., Inouye, M., Green Algorithms: Quantifying the Carbon Footprint of Computation. Adv. Sci. 2021, 2100707. <https://doi.org/10.1002/advs.202100707>

