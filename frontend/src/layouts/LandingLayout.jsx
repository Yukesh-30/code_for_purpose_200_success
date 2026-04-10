import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { TrendingUp, LogIn } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { ThemeToggle } from '../components/ui/ThemeToggle';

export default function LandingLayout() {
  return (
    <div className="min-h-screen theme-gradient text-primary-text flex flex-col items-center overflow-x-hidden">
      <header className="w-full h-20 flex items-center justify-between px-8 max-w-7xl mx-auto border-b border-border/50">
        <div className="flex items-center gap-2 font-bold text-2xl text-gradient">
          <TrendingUp className="text-primary" size={32} />
          FlowSight AI
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
          <Link to="#features" className="text-muted-text hover:text-primary-text transition-colors">Features</Link>
          <Link to="#how-it-works" className="text-muted-text hover:text-primary-text transition-colors">How it works</Link>
          <Link to="#pricing" className="text-muted-text hover:text-primary-text transition-colors">Pricing</Link>
        </nav>
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Button variant="ghost" className="hidden sm:flex" asChild>
            <Link to="/login">Login</Link>
          </Button>
          <Button asChild>
            <Link to="/login">Get Started <LogIn size={16} className="ml-2" /></Link>
          </Button>
        </div>
      </header>

      <main className="flex-1 w-full relative">
        {/* Subtle background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/10 blur-[120px] rounded-full pointer-events-none" />
        <Outlet />
      </main>

      <footer className="w-full py-12 border-t border-border/50 mt-20">
        <div className="max-w-7xl mx-auto px-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-text">
          <div className="flex items-center gap-2 font-bold text-lg text-primary-text">
            <TrendingUp className="text-primary" size={24} />
            FlowSight AI
          </div>
          <p>&copy; {new Date().getFullYear()} FlowSight AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
