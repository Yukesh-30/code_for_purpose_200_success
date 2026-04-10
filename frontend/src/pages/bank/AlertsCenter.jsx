import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Bell, AlertTriangle, Info, CheckCircle, Search, Filter } from 'lucide-react';
import { Input } from '../../components/ui/Input';

const alerts = [
  { id: 1, type: 'critical', title: 'Cash Flow Drop Detected', client: 'Zylos Manufacturing', time: '10 min ago', desc: 'Predictive model flags 40% probability of default in next 60 days.' },
  { id: 2, type: 'warning', title: 'Large Transaction Alert', client: 'Stellar Retail', time: '2 hrs ago', desc: 'Unusual outflow of $85k detected against average $12k.' },
  { id: 3, type: 'info', title: 'KYC Document Expiring', client: 'Alpha Logistics', time: '1 day ago', desc: 'Operating license renewal required by May 15.' },
  { id: 4, type: 'success', title: 'Collection Target Met', client: 'Portfolio Wide', time: '2 days ago', desc: 'April collection exceeds forecast by 12%.' },
  { id: 5, type: 'critical', title: 'Late Payment Recorded', client: 'Nexus Solutions', time: '3 days ago', desc: 'ID INV-2051 was not cleared by due date (Apr 20).' },
];

export default function AlertsCenter() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Alert Center</h1>
          <p className="text-muted-text mt-1">Real-time financial monitoring and event logs.</p>
        </div>
        <div className="flex gap-2">
           <Button variant="outline">Mark All as Read</Button>
           <Button>Clear History</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Statistics Widgets */}
        <div className="lg:col-span-1 space-y-4">
           <Card className="glass-panel border-danger/30">
              <CardContent className="p-4 flex items-center justify-between">
                 <div className="flex items-center gap-3">
                    <div className="p-2 bg-danger/10 text-danger rounded-lg"><AlertTriangle size={20}/></div>
                    <span className="font-semibold text-sm">Critical</span>
                 </div>
                 <span className="text-xl font-bold">12</span>
              </CardContent>
           </Card>
           <Card className="glass-panel border-warning/30">
              <CardContent className="p-4 flex items-center justify-between">
                 <div className="flex items-center gap-3">
                    <div className="p-2 bg-warning/10 text-warning rounded-lg"><Info size={20}/></div>
                    <span className="font-semibold text-sm">Warnings</span>
                 </div>
                 <span className="text-xl font-bold">45</span>
              </CardContent>
           </Card>
           <Card className="glass-panel border-info/30">
              <CardContent className="p-4 flex items-center justify-between">
                 <div className="flex items-center gap-3">
                    <div className="p-2 bg-info/10 text-info rounded-lg"><Bell size={20}/></div>
                    <span className="font-semibold text-sm">Operational</span>
                 </div>
                 <span className="text-xl font-bold">128</span>
              </CardContent>
           </Card>
        </div>

        {/* Alerts List */}
        <Card className="lg:col-span-3">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Recent Notifications</CardTitle>
            <div className="flex gap-2">
               <div className="relative w-64 hidden sm:block">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={16} />
                  <Input placeholder="Search alerts..." className="pl-9 h-9 border-border bg-background" />
               </div>
               <Button variant="outline" size="sm" className="gap-2"><Filter size={16}/> Filter</Button>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border">
              {alerts.map((alert) => (
                <div key={alert.id} className="p-6 hover:bg-white/5 transition-colors cursor-pointer group">
                  <div className="flex items-start gap-4">
                    <div className={`p-2 rounded-full mt-1 ${
                      alert.type === 'critical' ? 'bg-danger/20 text-danger' : 
                      alert.type === 'warning' ? 'bg-warning/20 text-warning' : 
                      alert.type === 'info' ? 'bg-info/20 text-info' : 'bg-success/20 text-success'
                    }`}>
                      {alert.type === 'critical' || alert.type === 'warning' ? <AlertTriangle size={18} /> : 
                       alert.type === 'info' ? <Info size={18} /> : <CheckCircle size={18} />}
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-1">
                        <h4 className="font-bold text-primary-text">{alert.title}</h4>
                        <span className="text-xs text-muted-text">{alert.time}</span>
                      </div>
                      <p className="text-xs text-primary/70 mb-2 font-semibold">{alert.client}</p>
                      <p className="text-sm text-secondary-text leading-relaxed">{alert.desc}</p>
                      <div className="mt-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button variant="outline" size="sm" className="h-7 text-xs">Acknowledge</Button>
                        <Button variant="ghost" size="sm" className="h-7 text-xs">View Details</Button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-6 text-center border-t border-border">
              <Button variant="link" className="text-muted-text hover:text-primary">Load Older Notifications</Button>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
