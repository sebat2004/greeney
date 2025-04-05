"""
Carbon Emission Calculator Module

This module contains functions to calculate carbon emissions from various transportation activities:
- Uber rides
- Doordash deliveries
- Air flights

Each function follows the formula: Activity × Emission Factor = CO₂ Emissions
"""

def calculate_uber_emissions(miles):
    """
    Calculate carbon emissions from Uber rides.
    
    Args:
        miles (float): Total miles driven with Uber
        
    Returns:
        float: Carbon emissions in kg CO₂
    """
    # Emission factor: 0.4 kg CO₂ per mile
    return miles * 0.4

def calculate_doordash_emissions(deliveries):
    """
    Calculate carbon emissions from Doordash deliveries.
    
    Args:
        deliveries (int): Number of Doordash deliveries
        
    Returns:
        float: Carbon emissions in kg CO₂
    """
    # Assume average of 5 miles per delivery with emission factor of 0.4 kg CO₂ per mile
    return deliveries * 5 * 0.4

def calculate_flight_emissions(miles):
    """
    Calculate carbon emissions from flights.
    
    Args:
        miles (float): Total flight distance in miles
        
    Returns:
        float: Carbon emissions in kg CO₂
    """
    # Emission factor: 0.25 kg CO₂ per mile per passenger
    return miles * 0.25

def calculate_total_emissions(uber_miles, doordash_deliveries, flight_miles):
    """
    Calculate total carbon emissions from all activities.
    
    Args:
        uber_miles (float): Total miles driven with Uber
        doordash_deliveries (int): Number of Doordash deliveries
        flight_miles (float): Total flight distance in miles
        
    Returns:
        float: Total carbon emissions in kg CO₂
    """
    uber_emissions = calculate_uber_emissions(uber_miles)
    doordash_emissions = calculate_doordash_emissions(doordash_deliveries)
    flight_emissions = calculate_flight_emissions(flight_miles)
    
    return uber_emissions + doordash_emissions + flight_emissions

def calculate_trees_needed(total_emissions):
    """
    Calculate number of trees needed to offset emissions over a year.
    
    Args:
        total_emissions (float): Total carbon emissions in kg CO₂
        
    Returns:
        int: Number of trees needed
    """
    # One mature tree sequesters approximately 22 kg CO₂ per year
    trees = total_emissions / 22
    return round(trees)  # Round to nearest whole number of trees

def calculate_london_ny_comparison(total_emissions):
    """
    Calculate percentage of London-to-New-York flight emissions.
    
    Args:
        total_emissions (float): Total carbon emissions in kg CO₂
        
    Returns:
        float: Percentage of London-to-New-York flight emissions
    """
    # London to New York is approximately 3,500 miles
    # Emissions for this flight: 3,500 * 0.25 = 875 kg CO₂
    london_ny_emissions = 3500 * 0.25
    
    return (total_emissions / london_ny_emissions) * 100