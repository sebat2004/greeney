'use client';

import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card';
import { CircleIcon, TreePine, Droplets, CloudRain, Car } from 'lucide-react';

interface MetricCardProps {
    title: string;
    value: string | number;
    description: string;
    icon: React.ReactNode;
    className?: string;
}

function MetricCard({
    title,
    value,
    description,
    icon,
    className,
}: MetricCardProps) {
    return (
        <Card className={className}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
                {icon}
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{value}</div>
                <p className="text-xs text-muted-foreground">{description}</p>
            </CardContent>
        </Card>
    );
}

interface ImpactMetricsProps {
    totalEmissions: number; // in kg of CO2
}

export function ImpactMetrics({ totalEmissions }: ImpactMetricsProps) {
    // Calculate impact metrics
    // Average tree absorbs about 25kg CO2 per year
    const treesNeeded = Math.ceil(totalEmissions / 21); // overall absorption

    // Water footprint: ~1000 liters per kg of CO2
    const waterFootprint = Math.round(totalEmissions * ((36.0 + 46.0) / 2));

    // Driving equivalent: ~0.4 kg CO2 per mile
    const drivingEquivalent = Math.round(totalEmissions / 0.404);

    // Carbon offset cost: ~$10-15 per metric ton (1000kg) of CO2
    const offsetCost = Math.round((totalEmissions / 1000) * 12);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <MetricCard
                title="Trees Needed"
                value={treesNeeded}
                description="Trees required to offset monthly emissions"
                icon={<TreePine className="h-4 w-4 text-green-600" />}
            />

            <MetricCard
                title="Water Footprint"
                value={`${waterFootprint.toLocaleString()} L`}
                description="Water usage associated with your emissions"
                icon={<Droplets className="h-4 w-4 text-blue-500" />}
            />

            <MetricCard
                title="Driving Equivalent"
                value={`${drivingEquivalent} miles`}
                description="Equivalent miles driven in an average car"
                icon={<Car className="h-4 w-4 text-orange-500" />}
            />

            <MetricCard
                title="Offset Cost"
                value={`$${offsetCost}`}
                description="Estimated cost to offset your carbon footprint"
                icon={<CloudRain className="h-4 w-4 text-purple-500" />}
            />
        </div>
    );
}
