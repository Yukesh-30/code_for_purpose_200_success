import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { CheckCircle2, Zap, ArrowRight, Wallet, TrendingUp } from 'lucide-react';

const products = [
  {
    name: 'Invoice Financing',
    description: 'Advance cash on your outstanding $24,750 high-risk invoices.',
    benefits: ['Funds within 24hrs', 'No collateral required', 'Protects against delay'],
    prob: 92,
    icon: Wallet,
    color: 'primary',
    recommended: true
  },
  {
    name: 'Working Capital Line',
    description: 'Flexible $50,000 credit line to bridge the upcoming payroll gap.',
    benefits: ['Pay only on what you use', 'Revolving credit', 'Builds business credit'],
    prob: 78,
    icon: TrendingUp,
    color: 'info',
    recommended: false
  }
];

export default function BankingRecommendation() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Banking Matching</h1>
        <p className="text-muted-text mt-1">AI-recommended financial products based on your forecasted gaps and risk profile.</p>
      </div>

      <div className="p-6 rounded-2xl glass-panel border border-border bg-gradient-to-r from-primary/10 to-transparent flex items-center gap-4">
         <div className="p-3 bg-primary/20 text-primary rounded-xl shrink-0"><Zap size={24} /></div>
         <div>
            <h3 className="font-semibold text-lg text-primary-text">Why are we recommending products?</h3>
            <p className="text-sm text-secondary-text mt-1">Our model predicts a <strong className="text-danger">-$12,450 cash gap on Apr 24</strong>. Applying today ensures funds clear before your obligations are due.</p>
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-4">
        {products.map((p, i) => (
          <Card key={i} className={`relative overflow-hidden ${p.recommended ? 'ring-2 ring-primary border-transparent' : 'border-border'}`}>
            {p.recommended && (
              <div className="absolute top-0 right-0 bg-primary text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
                Top Match
              </div>
            )}
            <CardContent className="p-8">
               <div className="flex items-start gap-4 mb-6">
                 <div className={`p-4 rounded-2xl bg-${p.color}/10 text-${p.color}`}>
                   <p.icon size={32} />
                 </div>
                 <div>
                   <h2 className="text-2xl font-bold">{p.name}</h2>
                   <p className="text-muted-text mt-1">{p.description}</p>
                 </div>
               </div>

               <div className="space-y-3 mb-8">
                 {p.benefits.map((b, idx) => (
                   <div key={idx} className="flex items-center gap-2 text-sm text-secondary-text">
                     <CheckCircle2 className="text-success" size={16} /> {b}
                   </div>
                 ))}
               </div>

               <div className="pt-6 border-t border-border flex items-center justify-between">
                 <div>
                   <p className="text-xs text-muted-text mb-1">Pre-approval Confidence</p>
                   <div className="flex items-center gap-3">
                     <span className="text-2xl font-bold">{p.prob}%</span>
                     <div className="w-24 h-2 bg-background rounded-full overflow-hidden">
                       <div className="h-full bg-success rounded-full" style={{ width: `${p.prob}%` }}></div>
                     </div>
                   </div>
                 </div>
                 <Button className={`gap-2 ${p.recommended ? '' : 'variant-secondary'}`} onClick={async () => {
                   try {
                     const resp = await fetch('http://localhost:5000/recommendation/apply', { method: 'POST' });
                     const data = await resp.json();
                     alert(data.message);
                   } catch (e) {
                     alert('Action failed.');
                   }
                 }}>Apply Now <ArrowRight size={16}/></Button>
               </div>
            </CardContent>
          </Card>
        ))}
      </div>

    </div>
  );
}
