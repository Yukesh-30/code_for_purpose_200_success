import React, { useState } from 'react';
import { ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Sparkles, Calendar, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';

const generateForecastData = (scenario) => {
  return Array.from({ length: 60 }).map((_, i) => {
    let base = 20000 + Math.sin(i / 5) * 15000;
    
    // Apply scenario modifications
    if (scenario === 'delay') {
      base -= i * 300; // Simulated compounding cash shortage due to delays
    } else if (scenario === 'expense') {
      base -= 10000;
    } else if (scenario === 'revenue') {
      base *= 0.9;
    }

    return {
      date: `Day ${i + 1}`,
      expected: base,
      upperBound: base + 5000,
      lowerBound: base - 5000,
      actual: i < 15 ? base + (Math.random() * 2000 - 1000) : null
    };
  });
};

export default function Forecasting() {
  const [scenario, setScenario] = useState('base');
  const data = generateForecastData(scenario);

  return (
    <div className="space-y-6">
      
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Liquidity Forecast</h1>
          <p className="text-muted-text mt-1">Simulate scenarios to see how your cash gap evolves over the next 60 days.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2"><Calendar size={16} /> Date Range</Button>
          <Button className="gap-2" onClick={async () => {
            try {
              const resp = await fetch('http://localhost:5000/forecasting/optimize', { method: 'POST' });
              const data = await resp.json();
              alert(data.message);
            } catch (e) {
              alert('Failed to optimize.');
            }
          }}><Sparkles size={16} /> Auto-Optimize</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Left Control Panel / Scenarios */}
        <div className="lg:col-span-1 space-y-4">
          <Card className={`cursor-pointer transition-colors ${scenario === 'base' ? 'border-primary ring-1 ring-primary/50' : 'hover:border-border/80'}`} onClick={() => setScenario('base')}>
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <CardTitle className="text-base">Baseline Forecast</CardTitle>
                <p className="text-xs text-muted-text mt-1">Expected current trajectory</p>
              </div>
              {scenario === 'base' && <Badge variant="success">Active</Badge>}
            </CardContent>
          </Card>
          
          <Card className={`cursor-pointer transition-colors ${scenario === 'delay' ? 'border-danger ring-1 ring-danger/50' : 'hover:border-border/80'}`} onClick={() => setScenario('delay')}>
            <CardContent className="p-4 flex items-start gap-3">
              <TrendingDown className="text-danger mt-1 shrink-0" size={18} />
              <div>
                <CardTitle className="text-base">Invoice Delay +20%</CardTitle>
                <p className="text-xs text-muted-text mt-1">If average collection period increases by 20%</p>
                {scenario === 'delay' && <p className="text-xs text-danger font-medium mt-2">Predicted Gap: -$24,000</p>}
              </div>
            </CardContent>
          </Card>

          <Card className={`cursor-pointer transition-colors ${scenario === 'expense' ? 'border-warning ring-1 ring-warning/50' : 'hover:border-border/80'}`} onClick={() => setScenario('expense')}>
            <CardContent className="p-4 flex items-start gap-3">
              <TrendingUp className="text-warning mt-1 shrink-0" size={18} />
              <div>
                <CardTitle className="text-base">Expenses +15%</CardTitle>
                <p className="text-xs text-muted-text mt-1">If vendor costs or payroll jumps unexpectedly</p>
              </div>
            </CardContent>
          </Card>

          <Card className={`cursor-pointer transition-colors ${scenario === 'revenue' ? 'border-info ring-1 ring-info/50' : 'hover:border-border/80'}`} onClick={() => setScenario('revenue')}>
            <CardContent className="p-4 flex items-start gap-3">
              <TrendingDown className="text-info mt-1 shrink-0" size={18} />
              <div>
                <CardTitle className="text-base">Revenue Drop -10%</CardTitle>
                <p className="text-xs text-muted-text mt-1">Simulating a slow season effect</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Chart */}
        <Card className="lg:col-span-3 glass-panel">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle>Cash Flow Prediction bounds</CardTitle>
              <div className="flex items-center gap-4 mt-2 text-xs text-muted-text">
                 <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-success"></span> Actuals</span>
                 <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-primary/50"></span> Confidence Interval (90%)</span>
                 <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-primary"></span> Predicted Engine</span>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="h-[400px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 12 }} dy={10} minTickGap={30} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 12 }} dx={-10} tickFormatter={(val) => `$${val/1000}k`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px' }}
                    itemStyle={{ color: '#F5F7FA' }}
                    labelStyle={{ color: '#AAB2C8' }}
                  />
                  {/* Confidence Interval Band */}
                  <Area type="monotone" dataKey="upperBound" stroke="none" fill="#4F8CFF" fillOpacity={0.1} />
                  <Area type="monotone" dataKey="lowerBound" stroke="none" fill="#121A2F" fillOpacity={1} />
                  
                  {/* Lines */}
                  <Line type="monotone" dataKey="expected" stroke="#4F8CFF" strokeWidth={3} dot={false} strokeDasharray="5 5" />
                  <Line type="monotone" dataKey="actual" stroke="#16C784" strokeWidth={3} dot={false} />

                  {/* Highlight Zero line for risk */}
                  <Line type="monotone" dataKey={() => 0} stroke="#FF5C5C" strokeWidth={1} strokeDasharray="3 3" dot={false} />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            
            {scenario !== 'base' && (
              <div className="mt-6 p-4 bg-secondary-background border border-border rounded-xl flex items-center justify-between">
                <div>
                  <h4 className="font-semibold flex items-center gap-2"><Sparkles size={16} className="text-secondary"/> AI Scenario Summary</h4>
                  <p className="text-sm text-muted-text mt-1">This scenario will force your balance into negative territory by Day 42. Immediate action is suggested.</p>
                </div>
                <Button className="shrink-0 gap-2" onClick={async () => {
                  try {
                    const resp = await fetch('http://localhost:5000/forecasting/mitigations', { method: 'POST' });
                    const data = await resp.json();
                    alert(data.message);
                  } catch (e) {
                    alert('Action failed.');
                  }
                }}>View Mitigations <ArrowRight size={16} /></Button>
              </div>
            )}
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
