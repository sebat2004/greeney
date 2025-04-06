import React from 'react';
import greeney from '../../../public/greeneytransparent.png'

export default function About() {
    return (
        <div className="max-w-3xl mx-auto p-6 font-sans">
            <h1 className="text-4xl font-bold text-green-400 text-center mb-8">About Greeney</h1>
            <div className="flex justify-center mt-10">
                <img src={greeney.src} alt="Greeney" className="max-w-xs shadow-md rounded-lg" />
            </div>

            <div className="space-y-6 mb-8">
                <p className="text-lg text-neutral-300 leading-relaxed">
                    Greeney is the ultimate carbon emissions footprint tracker on the web. Greeney leverages various technologies to gather information and provide users with real data. Greeney shows emissions from various sources such as Flights, Uber Rides/Eats, Lyft Rides, and DoorDash Orders.
                </p>
                <p className="text-lg text-neutral-300 leading-relaxed">
                    Take our expert-made questionnaire, created by our cutting-edge researchers, paired with the data we gather for you to make an impact on this world by seeing where you can lower your emissions. Greeney allows you to see where you are falling short so you can take action and make the earth a tad greener.
                </p>
                <p className="text-lg text-neutral-300 leading-relaxed">
                    Greeney was created by four Oregon State University students for the largest and most competitive hackathon ever hosted in the state of Oregon. We leveraged cutting-edge technologies like Next.js, React, Flask, and APIs provided by Google. Check out our <a href="https://github.com/sebat2004/greeney" target="_blank" rel="noopener noreferrer" className="text-green-600 hover:text-green-800 hover:underline font-medium">GitHub page</a> for an insight into how Greeney works under the hood.
                </p>
            </div>
        </div>
    )
}

