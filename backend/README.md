*Objective: Answer question*
What is the carbon emission impact of my Uber, Doordash, Air flights.


- comet - for visualzitaion
- venv - for setting up virtual enviroment (or conda?)
- flask - for running a server
- python (3.9+) - for computation

# potential dependencies?
Flask>=2.0.0
Flask-WTF>=1.0.0
Werkzeug>=2.0.0
plotly>=5.3.1
pandas>=1.3.0
arrow>=1.2.0
click>=8.0.0
fief-client[cli]>=0.14.0
prometheus_client>=0.13.0
psutil>=5.9.0
py-cpuinfo>=8.0.0
pynvml>=11.4.1
rapidfuzz>=2.6.0
requests>=2.26.0
typer>=0.4.0
python-dotenv>=0.19.0
gunicorn>=20.1.0

# Setup for Virtual Enviroment
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install --upgrade pip`
- `pip install -r requirements.txt`
- `python app.py`

# How to kill virtual env:
- Exit the current environment deactivate
deactivate
- Remove the environment rm -rf ~/backend_env


# key attributes:
- net power consumption (kwh)
- net carbon equivalent (kg. eq. CO2)
- miles driven (miles)

# extra:
- carbon footprint (same as net carbon eq. carbon dioxide equivalent" (CO2e) measures the global warming potential of a mixture of greenhouse gases.)
- energy consumption (same as new power consumption)
- carbon sequestration (it's the amount of CO2 sequestered by a tree in a month)
- % of the flight from London to NY


C = Carbon Intensity of the electricity consumed for computation: quantified as g of CO₂ emitted per kilowatt-hour of electricity.

E = Energy Consumed by the computational infrastructure: quantified as kilowatt-hours.

Carbon dioxide emissions (CO₂eq) can then be calculated as C * E



# Acknowledgments:

Lannelongue, L., Grealey, J., Inouye, M., Green Algorithms: Quantifying the Carbon Footprint of Computation. Adv. Sci. 2021, 2100707. https://doi.org/10.1002/advs.202100707