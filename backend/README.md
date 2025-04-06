# Carbon Emissions Flask API

A Flask-based API service that calculates carbon emissions from transportation activities, transforming data before sending it to the frontend.

## Setup and Running the Application

1. Create and activate virtual environment
```bash
python -m venv pyenv
source pyenv/bin/activate
```

2. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Configure Google Maps API key
```bash
echo "GOOGLE_MAPS=your_google_map_key" > .env
```
4. Running the Service
```bash
python app.py
```