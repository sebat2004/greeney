import { useQuery } from '@tanstack/react-query';
interface CalculatedResponse {
    data: {
        categories: {
            doordash?: { distance: number; emissions: number };
            flights?: { distance: number; emissions: number };
            lyft?: { distance: number; emissions: number };
            uber_eats?: { distance: number; emissions: number };
            uber_rides?: { distance: number; emissions: number };
            [key: string]: { distance: number; emissions: number } | undefined;
        };
        context: {
            london_ny_percentage: number;
            trees_needed: number;
        };
        success: boolean;
        total_emissions: number;
    };
}
const getCalculations = async () => {
    try {
        const response = await fetch('/api/calculate-emissions', {
            method: 'GET',
        });

        const data: CalculatedResponse = await response.json();
        return data.data;
    } catch (error) {
        console.error('Error fetching email data:', error);
        throw error;
    }
};

export const useGetCalculations = () => {
    return useQuery({
        queryKey: ['calculations'],
        queryFn: getCalculations,
    });
};
