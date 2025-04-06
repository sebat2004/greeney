'use client';

import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Legend,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';

// Types
export type EmissionSource = {
    name: string;
    value: number;
    color: string;
};

export type MonthlyEmission = {
    month: string;
    value: number;
};

interface EmissionsBreakdownProps {
    data: EmissionSource[];
}

interface EmissionsTrendProps {
    data: MonthlyEmission[];
}

// Color palette for charts
const COLORS = ['#047857', '#059669', '#10b981', '#34d399', '#6ee7b7'];

// Pie chart for emissions breakdown by source
export function EmissionsBreakdownChart({ data }: EmissionsBreakdownProps) {
    const total = data.reduce((sum, item) => sum + item.value, 0);

    return (
        <Card>
            <CardHeader>
                <CardTitle>Emissions Breakdown</CardTitle>
                <CardDescription>
                    Your carbon footprint by source (kg CO₂)
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                outerRadius={80}
                                innerRadius={40}
                                fill="#8884d8"
                                dataKey="value"
                                label={({ name, percent }) =>
                                    `${name} ${(percent * 100).toFixed(0)}%`
                                }
                            >
                                {data.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={
                                            entry.color ||
                                            COLORS[index % COLORS.length]
                                        }
                                    />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value: number) => [
                                    `${value.toFixed(1)} kg CO₂`,
                                    'Emissions',
                                ]}
                            />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
                <div className="mt-4 text-center">
                    <p className="text-sm text-muted-foreground">
                        Total Emissions
                    </p>
                    <p className="text-2xl font-bold">
                        {total.toFixed(1)} kg CO₂
                    </p>
                </div>
            </CardContent>
        </Card>
    );
}

// Bar chart for monthly emissions trends
export function EmissionsTrendChart({ data }: EmissionsTrendProps) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Monthly Emissions Trend</CardTitle>
                <CardDescription>
                    Your carbon footprint over time
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data}>
                            <CartesianGrid
                                strokeDasharray="3 3"
                                vertical={false}
                            />
                            <XAxis
                                dataKey="month"
                                tickLine={false}
                                axisLine={false}
                            />
                            <YAxis
                                tickLine={false}
                                axisLine={false}
                                tickFormatter={value => `${value} kg`}
                            />
                            <Tooltip
                                formatter={(value: number) => [
                                    `${value.toFixed(1)} kg CO₂`,
                                    'Emissions',
                                ]}
                            />
                            <Bar
                                dataKey="value"
                                fill="#10b981"
                                radius={[4, 4, 0, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
