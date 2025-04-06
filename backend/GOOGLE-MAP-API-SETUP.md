# Setting Up Google Maps API for Distance Calculations

This guide explains how to set up the Google Maps API for the Carbon Emissions Calculator's distance calculation features.

## Why You Need a Google API Key

The Carbon Emissions Calculator uses Google's APIs for two types of calculations:

1. **Distance Matrix API**: Calculates driving distances between addresses (for Uber Eats and Doordash)
2. **Geocoding API**: Converts airport codes to geographic coordinates (for flights)

Without a valid API key, the calculator will only work with direct distance inputs.

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Make note of your project ID

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for and enable these APIs:
   - **Distance Matrix API**
   - **Geocoding API**

## Step 3: Create an API Key

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. A new API key will be created - copy this key
4. (Optional but recommended) Click "Restrict Key" to limit which APIs can use this key

## Step 4: Set Up API Key in Your Environment

Before running the Carbon Emissions Calculator, set the API key as an environment variable:

### For macOS/Linux:

```bash
export GOOGLE_API_KEY='your-api-key-here'
```

### For Windows Command Prompt:

```
set GOOGLE_API_KEY=your-api-key-here
```

### For Windows PowerShell:

```powershell
$env:GOOGLE_API_KEY = 'your-api-key-here'
```

## Step 5: Test the API Integration

Run the provided test script to verify that the API integration is working:

```bash
python google_api_test.py
```

The script will test both direct distance calculations and Google API-based calculations.

## Troubleshooting

If you see errors related to the Google API:

1. **"This API project is not authorized to use this API"**: Make sure you've enabled both the Distance Matrix API and Geocoding API in your Google Cloud project.

2. **"The provided API key is invalid"**: Double check that you've correctly set the GOOGLE_API_KEY environment variable with the exact key.

3. **"You have exceeded your daily request quota"**: The free tier of Google Maps APIs has usage limits. Consider enabling billing or optimizing your usage.

## API Usage Considerations

- Google Maps APIs have usage limits and may incur costs if you exceed the free tier
- Consider implementing caching for frequent address/airport lookups
- Monitor your API usage in the Google Cloud Console
