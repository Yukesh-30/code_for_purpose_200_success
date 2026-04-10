import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ScatterChart, Scatter, ZAxis } from 'recharts';
import { ShieldCheck, TrendingDown, Target, BrainCircuit, Info } from 'lucide-react';
import { Button } from '../../components/ui/Button';

const defaultProbability = [
  { month: 'Jan', prob: 2.1 },
  { month: 'Feb', prob: 2.3 },
  { month: 'Mar', prob: 3.5 },
  { month: 'Apr', prob: 4.8 },
  { month: 'May', prob: 4.2 },
  { month: 'Jun', prob: 3.9 },
];

const scatterData = [
  { x: 45, y: 30, z: 200, name: 'Manufacturing' },
  { x: 30, y: 50, z: 150, name: 'Retail' },
  { x: 70, y: 15, z: 100, name: 'SaaS' },
  { x: 80, y: 80, z: 300, name: 'Logistics' },
  { x: 20, y: 10, z: 400, name: 'Agro' },
];

export default function RiskDefaultPrediction() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Risk & Default Prediction</h1>
          <p className="text-muted-text mt-1">AI-driven forecasting of portfolio-wide delinquency and default events.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Probability Line Chart */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Average Probability of Default (PD)</CardTitle>
            <Badge variant="outline" className="text-info border-info">Aggregated View</Badge>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={defaultProbability}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#7C879F', fontSize: 12}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#7C879F', fontSize: 12}} tickFormatter={(val) => `${val}%`} />
                  <Tooltip contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                  <Line type="monotone" dataKey="prob" stroke="#FF5C5C" strokeWidth={3} dot={{r: 4}} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Model Confidence */}
        <div className="space-y-6">
          <Card className="glass-panel border-primary/30">
            <CardContent className="p-6">
               <div className="flex items-center gap-3 mb-4">
                 <div className="p-2 bg-primary/10 rounded-lg text-primary"><BrainCircuit size={24}/></div>
                 <h4 className="font-bold">AI Model Health</h4>
               </div>
               <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>Model Accuracy</span>
                      <span>96.2%</span>
                    </div>
                    <div className="w-full bg-secondary-background h-1.5 rounded-full overflow-hidden">
                       <div className="bg-success h-full" style={{width: '96.2%'}}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-xs mb-1">
                      <span>Predictive Power (Gini)</span>
                      <span>0.74</span>
                    </div>
                    <div className="w-full bg-secondary-background h-1.5 rounded-full overflow-hidden">
                       <div className="bg-primary h-full" style={{width: '74%'}}></div>
                    </div>
                  </div>
               </div>
               <p className="text-[10px] text-muted-text mt-6 flex items-center gap-1">
                 <Info size={10} /> Last retrained on Apr 1, 2026.
               </p>
            </CardContent>
          </Card>

          <Card className="glass-panel">
            <CardContent className="p-6">
               <div className="flex items-center gap-3 mb-2">
                 <Target className="text-warning" size={20} />
                 <h4 className="font-bold text-sm">Default Hotspots</h4>
               </div>
               <p className="text-xs text-muted-text">
                 <strong>Logistics</strong> sector shows 23% increase in stress probability due to fuel price volatility.
               </p>
               <Button variant="link" size="sm" className="px-0 h-auto text-xs mt-2 text-primary">Download Deep Dive</Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Sector Risk Matrix */}
      <Card>
        <CardHeader>
          <CardTitle>Portfolio Concentration & Stress Matrix</CardTitle>
        </CardHeader>
        <CardContent>
           <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                 <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid stroke="rgba(255,255,255,0.05)" />
                    <XAxis type="number" dataKey="x" name="Exposure" unit="M" axisLine={false} tickLine={false} tick={{fill: '#7C879F', fontSize: 10}} label={{ value: 'Portfolio Exposure ($M)', position: 'bottom', fill: '#7C879F', fontSize: 10 }} />
                    <YAxis type="number" dataKey="y" name="Risk" unit="%" axisLine={false} tickLine={false} tick={{fill: '#7C879F', fontSize: 10}} label={{ value: 'Risk Probability (%)', angle: -90, position: 'left', fill: '#7C879F', fontSize: 10 }} />
                    <ZAxis type="number" dataKey="z" range={[60, 400]} name="Clients" />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                    <Scatter name="Sectors" data={scatterData} fill="#4F8CFF" />
                 </ScatterChart>
              </ResponsiveContainer>
           </div>
           <div className="mt-4 flex justify-center gap-6 text-xs text-muted-text">
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-primary/20"></span> Small Circle: Few Clients</span>
              <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-primary/80"></span> Large Circle: Many Clients</span>
           </div>
        </CardContent>
      </Card>
    </div>
  );
}
