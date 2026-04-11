import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { ShieldCheck, CalendarClock, Briefcase, Zap } from 'lucide-react';

const expenseData = [
  { name: 'Payroll', value: 45000 },
  { name: 'Vendor Payments', value: 25000 },
  { name: 'Rent & Utilities', value: 12000 },
  { name: 'Marketing', value: 8000 },
];
const COLORS = ['#4F8CFF', '#6C63FF', '#121A2F', '#7C879F'];

export default function WorkingCapital() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Working Capital</h1>
        <p className="text-muted-text mt-1">Monitor operational liquidity and upcoming obligations.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Gauge Card (Mocked with visuals) */}
        <Card className="glass-panel flex flex-col items-center justify-center p-8 text-center bg-gradient-to-br from-card to-secondary-background/80 relative overflow-hidden">
           <div className="absolute top-0 right-0 p-4">
             <Badge variant="outline" className="border-info text-info">Moderate Risk</Badge>
           </div>
           
           {/* Mock semi-circle gauge */}
           <div className="relative w-48 h-24 mb-6 mt-4">
             <div className="absolute inset-0 border-[16px] border-border rounded-t-full border-b-0"></div>
             <div className="absolute inset-0 border-[16px] border-warning rounded-t-full border-b-0" style={{ clipPath: 'polygon(0 0, 64% 0, 64% 100%, 0 100%)' }}></div>
             <div className="absolute bottom-[-10px] left-1/2 -translate-x-1/2 text-4xl font-bold text-primary-text">
               64
             </div>
           </div>
           
           <h3 className="text-lg font-semibold mt-4">Liquidity Score</h3>
           <p className="text-sm text-muted-text max-w-[200px] mt-2">Your ability to cover upcoming expenses is trending down. Action recommended.</p>
        </Card>

        {/* Breakdown Card */}
        <Card className="lg:col-span-2">
          <CardHeader>
             <CardTitle>Operating Expenses Base (Next 30 Days)</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col md:flex-row items-center">
            <div className="w-[200px] h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={expenseData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value" stroke="none">
                    {expenseData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-4 ml-8">
              {expenseData.map((item, i) => (
                <div key={i} className="flex justify-between items-center text-sm">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[i]}}></span>
                    <span className="text-primary-text">{item.name}</span>
                  </div>
                  <span className="font-semibold">${item.value.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

      </div>

      {/* Timeline obligations */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Critical Obligations</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative border-l-2 border-border ml-4 mt-2 space-y-8">
            
            <div className="relative pl-6">
              <span className="absolute -left-[11px] bg-danger rounded-full w-5 h-5 flex items-center justify-center ring-4 ring-background"><Briefcase size={10} className="text-white"/></span>
              <div className="bg-secondary-background/50 border border-border rounded-xl p-4">
                 <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold">Payroll Cycle</span>
                    <span className="font-bold text-danger">$45,000</span>
                 </div>
                 <p className="text-sm text-muted-text">Due: Apr 30. Predicted cash gap on this date. High Risk.</p>
                 <Button variant="outline" size="sm" className="mt-3 text-warning border-warning/50" onClick={async () => {
                   try {
                     const resp = await fetch('http://localhost:5000/recommendation/apply', { method: 'POST' });
                     const data = await resp.json();
                     alert(data.message);
                   } catch (e) {
                     alert('Action failed.');
                   }
                 }}>Explore Overdraft</Button>
              </div>
            </div>

            <div className="relative pl-6">
              <span className="absolute -left-[11px] bg-primary rounded-full w-5 h-5 flex items-center justify-center ring-4 ring-background"><ShieldCheck size={10} className="text-white"/></span>
              <div className="bg-secondary-background/50 border border-border rounded-xl p-4">
                 <div className="flex justify-between items-center mb-2">
                    <span className="font-semibold">AWS Cloud Hosting</span>
                    <span className="font-bold">$12,400</span>
                 </div>
                 <p className="text-sm text-muted-text">Due: May 2. Safe to pay.</p>
              </div>
            </div>

          </div>
        </CardContent>
      </Card>

    </div>
  );
}
