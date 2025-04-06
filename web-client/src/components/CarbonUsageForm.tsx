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

const formSchema = z.object({
    flightMiles: z
        .number()
        .nonnegative('Flight miles cannot be negative')
        .optional(),
    carMiles: z.number().nonnegative('Car miles cannot be negative').optional(),
    foodDelivery: z
        .number()
        .nonnegative('Food delivery count cannot be negative')
        .optional(),
    rideShareMiles: z
        .number()
        .nonnegative('Ride share miles cannot be negative')
        .optional(),
    electricityUsage: z
        .number()
        .nonnegative('Electricity usage cannot be negative')
        .optional(),
});

export type CarbonUsageFormData = z.infer<typeof formSchema>;

interface CarbonUsageFormProps {
    onSubmit: (values: CarbonUsageFormData) => void;
    defaultValues?: Partial<CarbonUsageFormData>;
}

export function CarbonUsageForm({
    onSubmit,
    defaultValues,
}: CarbonUsageFormProps) {
    const form = useForm<CarbonUsageFormData>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            flightMiles: defaultValues?.flightMiles || 0,
            carMiles: defaultValues?.carMiles || 0,
            foodDelivery: defaultValues?.foodDelivery || 0,
            rideShareMiles: defaultValues?.rideShareMiles || 0,
            electricityUsage: defaultValues?.electricityUsage || 0,
        },
    });

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
            <CardHeader>
                <CardTitle>Track Your Carbon Footprint</CardTitle>
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
                                                max={5000}
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
                                                max={2000}
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
                            name="foodDelivery"
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
