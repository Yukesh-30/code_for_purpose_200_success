import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Wallet, AlertTriangle, TrendingDown, TrendingUp, Activity, ArrowRight, Zap } from 'lucide-react';
import { Button } from '../components/ui/Button';

// Mock Data
const cashFlowData = Array.from({ length: 30 }).map((_, i) => ({
  date: `Apr ${i + 1}`,
  balance: Math.max(5000, 20000 + Math.sin(i / 3) * 15000 - (i > 20 ? 12000 : 0)), // Creating a dip towards the end
  inflow: Math.random() * 5000 + 1000,
  outflow: Math.random() * 4000 + 2000,
}));

const highRiskInvoices = [
  { id: 'INV-2041', client: 'Acme Corp', amount: '$12,450', dueDate: 'Apr 12', risk: 85, daysDelay: 14 },
  { id: 'INV-2045', client: 'Global Tech', amount: '$8,200', dueDate: 'Apr 15', risk: 72, daysDelay: 8 },
  { id: 'INV-2050', client: 'Nexus Inc', amount: '$4,100', dueDate: 'Apr 18', risk: 91, daysDelay: 21 },
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
          <p className="text-muted-text mt-1">Your AI-generated financial summary for the next 30 days.</p>
        </div>
        <Button>Generate Report</Button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <Card className="glass-panel group">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-text mb-1">Current Cash Balance</p>
                <h3 className="text-3xl font-bold text-primary-text">$42,500.00</h3>
              </div>
              <div className="p-2 bg-secondary-background rounded-lg group-hover:bg-primary/20 transition-colors">
                <Wallet className="text-primary" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="flex items-center text-success"><TrendingUp size={16} className="mr-1" /> +2.4%</span>
              <span className="text-muted-text ml-2">from last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel group border-danger/50 relative overflow-hidden">
          <div className="absolute inset-0 bg-danger/5 group-hover:bg-danger/10 transition-colors" />
          <CardContent className="p-6 relative z-10">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-text mb-1">Forecasted Cash Gap</p>
                <h3 className="text-3xl font-bold text-danger">-$12,450.00</h3>
              </div>
              <div className="p-2 bg-secondary-background rounded-lg group-hover:bg-danger/20 transition-colors">
                <AlertTriangle className="text-danger" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <Badge variant="danger" className="mr-2">High Risk</Badge>
              <span className="text-muted-text">Expected Apr 24</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel group">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-text mb-1">Invoice Delay Risk</p>
                <h3 className="text-3xl font-bold text-warning">3 Critical</h3>
              </div>
              <div className="p-2 bg-secondary-background rounded-lg group-hover:bg-warning/20 transition-colors">
                <Activity className="text-warning" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="flex items-center text-danger"><TrendingDown size={16} className="mr-1" /> -12%</span>
              <span className="text-muted-text ml-2">collection rate</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel group">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-text mb-1">Working Capital Score</p>
                <h3 className="text-3xl font-bold text-primary-text">64/100</h3>
              </div>
              <div className="p-2 bg-secondary-background rounded-lg group-hover:bg-info/20 transition-colors">
                <TrendingUp className="text-info" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <Badge variant="warning" className="mr-2">Moderate</Badge>
              <span className="text-muted-text">Trending down</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts & Tables Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Chart */}
        <Card className="col-span-1 lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle>Cash Flow Forecast (30 Days)</CardTitle>
              <p className="text-sm text-muted-text mt-1">AI predicted liquidity including expected invoice delays.</p>
            </div>
            <select className="bg-secondary-background border border-border text-sm rounded-md px-3 py-1.5 outline-none">
              <option>30 Days</option>
              <option>60 Days</option>
              <option>90 Days</option>
            </select>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={cashFlowData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#4F8CFF" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#4F8CFF" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis 
                    dataKey="date" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#7C879F', fontSize: 12 }}
                    dy={10}
                    minTickGap={20}
                  />
                  <YAxis 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#7C879F', fontSize: 12 }}
                    tickFormatter={(val) => `$${val/1000}k`}
                    dx={-10}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px' }}
                    itemStyle={{ color: '#F5F7FA' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="balance" 
                    stroke="#4F8CFF" 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorBalance)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Right Column: Alerts & AI Recommendations */}
        <div className="space-y-6">
          <Card className="border-info/30">
            <CardHeader className="pb-3">
              <CardTitle className="text-info flex items-center gap-2">
                <Zap size={20} /> AI Recommendation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">Based on your forecasted cash gap of <strong>$12,450</strong> on Apr 24, we recommend an <strong>Invoice Financing</strong> product.</p>
              <div className="mt-4 p-3 bg-secondary-background rounded-lg border border-border">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-sm">Approval Odds</span>
                  <Badge variant="success">92%</Badge>
                </div>
                <div className="w-full bg-background rounded-full h-2">
                  <div className="bg-success h-2 rounded-full" style={{ width: '92%' }}></div>
                </div>
              </div>
              <Button className="w-full mt-4" variant="outline">View Products</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <div className="flex justify-between items-center">
                <CardTitle>High Risk Invoices</CardTitle>
                <Button variant="link" size="sm" className="px-0">View All</Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {highRiskInvoices.map((inv) => (
                <div key={inv.id} className="flex flex-col gap-2 p-3 bg-secondary-background/50 rounded-xl border border-border hover:bg-secondary-background transition-colors">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold text-sm">{inv.client}</span>
                    <span className="font-bold text-danger">{inv.amount}</span>
                  </div>
                  <div className="flex justify-between items-center text-xs text-muted-text">
                    <span>Due: {inv.dueDate}</span>
                    <span className="flex items-center text-danger"><AlertTriangle size={12} className="mr-1" /> {inv.daysDelay} days late (est.)</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
