import { auth } from '@/lib/auth';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const session = await auth(); // Ensure the user is authenticated
    if (!session) {
        // If the user is not authenticated, return a 401 Unauthorized response
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // This route is intended to handle POST requests only
    if (request.method !== 'POST') {
        return NextResponse.json(
            { error: 'Method not allowed' },
            { status: 405 },
        );
    }

    try {
        const response = await fetch(
            'http://localhost:3001/calculate-emissions',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*', // Allow CORS for local testing, remove in production
                },
                body: JSON.stringify({
                    access_token: session.accessToken,
                    client_id: process.env.AUTH_GOOGLE_ID, // Pass the client_id if needed for the backend service
                    client_secret: process.env.AUTH_GOOGLE_SECRET, // Pass the client_secret if needed for the backend service
                }),
            },
        );

        if (!response.ok) {
            throw new Error(
                `Failed to calculate emissions: ${response.statusText}`,
            );
        }

        const data = await response.json();
        console.log('Data received from backend:', data);
        return NextResponse.json({ message: 'Data received', data });
    } catch (error) {
        return NextResponse.json({ error: 'Invalid JSON' }, { status: 401 });
    }
}
