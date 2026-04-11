import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Building2, 
  MapPin, 
  Briefcase, 
  TrendingUp, 
  Users, 
  FileText,
  CheckCircle2,
  AlertCircle,
  ArrowRight
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { useAuth } from '../context/AuthContext';

export default function CompleteProfile() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    business_name: '',
    business_type: 'Retail',
    industry: 'Retail',
    gst_number: '',
    annual_revenue: '',
    employee_count: '',
    city: '',
    state: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/business/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          user_id: user.id
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Update user config in local storage with new business_id immediately
        const savedUser = JSON.parse(localStorage.getItem('user') || '{}');
        savedUser.business_id = data.business_id;
        localStorage.setItem('user', JSON.stringify(savedUser));
        
        // Let AuthContext pick it up via refresh or reload, but we'll navigate directly
        window.location.href = '/upload-data';
      } else {
        setError(data.error || 'Failed to create business profile');
      }
    } catch (err) {
      setError('Connection to server failed');
    } finally {
      setLoading(false);
    }
  };

  const businessTypes = ['Retail', 'Manufacturing', 'Service', 'Technology', 'Healthcare', 'Restaurant'];
  const industries = ['Retail', 'Textile', 'F&B', 'Tech', 'Automotive', 'Logistics'];

  return (
    <div className="min-h-screen theme-gradient py-12 px-6 flex items-center justify-center">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-2xl"
      >
        <Card className="glass-panel border-white/10 shadow-2xl">
          <CardHeader className="text-center">
            <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center text-primary mx-auto mb-4">
              <Building2 size={32} />
            </div>
            <CardTitle className="text-3xl">Complete Your Profile</CardTitle>
            <CardDescription>Tell us about your business to unlock AI-powered insights.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-3 rounded-lg bg-danger/10 border border-danger/20 text-danger text-sm flex items-center gap-2">
                  <AlertCircle size={16} />
                  {error}
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase text-muted-text">Business Name</label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={18} />
                    <Input 
                      placeholder="e.g. Acme Corp" 
                      className="pl-10 h-10 bg-white/5 border-white/10"
                      value={formData.business_name}
                      onChange={(e) => setFormData({...formData, business_name: e.target.value})}
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase text-muted-text">GST Number (Optional)</label>
                  <div className="relative">
                    <FileText className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={18} />
                    <Input 
                      placeholder="e.g. 29AAAAA0000A1Z5" 
                      className="pl-10 h-10 bg-white/5 border-white/10 text-xs uppercase"
                      value={formData.gst_number}
                      onChange={(e) => setFormData({...formData, gst_number: e.target.value.toUpperCase()})}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase text-muted-text">Business Type</label>
                  <div className="relative">
                    <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={18} />
                    <select 
                      className="w-full h-10 pl-10 pr-4 bg-white/5 border border-white/10 rounded-lg text-sm text-primary-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                      value={formData.business_type}
                      onChange={(e) => setFormData({...formData, business_type: e.target.value})}
                    >
                      {businessTypes.map(type => <option key={type} value={type}>{type}</option>)}
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase text-muted-text">Industry</label>
                  <div className="relative">
                    <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={18} />
                    <select 
                      className="w-full h-10 pl-10 pr-4 bg-white/5 border border-white/10 rounded-lg text-sm text-primary-text focus:outline-none focus:ring-2 focus:ring-primary/50"
                      value={formData.industry}
                      onChange={(e) => setFormData({...formData, industry: e.target.value})}
                    >
                      {industries.map(ind => <option key={ind} value={ind}>{ind}</option>)}
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase text-muted-text">Annual Revenue (₹)</label>
                  <div className="relative">
                    <TrendingUp className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={18} />
                    <Input 
                      type="number"
                      placeholder="e.g. 5000000" 
                      className="pl-10 h-10 bg-white/5 border-white/10"
                      value={formData.annual_revenue}
                      onChange={(e) => setFormData({...formData, annual_revenue: e.target.value})}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase text-muted-text">Employee Count</label>
                  <div className="relative">
                    <Users className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={18} />
                    <Input 
                      type="number"
                      placeholder="e.g. 20" 
                      className="pl-10 h-10 bg-white/5 border-white/10"
                      value={formData.employee_count}
                      onChange={(e) => setFormData({...formData, employee_count: e.target.value})}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase text-muted-text">City</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={18} />
                    <Input 
                      placeholder="e.g. Chennai" 
                      className="pl-10 h-10 bg-white/5 border-white/10"
                      value={formData.city}
                      onChange={(e) => setFormData({...formData, city: e.target.value})}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold uppercase text-muted-text">State</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={18} />
                    <Input 
                      placeholder="e.g. Tamil Nadu" 
                      className="pl-10 h-10 bg-white/5 border-white/10"
                      value={formData.state}
                      onChange={(e) => setFormData({...formData, state: e.target.value})}
                    />
                  </div>
                </div>
              </div>

              <div className="pt-4 flex gap-4">
                <Button variant="ghost" className="flex-1" onClick={() => navigate('/dashboard')}>Skip for now</Button>
                <Button type="submit" className="flex-1" disabled={loading}>
                  {loading ? 'Saving...' : 'Complete Profile'} <ArrowRight size={18} className="ml-2" />
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
