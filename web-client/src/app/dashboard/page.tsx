'use client';

import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    CarbonUsageForm,
    CarbonUsageFormData,
} from '@/components/CarbonUsageForm';
import {
    EmissionsBreakdownChart,
    EmissionsTrendChart,
    EmissionSource,
    MonthlyEmission,
} from '@/components/EmissionsCharts';
import { ImpactMetrics } from '@/components/ImpactMetrics';
import { calculateEmissions } from '@/lib/EmissionsCalculator';
import { useGetCalculations } from '@/hooks/useGetCalculations';
import React, { useEffect } from 'react';
import GlobeDemo from '@/components/dataglobe';

export default function Dashboard() {
    const { data: calculatedResponse, isLoading } = useGetCalculations();

    const [defaultValues, setDefaultValues] =
        React.useState<CarbonUsageFormData>({
            flightMiles: 0,
            foodDeliveryMiles: 0,
            rideShareMiles: 0,
            electricityUsage: 0,
            carMiles: 0,
        });

    const [emissionsData, setEmissionsData] = React.useState<{
        total: number;
        sources: EmissionSource[];
        historical: MonthlyEmission[];
    }>({
        total: 0,
        sources: [],
        historical: [],
    });

    useEffect(() => {
        if (calculatedResponse) {
            // Update default form values using the fetched data
            const newValues = {
                flightMiles:
                    (calculatedResponse.categories.flights?.distance ?? 0) / 12,
                foodDeliveryMiles:
                    (calculatedResponse.categories.uber_eats?.distance || 0) +
                    (calculatedResponse.categories.doordash?.distance || 0),
                rideShareMiles:
                    (calculatedResponse.categories.uber_rides?.distance || 0) +
                    (calculatedResponse.categories.lyft?.distance || 0),
                electricityUsage: 0,
                carMiles: 0,
            };
            setDefaultValues(newValues);

            // Calculate emissions based on the fetched data
            const calculatedData = calculateEmissions(newValues);
            setEmissionsData(calculatedData);
        }
    }, [calculatedResponse]);

    // Handle form submission and calculate emissions
    const handleFormSubmit = (formData: CarbonUsageFormData) => {
        const calculatedData = calculateEmissions(formData);
        setEmissionsData(calculatedData);
    };

    return (
        <div className="container mx-auto py-6 px-4">
            <h1 className="text-3xl font-bold mb-6">Your Carbon Dashboard</h1>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left column: Form */}
                <div className="lg:col-span-1">
                    {/* Pass defaultValues to the form */}
                    <CarbonUsageForm
                        onSubmit={handleFormSubmit}
                        defaultValues={defaultValues}
                        isLoading={isLoading}
                    />
                    {/* Impact metrics (visible on desktop) */}
                    <Card className="lg:flex items-center justify-center mt-6 bg-black border-0 lg:mt-12 h-[420px] w-[420px] gap-10">
                        <h1 className="text-center text-lg font-bold z-10">
                            Visualize Your Flight History
                        </h1>
                        <GlobeDemo />
                    </Card>
                </div>

                {/* Right column: Charts */}
                <div className="lg:col-span-2">
                    {/* Desktop view: Show both charts */}
                    <div className="hidden lg:grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
                        <EmissionsBreakdownChart data={emissionsData.sources} />
                        <div className=" hidden lg:block">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Environmental Impact</CardTitle>
                                    <CardDescription>
                                        The real-world impact of your carbon
                                        footprint
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <ImpactMetrics
                                        totalEmissions={emissionsData.total}
                                    />
                                </CardContent>
                            </Card>
                        </div>
                    </div>

                    <EmissionsTrendChart data={emissionsData.historical} />

                    {/* Mobile view: Tabs for charts */}
                    <div className="lg:hidden">
                        <Tabs defaultValue="breakdown" className="w-full">
                            <TabsList className="grid grid-cols-2">
                                <TabsTrigger value="breakdown">
                                    Breakdown
                                </TabsTrigger>
                                <TabsTrigger value="trend">Trend</TabsTrigger>
                            </TabsList>
                            <TabsContent value="breakdown" className="mt-4">
                                <EmissionsBreakdownChart
                                    data={emissionsData.sources}
                                />
                            </TabsContent>
                            <TabsContent value="trend" className="mt-4">
                                <EmissionsTrendChart
                                    data={emissionsData.historical}
                                />
                            </TabsContent>
                        </Tabs>
                    </div>

                    {/* Impact metrics (visible on mobile, below charts) */}
                    <div className="mt-6 lg:hidden">
                        <Card>
                            <CardHeader>
                                <CardTitle>Environmental Impact</CardTitle>
                                <CardDescription>
                                    The real-world impact of your carbon
                                    footprint
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <ImpactMetrics
                                    totalEmissions={emissionsData.total}
                                />
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
