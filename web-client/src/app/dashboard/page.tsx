'use client';

import { useState } from 'react';
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

export default function Dashboard() {
    // State to store emissions data
    const [emissionsData, setEmissionsData] = useState<{
        sources: EmissionSource[];
        total: number;
        historical: MonthlyEmission[];
    }>({
        sources: [{ name: 'No Data', value: 0, color: '#d1d5db' }],
        total: 0,
        historical: Array.from({ length: 6 }, (_, i) => ({
            month: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][i],
            value: 0,
        })),
    });

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
                    <CarbonUsageForm onSubmit={handleFormSubmit} />

                    {/* Impact metrics (visible on desktop) */}
                    <div className="mt-6 hidden lg:block">
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

                {/* Right column: Charts */}
                <div className="lg:col-span-2">
                    {/* Desktop view: Show both charts */}
                    <div className="hidden lg:grid grid-cols-1 xl:grid-cols-2 gap-6">
                        <EmissionsBreakdownChart data={emissionsData.sources} />
                        <EmissionsTrendChart data={emissionsData.historical} />
                    </div>

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
