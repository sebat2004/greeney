'use client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

export const Providers = ({
    children,
}: {
    children: React.ReactNode;
}): React.JSX.Element => {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                // Default settings for queries
                retry: 1, // Retry failed queries once
                staleTime: 60 * 1000, // 1 minutes
            },
        },
    });

    return (
        <QueryClientProvider client={queryClient}>
            {children}
        </QueryClientProvider>
    );
};
