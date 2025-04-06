'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { useEffect } from 'react';

import { Button } from '@/components/ui/button';
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader } from 'lucide-react';

const formSchema = z.object({
    foodDeliveryMiles: z
        .number()
        .min(0, 'Food delivery orders must be at least 0')
        .max(1000, 'Food delivery orders must be at most 1000'),
    flightMiles: z
        .number()
        .min(0, 'Flight miles must be at least 0')
        .max(100000, 'Flight miles must be at most 5000'), // Adjusted max for flights
    carMiles: z
        .number()
        .min(0, 'Car miles must be at least 0')
        .max(50000, 'Car miles must be at most 2000'), // Adjusted max for car miles
    rideShareMiles: z
        .number()
        .min(0, 'Ride share miles must be at least 0')
        .max(500, 'Ride share miles must be at most 500'), // Adjusted max for ride share
    electricityUsage: z
        .number()
        .min(0, 'Electricity usage must be at least 0')
        .max(1000, 'Electricity usage must be at most 1000'), // Adjusted max for electricity usage
});

export type CarbonUsageFormData = z.infer<typeof formSchema>;

interface CarbonUsageFormProps {
    onSubmit: (values: CarbonUsageFormData) => void;
    defaultValues?: Partial<CarbonUsageFormData>;
    isLoading: boolean; // Optional: to indicate loading state
}

export function CarbonUsageForm({
    onSubmit,
    defaultValues,
    isLoading,
}: CarbonUsageFormProps) {
    const form = useForm<CarbonUsageFormData>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            flightMiles: defaultValues?.flightMiles || 0,
            carMiles: defaultValues?.carMiles || 0,
            foodDeliveryMiles: defaultValues?.foodDeliveryMiles || 0,
            rideShareMiles: defaultValues?.rideShareMiles || 0,
            electricityUsage: defaultValues?.electricityUsage || 0,
        },
    });

    // Reset form values whenever defaultValues prop changes
    useEffect(() => {
        if (defaultValues) {
            form.reset({
                flightMiles: defaultValues.flightMiles || 0,
                carMiles: defaultValues.carMiles || 0,
                foodDeliveryMiles: defaultValues.foodDeliveryMiles || 0,
                rideShareMiles: defaultValues.rideShareMiles || 0,
                electricityUsage: defaultValues.electricityUsage || 0,
            });
        }
    }, [defaultValues, form]);

    // Effect to trigger initial calculation on component mount
    useEffect(() => {
        const initialValues = form.getValues();
        onSubmit(initialValues);
    }, []);

    function handleSubmit(values: CarbonUsageFormData) {
        onSubmit(values);
    }

    return (
        <Card className="w-full">
            <CardHeader className="flex gap-5">
                <CardTitle>Track Your Carbon Footprint</CardTitle>
                {isLoading ? (
                    // Show loader when isLoading is true
                    <Loader className="animate-spin text-gray-500" />
                ) : null}
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form
                        onSubmit={form.handleSubmit(handleSubmit)}
                        className="space-y-6"
                    >
                        <FormField
                            control={form.control}
                            name="flightMiles"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>
                                        Air Travel (miles/month)
                                    </FormLabel>
                                    <FormControl>
                                        <div className="flex items-center gap-4">
                                            <Slider
                                                min={0}
                                                max={20000}
                                                step={50}
                                                value={[field.value || 0]}
                                                onValueChange={value =>
                                                    field.onChange(value[0])
                                                }
                                                className="flex-1"
                                            />
                                            <Input
                                                type="number"
                                                className="w-20"
                                                value={field.value || 0}
                                                onChange={e =>
                                                    field.onChange(
                                                        Number(e.target.value),
                                                    )
                                                }
                                            />
                                        </div>
                                    </FormControl>
                                    <FormDescription>
                                        Average flight miles per month
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="carMiles"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>
                                        Car Travel (miles/month)
                                    </FormLabel>
                                    <FormControl>
                                        <div className="flex items-center gap-4">
                                            <Slider
                                                min={0}
                                                max={5000}
                                                step={10}
                                                value={[field.value || 0]}
                                                onValueChange={value =>
                                                    field.onChange(value[0])
                                                }
                                                className="flex-1"
                                            />
                                            <Input
                                                type="number"
                                                className="w-20"
                                                value={field.value || 0}
                                                onChange={e =>
                                                    field.onChange(
                                                        Number(e.target.value),
                                                    )
                                                }
                                            />
                                        </div>
                                    </FormControl>
                                    <FormDescription>
                                        Miles driven in personal vehicle
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="foodDeliveryMiles"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>
                                        Food Delivery (orders/month)
                                    </FormLabel>
                                    <FormControl>
                                        <div className="flex items-center gap-4">
                                            <Slider
                                                min={0}
                                                max={30}
                                                step={1}
                                                value={[field.value || 0]}
                                                onValueChange={value =>
                                                    field.onChange(value[0])
                                                }
                                                className="flex-1"
                                            />
                                            <Input
                                                type="number"
                                                className="w-20"
                                                value={field.value || 0}
                                                onChange={e =>
                                                    field.onChange(
                                                        Number(e.target.value),
                                                    )
                                                }
                                            />
                                        </div>
                                    </FormControl>
                                    <FormDescription>
                                        Number of food deliveries ordered
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="rideShareMiles"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>
                                        Ride Share (miles/month)
                                    </FormLabel>
                                    <FormControl>
                                        <div className="flex items-center gap-4">
                                            <Slider
                                                min={0}
                                                max={500}
                                                step={5}
                                                value={[field.value || 0]}
                                                onValueChange={value =>
                                                    field.onChange(value[0])
                                                }
                                                className="flex-1"
                                            />
                                            <Input
                                                type="number"
                                                className="w-20"
                                                value={field.value || 0}
                                                onChange={e =>
                                                    field.onChange(
                                                        Number(e.target.value),
                                                    )
                                                }
                                            />
                                        </div>
                                    </FormControl>
                                    <FormDescription>
                                        Miles traveled using ride sharing
                                        services
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="electricityUsage"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>
                                        Electricity Usage (kWh/month)
                                    </FormLabel>
                                    <FormControl>
                                        <div className="flex items-center gap-4">
                                            <Slider
                                                min={0}
                                                max={1000}
                                                step={10}
                                                value={[field.value || 0]}
                                                onValueChange={value =>
                                                    field.onChange(value[0])
                                                }
                                                className="flex-1"
                                            />
                                            <Input
                                                type="number"
                                                className="w-20"
                                                value={field.value || 0}
                                                onChange={e =>
                                                    field.onChange(
                                                        Number(e.target.value),
                                                    )
                                                }
                                            />
                                        </div>
                                    </FormControl>
                                    <FormDescription>
                                        Monthly household electricity
                                        consumption
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <Button type="submit" className="w-full">
                            Calculate Impact
                        </Button>
                    </form>
                </Form>
            </CardContent>
        </Card>
    );
}
