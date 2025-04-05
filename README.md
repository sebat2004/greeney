*Objective: Answer question*
What is the carbon emission impact of my Uber, Doordash, Air flights.


comet - for visualzitaion
venv - for setting up virtual enviroment (or conda?)
flask - for running a server
python (3.9+) - for computation

potential dependencies?
    arrow
    click
    fief-client[cli]
    pandas
    prometheus_client
    psutil
    py-cpuinfo
    pynvml
    rapidfuzz
    requests
    questionary
    rich
    typer

key attributes:
- net power consumption (kwh)
- net carbon equivalent (kg. eq. CO2)
- miles driven (miles)

extra:
- carbon footprint (same as net carbon eq. carbon dioxide equivalent" (CO2e) measures the global warming potential of a mixture of greenhouse gases.)
- energy consumption (same as new power consumption)
- carbon sequestration (it's the amount of CO2 sequestered by a tree in a month)
- % of the flight from London to NY

**
C = Carbon Intensity of the electricity consumed for computation: quantified as g of CO₂ emitted per kilowatt-hour of electricity.

E = Energy Consumed by the computational infrastructure: quantified as kilowatt-hours.

Carbon dioxide emissions (CO₂eq) can then be calculated as C * E
**


Acknowledgments:

Lannelongue, L., Grealey, J., Inouye, M., Green Algorithms: Quantifying the Carbon Footprint of Computation. Adv. Sci. 2021, 2100707. https://doi.org/10.1002/advs.202100707