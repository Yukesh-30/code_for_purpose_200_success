import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, Play, CheckCircle2, TrendingUp, AlertTriangle, Briefcase, Zap } from 'lucide-react';
import { Button } from '../components/ui/Button';

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center w-full pb-20">
      
      {/* Hero Section */}
      <section className="w-full max-w-7xl mx-auto px-8 pt-24 pb-32 flex flex-col lg:flex-row items-center gap-12">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex-1 space-y-8"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
            <Zap size={16} />
            <span>AI-Powered Financial Intelligence</span>
          </div>
          
          <h1 className="text-5xl lg:text-7xl font-bold leading-tight">
            Predict Cash Flow Problems <br className="hidden lg:block"/>
            <span className="text-gradient">Before They Happen</span>
          </h1>
          
          <p className="text-xl text-muted-text max-w-2xl leading-relaxed">
            AI-powered forecasting, invoice risk prediction, and working capital intelligence for MSMEs and banks. 
            Take control of your financial future.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <Button size="lg" className="w-full sm:w-auto text-lg px-8 round-full" asChild>
              <Link to="/dashboard">Get Started <ArrowRight className="ml-2" size={20} /></Link>
            </Button>
            <Button size="lg" variant="outline" className="w-full sm:w-auto text-lg px-8 round-full">
              <Play className="mr-2 text-primary" size={20} /> Watch Demo
            </Button>
          </div>
          
          <div className="flex items-center gap-6 pt-4 text-sm text-secondary-text">
            <div className="flex items-center gap-2"><CheckCircle2 className="text-success" size={16} /> 99% Accuracy</div>
            <div className="flex items-center gap-2"><CheckCircle2 className="text-success" size={16} /> Bank Grade Security</div>
            <div className="flex items-center gap-2"><CheckCircle2 className="text-success" size={16} /> Easy Integration</div>
          </div>
        </motion.div>

        {/* Hero Visual */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="flex-1 w-full max-w-lg lg:max-w-none relative"
        >
          <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-secondary/20 blur-3xl rounded-full" />
          <div className="relative glass-panel rounded-2xl p-6 border border-border shadow-2xl">
            <div className="flex justify-between items-center mb-6">
              <div>
                <p className="text-sm text-muted-text">Forecasted Cash Gap</p>
                <h3 className="text-2xl font-bold text-danger">-$12,450.00</h3>
              </div>
              <div className="px-3 py-1 bg-danger/20 text-danger text-xs font-bold rounded-full">High Risk</div>
            </div>
            {/* Mock Chart Area */}
            <div className="h-48 w-full bg-secondary-background/50 rounded-xl border border-border relative overflow-hidden flex items-end px-4 gap-2 pb-4">
               {/* Just simple visual bars */}
               <div className="w-1/6 bg-success/80 h-[80%] rounded-t-md"></div>
               <div className="w-1/6 bg-success/60 h-[60%] rounded-t-md"></div>
               <div className="w-1/6 border-2 border-dashed border-primary h-[50%] rounded-t-md"></div>
               <div className="w-1/6 bg-danger/80 h-[30%] rounded-b-md transform translate-y-full"></div>
            </div>
            <div className="mt-6 flex space-x-3">
              <div className="flex-1 bg-secondary-background/50 p-3 rounded-lg border border-border">
                <p className="text-xs text-muted-text mb-1">Invoice Delay Risk</p>
                <p className="text-sm font-semibold">8 Invoices (Critical)</p>
              </div>
              <div className="flex-1 bg-secondary-background/50 p-3 rounded-lg border border-border">
                <p className="text-xs text-muted-text mb-1">AI Recommendation</p>
                <p className="text-sm font-semibold text-primary">Invoice Financing</p>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Trusted By */}
      <section className="w-full py-10 border-y border-border/50 bg-secondary-background/20">
        <div className="max-w-7xl mx-auto px-8 text-center">
          <p className="text-sm text-muted-text font-semibold tracking-wider uppercase mb-6">Trusted By Leading Banks & MSMEs</p>
          <div className="flex justify-center items-center gap-12 flex-wrap opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
            <span className="text-2xl font-bold font-serif whitespace-nowrap">Global Bank</span>
            <span className="text-2xl font-bold whitespace-nowrap tracking-tighter">FinTrust</span>
            <span className="text-2xl font-bold italic whitespace-nowrap">Nova Capital</span>
            <span className="text-2xl font-bold whitespace-nowrap uppercase tracking-widest">Nexus</span>
          </div>
        </div>
      </section>

      {/* Features Outline */}
      <section id="features" className="w-full max-w-7xl mx-auto px-8 py-32 space-y-32">
        
        {/* Feature 1 */}
        <div className="flex flex-col md:flex-row items-center gap-16">
          <div className="flex-1 glass-panel rounded-2xl h-80 w-full flex items-center justify-center p-8 relative overflow-hidden group">
            <div className="absolute inset-0 bg-primary/5 group-hover:bg-primary/10 transition-colors" />
            <TrendingUp size={120} className="text-primary opacity-20 transform group-hover:scale-110 transition-transform duration-700" />
          </div>
          <div className="flex-1 space-y-6">
            <h2 className="text-3xl font-bold">Unmatched Cash Flow Forecasting</h2>
            <p className="text-lg text-muted-text leading-relaxed">
              Our AI models analyze historical data, seasonality, and market trends to predict your liquidity position 30, 60, and 90 days out with absolute precision.
            </p>
            <ul className="space-y-3 text-secondary-text">
              <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-primary" /> Visual intuitive chart comparisons</li>
              <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-primary" /> Multi-scenario simulations</li>
              <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-primary" /> Confidence interval banding</li>
            </ul>
          </div>
        </div>

        {/* Feature 2 */}
        <div className="flex flex-col md:flex-row-reverse items-center gap-16">
          <div className="flex-1 glass-panel rounded-2xl h-80 w-full flex items-center justify-center p-8 relative overflow-hidden group">
            <div className="absolute inset-0 bg-danger/5 group-hover:bg-danger/10 transition-colors" />
            <AlertTriangle size={120} className="text-danger opacity-20 transform group-hover:scale-110 transition-transform duration-700" />
          </div>
          <div className="flex-1 space-y-6">
            <h2 className="text-3xl font-bold">Invoice Delay Heatmaps</h2>
            <p className="text-lg text-muted-text leading-relaxed">
              Stop guessing if you'll get paid on time. FlowSight evaluates customer payment histories and industry behaviors to assign probability scores to every outstanding invoice.
            </p>
            <Button variant="outline" className="mt-2">Explore Risk Modules</Button>
          </div>
        </div>

        {/* Feature 3 */}
        <div className="flex flex-col md:flex-row items-center gap-16">
          <div className="flex-1 glass-panel rounded-2xl h-80 w-full flex items-center justify-center p-8 relative overflow-hidden group">
            <div className="absolute inset-0 bg-success/5 group-hover:bg-success/10 transition-colors" />
            <Briefcase size={120} className="text-success opacity-20 transform group-hover:scale-110 transition-transform duration-700" />
          </div>
          <div className="flex-1 space-y-6">
            <h2 className="text-3xl font-bold">Smart Banking Recommendations</h2>
            <p className="text-lg text-muted-text leading-relaxed">
              When a cash gap is predicted, FlowSight autonomously matches your risk profile against available banking products and calculates your approval odds.
            </p>
            <Button variant="outline" className="mt-2">View Financial Products</Button>
          </div>
        </div>

      </section>

      {/* CTA Section */}
      <section className="w-full max-w-5xl mx-auto px-8 py-20 mt-10">
        <div className="glass-panel overflow-hidden border border-border shadow-[0_0_50px_rgba(79,140,255,0.15)] rounded-3xl p-12 text-center relative">
          <div className="absolute inset-0 bg-gradient-to-b from-primary/10 to-transparent pointer-events-none" />
          <h2 className="text-4xl font-bold mb-6">Stop Reacting. Start Predicting.</h2>
          <p className="text-lg text-muted-text max-w-2xl mx-auto mb-10">
            Join the MSMEs and Banks that are using AI to secure their financial liquidity. Fast setup, instant insights.
          </p>
          <Button size="lg" className="px-10 py-6 text-lg rounded-full">
            Launch Your Dashboard Now
          </Button>
        </div>
      </section>

    </div>
  );
}
