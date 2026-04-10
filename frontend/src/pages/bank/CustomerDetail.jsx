import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowLeft, Building2, Mail, Phone, ExternalLink, ShieldCheck, AlertTriangle, TrendingUp, HandCoins } from 'lucide-react';

const yearlyRevenue = [
  { month: 'Jan', rev: 45000, risk: 20 },
  { month: 'Feb', rev: 52000, risk: 22 },
  { month: 'Mar', rev: 48000, risk: 25 },
  { month: 'Apr', rev: 31000, risk: 65 }, // Dip
  { month: 'May', rev: 33000, risk: 70 },
];

export default function CustomerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft size={20} />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Zylos Manufacturing</h1>
          <p className="text-muted-text mt-1">Registry ID: {id || 'MSME-402'} • Industry: Logistics</p>
        </div>
        <div className="ml-auto flex gap-2">
           <Badge variant="danger" className="h-8 px-3">High Risk (88)</Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left: Client Info */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm uppercase tracking-wider text-muted-text">Principal Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start gap-3">
                <Building2 size={18} className="text-primary mt-1" />
                <div>
                  <p className="text-sm font-semibold">HQ Address</p>
                  <p className="text-xs text-muted-text">42 Industrial Way, South Sector, Tech Park</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Mail size={18} className="text-primary mt-1" />
                <div>
                  <p className="text-sm font-semibold">Contact Email</p>
                  <p className="text-xs text-muted-text">finance@zylos.com</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Phone size={18} className="text-primary mt-1" />
                <div>
                  <p className="text-sm font-semibold">Phone</p>
                  <p className="text-xs text-muted-text">+1 (555) 012-3456</p>
                </div>
              </div>
              <Button variant="outline" className="w-full text-xs h-8">
                View Full Credit Report <ExternalLink size={12} className="ml-2"/>
              </Button>
            </CardContent>
          </Card>

          <Card className="border-warning/30 bg-warning/5">
            <CardHeader>
              <CardTitle className="text-sm flex items-center gap-2">
                <ShieldCheck size={16} /> Compliance Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
               <div className="flex justify-between text-xs">
                 <span>KYC/AML Status</span>
                 <Badge variant="success">Verified</Badge>
               </div>
               <div className="flex justify-between text-xs">
                 <span>Tax Filings (2025)</span>
                 <Badge variant="success">Up to date</Badge>
               </div>
               <div className="flex justify-between text-xs">
                 <span>Annual Audit</span>
                 <Badge variant="warning">Due in 12 days</Badge>
               </div>
            </CardContent>
          </Card>
        </div>

        {/* Center/Right: Financial Trends */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             <Card className="glass-panel">
               <CardContent className="p-6">
                 <p className="text-sm text-muted-text mb-1">Total Loan Exposure</p>
                 <h3 className="text-2xl font-bold">$450,000.00</h3>
                 <div className="mt-3 flex gap-2">
                   <Badge variant="outline" className="text-info border-info">Term Loan (3yr)</Badge>
                 </div>
               </CardContent>
             </Card>
             <Card className="glass-panel">
               <CardContent className="p-6">
                 <p className="text-sm text-muted-text mb-1">Repayment History</p>
                 <h3 className="text-2xl font-bold text-success">98.4%</h3>
                 <p className="text-xs text-muted-text mt-1">1 late payment in last 24 months</p>
               </CardContent>
             </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Predictive Cash Flow Performance</CardTitle>
            </CardHeader>
            <CardContent>
               <div className="h-[250px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={yearlyRevenue}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#7C879F', fontSize: 12}} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: '#7C879F', fontSize: 12}} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                      />
                      <Line type="monotone" dataKey="rev" stroke="#4F8CFF" strokeWidth={3} dot={{r: 4}} />
                      <Line type="monotone" dataKey="risk" stroke="#FF5C5C" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
               </div>
               <div className="mt-4 p-4 bg-secondary-background border border-border rounded-xl">
                 <div className="flex items-start gap-3">
                    <AlertTriangle className="text-danger shrink-0 mt-1" size={20} />
                    <div>
                      <h4 className="font-semibold text-sm">AI Early Warning Check</h4>
                      <p className="text-xs text-muted-text mt-1 leading-relaxed">
                        Revenue dropped by 35% in Apr due to contract losses. Predicted liquidity gap in May is $12,000. 
                        We recommend offering a <strong>short-term bridge facility</strong> or <strong>invoice discounting</strong> immediately.
                      </p>
                      <div className="mt-3 flex gap-2">
                         <Button size="sm" className="h-7 text-xs">Initiate Outreach</Button>
                         <Button variant="outline" size="sm" className="h-7 text-xs">Flag for Audit</Button>
                      </div>
                    </div>
                 </div>
               </div>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
