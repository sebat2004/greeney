import { Spotlight } from '@/components/ui/spotlight-new';

export default function Home() {
    return (
        <div className="h-[80vh] w-full rounded-md flex md:items-center md:justify-center bg-black/[0.96] antialiased bg-grid-white/[0.02] relative overflow-hidden">
            <Spotlight />
            <div className=" p-4 max-w-7xl  mx-auto relative z-10  w-full pt-20 md:pt-0">
                <h1 className="text-4xl md:text-7xl font-bold text-center bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400 bg-opacity-50">
                    Welcome to <span className="text-green-400">Greeney</span>
                </h1>
                <p className="mt-4 font-normal text-base text-neutral-300 max-w-lg text-center mx-auto">
                    Greeney is your companion in tracking and reducing carbon
                    emissions.
                    <br />
                    Start your journey towards sustainability today!
                </p>
                <div className="mt-8 flex items-center justify-center">
                    <a
                        href="/dashboard"
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-semibold"
                    >
                        Get Started
                    </a>
                    <a
                        href="/about"
                        className="ml-4 px-4 py-2 bg-neutral-700 hover:bg-neutral-600 text-white rounded-md text-sm font-semibold"
                    >
                        Learn More
                    </a>
                </div>
            </div>
        </div>
    );
}
