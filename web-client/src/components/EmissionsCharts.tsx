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
    CardFooter,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import {
    ChartConfig,
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
} from './ui/chart';
import { TrendingUp } from 'lucide-react';

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

const chartConfig = {} satisfies ChartConfig;

// Color palette for charts
const COLORS = ['#047857', '#059669', '#10b981', '#34d399', '#6ee7b7'];

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
                <ChartContainer config={chartConfig}>
                    <BarChart
                        data={data}
                        layout="vertical"
                        margin={{ left: 0, right: 20, top: 20, bottom: 20 }}
                    >
                        <YAxis
                            dataKey="name"
                            type="category"
                            tickLine={false}
                            tickMargin={1}
                            axisLine={false}
                            width={100}
                        />
                        <XAxis dataKey="value" type="number" hide />
                        <ChartTooltip
                            cursor={false}
                            content={<ChartTooltipContent hideLabel />}
                        />
                        <Bar dataKey="value" layout="vertical" radius={5}>
                            {data.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={entry.color}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ChartContainer>
            </CardContent>
            <CardFooter className="flex-col items-start gap-2 text-sm">
                <div className="flex gap-2 font-medium leading-none">
                    <TrendingUp className="h-4 w-4" />
                </div>
                <div className="leading-none text-muted-foreground">
                    Total Emissions: {total.toFixed(1)} kg CO₂
                </div>
            </CardFooter>
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
