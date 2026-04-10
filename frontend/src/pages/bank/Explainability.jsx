import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { BrainCircuit, Info, ShieldAlert, Cpu, Network } from 'lucide-react';
import { Button } from '../../components/ui/Button';

const featureImportance = [
  { name: 'Cash Flow Volatility', score: 85 },
  { name: 'Industry Sector Risk', score: 72 },
  { name: 'Debt Service Coverage', score: 68 },
  { name: 'Supplier Payment History', score: 45 },
  { name: 'Customer Diversification', score: 38 },
  { name: 'Macro-economic Index', score: 25 },
];

export default function Explainability() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Explainability Center</h1>
          <p className="text-muted-text mt-1">Understanding the 'Why' behind AI-generated risk ratings and predictions.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Feature Importance */}
        <Card className="glass-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu size={20} className="text-primary" /> Feature Importance (SHAP values)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[350px] w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={featureImportance} layout="vertical" margin={{ left: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fill: '#F5F7FA', fontSize: 11}} />
                  <Tooltip cursor={{fill: 'rgba(255,255,255,0.02)'}} contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                  <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                    {featureImportance.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={`rgba(79, 140, 255, ${1 - index * 0.12})`} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 p-3 bg-secondary-background/50 rounded-lg border border-border flex items-start gap-3">
               <Info size={16} className="text-info mt-1 shrink-0" />
               <p className="text-xs text-muted-text leading-relaxed">
                 The model is currenty prioritizing <strong>Cash Flow Volatility</strong> as the strongest predictor of default across the MSME portfolio.
               </p>
            </div>
          </CardContent>
        </Card>

        {/* Global Model Logic */}
        <div className="space-y-6">
          <Card className="glass-panel">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Network size={20} className="text-secondary" /> Model Architecture
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
               <div className="grid grid-cols-2 gap-4">
                 <div className="p-4 bg-secondary-background/50 rounded-xl border border-border">
                    <p className="text-[10px] text-muted-text uppercase font-bold tracking-wider">Type</p>
                    <p className="text-sm font-semibold">Ensemble Gradient Boosting (XGBoost)</p>
                 </div>
                 <div className="p-4 bg-secondary-background/50 rounded-xl border border-border">
                    <p className="text-[10px] text-muted-text uppercase font-bold tracking-wider">Inputs</p>
                    <p className="text-sm font-semibold">142 Data Points</p>
                 </div>
               </div>
               <div className="p-4 border border-border/60 rounded-xl">
                  <h4 className="text-sm font-bold mb-2">Ethical Guardrails & Bias Checks</h4>
                  <ul className="space-y-2">
                     <li className="flex items-center gap-2 text-xs text-muted-text"><ShieldAlert size={14} className="text-success" /> No protected class variables used in training.</li>
                     <li className="flex items-center gap-2 text-xs text-muted-text"><ShieldAlert size={14} className="text-success" /> Differential privacy applied to edge datasets.</li>
                     <li className="flex items-center gap-2 text-xs text-muted-text"><ShieldAlert size={14} className="text-success" /> Bias parity monitored monthly across sectors.</li>
                  </ul>
               </div>
               <Button variant="outline" className="w-full text-xs">Download Transparency Report</Button>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-primary/10 to-transparent border-primary/20">
             <CardContent className="p-6">
                <div className="flex items-center gap-3 mb-3">
                   <div className="p-2 bg-primary/20 rounded-lg"><BrainCircuit size={20} className="text-primary"/></div>
                   <h4 className="font-bold">Explainable AI (XAI) Dashboard</h4>
                </div>
                <p className="text-sm text-primary-text leading-relaxed">
                  Our platform uses LIME and SHAP value decomposition to ensure every risk rating is auditing-ready and can be explained to both customers and regulators.
                </p>
             </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
