import { cn } from "@/lib/utils";
import React from "react";

interface BackgroundProps {
    children: React.ReactNode;
    className?: string;
}


interface DotBackgroundProps {
    children: React.ReactNode;
    className?: string;
}

export function GridBackgroundDemo({ children, className }: DotBackgroundProps) {
    return (
        <div className={cn("relative w-full bg-white dark:bg-black", className)}>
            {/* Background grid - moved to lower z-index */}
            <div
                className={cn(
                    "absolute inset-0 z-0",
                    "[background-size:40px_40px]",
                    "[background-image:linear-gradient(to_right,#e4e4e7_1px,transparent_1px),linear-gradient(to_bottom,#e4e4e7_1px,transparent_1px)]",
                    "dark:[background-image:linear-gradient(to_right,#262626_1px,transparent_1px),linear-gradient(to_bottom,#262626_1px,transparent_1px)]",
                )}
            />
            {/* Radial gradient - also moved to lower z-index */}
            <div className="pointer-events-none absolute inset-0 z-0 flex items-center justify-center bg-white [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)] dark:bg-black" />

            {/* Content container - higher z-index */}
            <div className="relative z-10">
                {children}
            </div>
        </div>
    );
}

