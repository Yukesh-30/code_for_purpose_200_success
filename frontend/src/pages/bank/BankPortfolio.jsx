import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Building2, Users, AlertCircle, TrendingUp, HandCoins, Activity } from 'lucide-react';
import { Button } from '../../components/ui/Button';

const portfolioTrend = [
  { month: 'Jan', aum: 4.2, risk: 12 },
  { month: 'Feb', aum: 4.5, risk: 10 },
  { month: 'Mar', aum: 4.8, risk: 15 },
  { month: 'Apr', aum: 5.2, risk: 18 },
  { month: 'May', aum: 5.1, risk: 14 },
  { month: 'Jun', aum: 5.5, risk: 13 },
];

const riskDistribution = [
  { category: 'Low', count: 142 },
  { category: 'Medium', count: 45 },
  { category: 'High', count: 18 },
  { category: 'Critical', count: 4 },
];

export default function BankPortfolio() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Portfolio Dashboard</h1>
          <p className="text-muted-text mt-1">Aggregated monitoring of MSME assets and risk health.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline">Schedule Report</Button>
          <Button>Export Data</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <Card className="glass-panel group">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-text mb-1">Total Assets (AUM)</p>
                <h3 className="text-3xl font-bold text-primary-text">$5.5M</h3>
              </div>
              <div className="p-2 bg-primary/10 rounded-lg">
                <Building2 className="text-primary" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <span className="text-success flex items-center"><TrendingUp size={16} className="mr-1"/> +8.2%</span>
              <span className="text-muted-text ml-2">Growth QoQ</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel group">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-text mb-1">Active MSME Clients</p>
                <h3 className="text-3xl font-bold text-primary-text">209</h3>
              </div>
              <div className="p-2 bg-secondary/10 rounded-lg">
                <Users className="text-secondary" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-muted-text">
              <span>+12 new this month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel group border-danger/30 overflow-hidden relative">
          <div className="absolute inset-0 bg-danger/5 opacity-50" />
          <CardContent className="p-6 relative z-10">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-text mb-1">Portfolio Risk Score</p>
                <h3 className="text-3xl font-bold text-danger">High (72)</h3>
              </div>
              <div className="p-2 bg-danger/10 rounded-lg">
                <AlertCircle className="text-danger" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-danger">
              <Badge variant="danger">Attention Needed</Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-panel group">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-muted-text mb-1">Pending Loans</p>
                <h3 className="text-3xl font-bold text-warning">$840k</h3>
              </div>
              <div className="p-2 bg-warning/10 rounded-lg">
                <HandCoins className="text-warning" size={24} />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-muted-text">
              <span>18 applications review</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Portfolio Performance & Risk Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={portfolioTrend}>
                  <defs>
                    <linearGradient id="colorAum" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#4F8CFF" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#4F8CFF" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#7C879F', fontSize: 12}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#7C879F', fontSize: 12}} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    itemStyle={{ color: '#F5F7FA' }}
                  />
                  <Area type="monotone" dataKey="aum" stroke="#4F8CFF" strokeWidth={3} fillOpacity={1} fill="url(#colorAum)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Client Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={riskDistribution} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="category" type="category" axisLine={false} tickLine={false} tick={{fill: '#F5F7FA', fontSize: 12}} />
                  <Tooltip cursor={{fill: 'transparent'}} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.category === 'Critical' ? '#FF5C5C' : entry.category === 'High' ? '#F5A524' : entry.category === 'Medium' ? '#4F8CFF' : '#16C784'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 text-center text-sm text-muted-text">
              78% of the portfolio is in the <span className="text-success font-semibold">Safe Zone</span>.
            </div>
          </CardContent>
        </Card>
      </div>

    </div>
  );
}

// Helper Cell component for BarChart
function Cell({ fill }) {
  return <rect fill={fill} />;
}
