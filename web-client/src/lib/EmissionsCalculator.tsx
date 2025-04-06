import { CarbonUsageFormData } from '@/components/CarbonUsageForm';
import { EmissionSource, MonthlyEmission } from '@/components/EmissionsCharts';

// Carbon emissions factors (kg CO2 per unit)
const EMISSIONS_FACTORS = {
    flight: 0.2, // kg CO2 per mile
    car: 0.4, // kg CO2 per mile
    foodDelivery: 3.5, // kg CO2 per delivery
    rideShare: 0.45, // kg CO2 per mile
    electricity: 0.5, // kg CO2 per kWh
};

const mockData: MonthlyEmission[] = [
    { month: 'Jun', value: 200 * 0.85 },
    { month: 'Jul', value: 200 * 0.92 },
    { month: 'Aug', value: 200 * 0.78 },
    { month: 'Sep', value: 200 * 0.95 },
    { month: 'Oct', value: 200 * 0.88 },
    { month: 'Nov', value: 100 },
];

// Calculate emissions from form data
export function calculateEmissions(formData: CarbonUsageFormData): {
    sources: EmissionSource[];
    total: number;
    historical: MonthlyEmission[];
} {
    // Calculate emissions for each source
    const flightEmissions =
        (formData.flightMiles || 0) * EMISSIONS_FACTORS.flight;
    const carEmissions = (formData.carMiles || 0) * EMISSIONS_FACTORS.car;
    const foodDeliveryEmissions =
        (formData.foodDelivery || 0) * EMISSIONS_FACTORS.foodDelivery;
    const rideShareEmissions =
        (formData.rideShareMiles || 0) * EMISSIONS_FACTORS.rideShare;
    const electricityEmissions =
        (formData.electricityUsage || 0) * EMISSIONS_FACTORS.electricity;

    // Create sources data for the breakdown chart
    const sources: EmissionSource[] = [
        { name: 'Air Travel', value: flightEmissions, color: '#047857' },
        { name: 'Car Travel', value: carEmissions, color: '#059669' },
        {
            name: 'Food Delivery',
            value: foodDeliveryEmissions,
            color: '#10b981',
        },
        { name: 'Ride Share', value: rideShareEmissions, color: '#34d399' },
        { name: 'Electricity', value: electricityEmissions, color: '#6ee7b7' },
    ].filter(source => source.value > 0); // Only include sources with emissions

    // If no sources have emissions, add a placeholder
    if (sources.length === 0) {
        sources.push({ name: 'No Emissions', value: 0, color: '#d1d5db' });
    }

    // Calculate total emissions
    const total = sources.reduce((sum, source) => sum + source.value, 0);

    return {
        sources,
        total,
        historical: mockData,
    };
}
