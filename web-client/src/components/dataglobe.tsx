// globe code
'use client';
import React from 'react';
import { motion } from 'motion/react';
import dynamic from 'next/dynamic';
import { useGetCalculations } from '@/hooks/useGetCalculations';
import { useEffect, useState } from 'react';

const World = dynamic(
    () => import('@/components/ui/globe').then(m => m.World),
    {
        ssr: false,
    },
);

export function GlobeDemo() {
    const globeConfig = {
        pointSize: 4,
        globeColor: '#062056',
        showAtmosphere: true,
        atmosphereColor: '#FFFFFF',
        atmosphereAltitude: 0.1,
        emissive: '#062056',
        emissiveIntensity: 0.1,
        shininess: 0.9,
        polygonColor: 'rgba(255,255,255,0.7)',
        ambientLight: '#38bdf8',
        directionalLeftLight: '#ffffff',
        directionalTopLight: '#ffffff',
        pointLight: '#ffffff',
        arcTime: 1000,
        arcLength: 0.9,
        rings: 1,
        maxRings: 3,
        initialPosition: { lat: 39.8283, lng: -98.5795 },
        autoRotate: true,
        autoRotateSpeed: 0.5,
    };

    const colors = ['#06b6d4', '#3b82f6', '#6366f1'];
    // example:
    //   {
    //     order: 1,
    //     startLat: -19.885592,
    //     startLng: -43.951191,
    //     endLat: -22.9068,
    //     endLng: -43.1729,
    //     arcAlt: 0.1,
    //     color: colors[Math.floor(Math.random() * (colors.length - 1))],
    //   }

    const { data: calculatedResponse, isLoading } = useGetCalculations();

    const generateArcs = () => {
        if (!calculatedResponse?.categories?.flights?.flights) return [];

        const arcs = [];
        let order = 1;

        calculatedResponse.categories.flights.flights.forEach(
            (flight, index) => {
                flight.segments.forEach(segment => {
                    arcs.push({
                        order: Math.floor(index / 4) + 1, // Increase order every 4th flight
                        startLat: segment.origin.latitude,
                        startLng: segment.origin.longitude,
                        endLat: segment.destination.latitude,
                        endLng: segment.destination.longitude,
                        arcAlt: 0.4,
                        color: colors[
                            Math.floor(Math.random() * colors.length)
                        ],
                    });
                });
            },
        );

        return arcs;
    };

    return (
        <div className="flex flex-col items-center justify-center absolute h-[400px] w-[400px] bg-white dark:bg-black">
            <div className="relative w-full aspect-square max-w-6xl">
                <motion.div
                    initial={{
                        opacity: 0,
                        y: 20,
                    }}
                    animate={{
                        opacity: 1,
                        y: 0,
                    }}
                    transition={{
                        duration: 1,
                    }}
                />
                <div className="absolute h-full w-full">
                    <World data={generateArcs()} globeConfig={globeConfig} />
                </div>
            </div>
        </div>
    );
}
export default GlobeDemo;
