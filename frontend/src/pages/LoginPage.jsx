import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { TrendingUp, User, ShieldCheck, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleDemoLogin = (role) => {
    login(role);
    if (role === 'msme') {
      navigate('/dashboard');
    } else {
      navigate('/bank/portfolio');
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/20 blur-[120px] rounded-full pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12 relative z-10"
      >
        <div className="flex items-center justify-center gap-2 font-bold text-3xl text-gradient mb-4">
          <TrendingUp className="text-primary" size={40} />
          FlowSight AI
        </div>
        <p className="text-muted-text max-w-sm mx-auto">
          Sign in to access your AI-powered financial intelligence dashboard.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-2xl relative z-10">
        
        {/* MSME Persona */}
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Card className="cursor-pointer border-border/60 hover:border-primary/50 transition-colors h-full group" onClick={() => handleDemoLogin('msme')}>
            <CardContent className="p-8 flex flex-col items-center text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-colors">
                <User size={32} />
              </div>
              <div>
                <h3 className="text-xl font-bold">MSME Owner</h3>
                <p className="text-sm text-muted-text mt-2">View cash flow forecasts, invoice risks, and banking recommendations.</p>
              </div>
              <Button variant="outline" className="w-full group-hover:bg-primary group-hover:text-white">
                Enter as MSME <ArrowRight size={16} className="ml-2" />
              </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Bank Admin Persona */}
        <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
          <Card className="cursor-pointer border-border/60 hover:border-secondary/50 transition-colors h-full group" onClick={() => handleDemoLogin('bank')}>
            <CardContent className="p-8 flex flex-col items-center text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-secondary/10 flex items-center justify-center text-secondary group-hover:bg-secondary group-hover:text-white transition-colors">
                <ShieldCheck size={32} />
              </div>
              <div>
                <h3 className="text-xl font-bold">Bank Admin</h3>
                <p className="text-sm text-muted-text mt-2">Monitor portfolio risk, detect default patterns, and manage system alerts.</p>
              </div>
              <Button variant="outline" className="w-full group-hover:bg-secondary group-hover:text-white">
                Enter as Bank Admin <ArrowRight size={16} className="ml-2" />
              </Button>
            </CardContent>
          </Card>
        </motion.div>

      </div>

      <p className="mt-12 text-sm text-muted-text">
        Don't have an account? <span className="text-primary hover:underline cursor-pointer">Contact sales</span>
      </p>
    </div>
  );
}
