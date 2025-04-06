'use client';

import { EmissionsBarChart } from '@/components/EmissionsBarChart';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useEffect } from 'react';

export default function Dashboard() {
    useEffect(() => {
        fetch('/api/calculate-emissions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Emissions calculated:', data);
            })
            .catch(error => {
                console.error('Error calculating emissions:', error);
            });
    });

    return (
        <div className="flex flex-col xl:flex-row justify-between px-6 sm:px-10 py-5">
            {/* Charts Section */}
            <div className="w-full order-first md:order-last">
                {/* Desktop Version: Two-wide grid (shown on md and larger screens) */}
                <div className="hidden md:grid grid-cols-2 gap-6">
                    <EmissionsBarChart />
                    <EmissionsBarChart />
                </div>

                {/* Mobile Version: Tabs view (shown below md) */}
                <div className="block md:hidden">
                    <Tabs defaultValue="chart1" className="w-full">
                        <TabsList className="grid grid-cols-2">
                            <TabsTrigger value="chart1">Chart 1</TabsTrigger>
                            <TabsTrigger value="chart2">Chart 2</TabsTrigger>
                        </TabsList>
                        <TabsContent value="chart1" className="mt-4">
                            <EmissionsBarChart />
                        </TabsContent>
                        <TabsContent value="chart2" className="mt-4">
                            <EmissionsBarChart />
                        </TabsContent>
                    </Tabs>
                </div>
            </div>

            {/* Usage Form Section */}
            <section className="mt-8 w-[60%] order-last xl:order-first">
                <h2 className="text-xl font-semibold mb-2">Usage Form</h2>
                <p>This section would contain a form to submit usage data.</p>
            </section>
        </div>
    );
}
