'use client';
import { Spotlight } from '@/components/ui/spotlight-new';
import { motion, useAnimate, useInView } from 'motion/react';
import { useEffect } from 'react';

export default function Home() {
    const [scope, animate] = useAnimate();
    const isInView = useInView(scope);

    useEffect(() => {
        if (isInView) {
            animate(
                'span.typewriter-char',
                {
                    display: 'inline-block',
                    opacity: 1,
                },
                {
                    duration: 0.2,
                    delay: i => i * 0.1,
                    ease: 'easeInOut',
                },
            );
        }
    }, [isInView, animate]);

    // Add a space after "Welcome to"
    const welcomeText = 'Welcome to ';
    const greeneyText = 'Greeney';

    return (
        <div className="h-[95vh] w-full rounded-md flex md:items-center md:justify-center bg-black/[0.96] antialiased bg-grid-white/[0.02] relative overflow-hidden">
            <Spotlight />
            <div className="p-4 max-w-7xl mx-auto relative z-10 w-full pt-20 md:pt-0">
                <h1 className="text-4xl md:text-7xl font-bold text-center">
                    <span ref={scope} className="inline-block">
                        {/* Add whitespace: pre to preserve spaces */}
                        <span style={{ whiteSpace: 'pre' }}>
                            {welcomeText.split('').map((char, i) => (
                                <span
                                    key={`welcome-${i}`}
                                    className="typewriter-char opacity-0 hidden bg-clip-text text-transparent bg-gradient-to-b from-neutral-50 to-neutral-400"
                                >
                                    {char}
                                </span>
                            ))}
                        </span>
                        {greeneyText.split('').map((char, i) => (
                            <span
                                key={`greeney-${i}`}
                                className="typewriter-char opacity-0 hidden text-green-400"
                            >
                                {char}
                            </span>
                        ))}
                        <motion.span
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{
                                duration: 0.8,
                                repeat: Infinity,
                                repeatType: 'reverse',
                            }}
                            className="inline-block rounded-sm w-[4px] h-6 md:h-10 bg-green-400 ml-1"
                        ></motion.span>
                    </span>
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
