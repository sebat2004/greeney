'use client';

import * as React from 'react';
import Link from 'next/link';
import { useTheme } from 'next-themes';
import { Home, BarChart, Info, LogIn, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { ModeToggle } from './ModeToggle';
import LoginButton from './login-button';
import { useSession } from 'next-auth/react';
import LogoutButton from './logout-button';

const Navbar: React.FC = () => {
    const { theme } = useTheme();
    const { data: session } = useSession();
    console.log(session);

    return (
        <nav className="w-full flex items-center justify-between px-6 py-4 border-b bg-background">
            {/* Logo */}
            <Link
                href="/"
                className="text-2xl font-bold text-green-600 dark:text-green-400"
            >
                Greeney
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex gap-6 items-center text-sm font-medium">
                <Link
                    href="/"
                    className="flex items-center gap-1 hover:text-green-600 transition"
                >
                    <Home className="w-4 h-4" />
                    Home
                </Link>
                <Link
                    href="/dashboard"
                    className="flex items-center gap-1 hover:text-green-600 transition"
                >
                    <BarChart className="w-4 h-4" />
                    Dashboard
                </Link>
                <Link
                    href="/about"
                    className="flex items-center gap-1 hover:text-green-600 transition"
                >
                    <Info className="w-4 h-4" />
                    About
                </Link>
            </div>

            {/* Right side: theme toggle + login (desktop only) */}
            <div className="hidden md:flex items-center gap-4">
                <ModeToggle />
                {session ? <LogoutButton /> : <LoginButton />}
            </div>

            {/* Mobile Drawer (visible only on small screens) */}
            <div className="md:hidden flex items-center gap-2">
                <ModeToggle />
                <Sheet>
                    <SheetTrigger asChild>
                        <Button variant="ghost" size="icon">
                            <Menu className="h-6 w-6" />
                        </Button>
                    </SheetTrigger>
                    <SheetContent side="right" className="w-64">
                        <div className="flex flex-col gap-4 mt-6 text-sm font-medium">
                            <Link
                                href="/"
                                className="flex items-center gap-2 hover:text-green-600"
                            >
                                <Home className="w-4 h-4" />
                                Home
                            </Link>
                            <Link
                                href="/dashboard"
                                className="flex items-center gap-2 hover:text-green-600"
                            >
                                <BarChart className="w-4 h-4" />
                                Dashboard
                            </Link>
                            <Link
                                href="/about"
                                className="flex items-center gap-2 hover:text-green-600"
                            >
                                <Info className="w-4 h-4" />
                                About
                            </Link>
                            <LoginButton />
                        </div>
                    </SheetContent>
                </Sheet>
            </div>
        </nav>
    );
};

export default Navbar;
