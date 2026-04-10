import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { HandCoins, Target, TrendingUp, Filter, Search, ArrowRight } from 'lucide-react';
import { Input } from '../../components/ui/Input';

const opportunities = [
  { id: 'OP-1', name: 'Zylos Manufacturing', revGrowth: '+12%', eligibility: 94, recommended: 'Invoice Discounting', amt: '$50k - $200k', reason: 'Strong seasonal orders' },
  { id: 'OP-2', name: 'GreenLeaf Agrotech', revGrowth: '+25%', eligibility: 88, recommended: 'Equipment Finance', amt: '$100k - $300k', reason: 'Expansion potential' },
  { id: 'OP-3', name: 'Nexus Solutions', revGrowth: '+40%', eligibility: 91, recommended: 'Revolving Credit', amt: '$500k+', reason: 'Recurring SaaS revenue' },
  { id: 'OP-4', name: 'Alpha Logistics', revGrowth: '+8%', eligibility: 82, recommended: 'Fleet Leasing', amt: '$250k+', reason: 'Contract backlog' },
];

export default function LendingOpportunities() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Lending Opportunities</h1>
          <p className="text-muted-text mt-1">AI-driven cross-sell and up-sell engine matching products to safe, growing MSMEs.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="glass-panel border-success/30">
          <CardContent className="p-6">
             <p className="text-sm font-medium text-success mb-1">Total Opportunity Value</p>
             <h3 className="text-3xl font-bold text-primary-text">$2.4M</h3>
             <p className="text-xs text-muted-text mt-2">Mapped across 42 clients</p>
          </CardContent>
        </Card>
        <Card className="glass-panel group">
          <CardContent className="p-6">
             <p className="text-sm font-medium text-muted-text mb-1">Avg. Approval Confidence</p>
             <h3 className="text-3xl font-bold text-primary-text">86%</h3>
             <p className="text-xs text-success mt-2 flex items-center gap-1"><TrendingUp size={14}/> Top 10% Industry tier</p>
          </CardContent>
        </Card>
        <Card className="glass-panel group">
          <CardContent className="p-6">
             <p className="text-sm font-medium text-muted-text mb-1">Conversion Potential</p>
             <h3 className="text-3xl font-bold text-primary-text">$850k</h3>
             <p className="text-xs text-muted-text mt-2">Likely to convert in 30 days</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recommended Financial Products</CardTitle>
          <div className="flex gap-2">
            <div className="relative w-64 hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={16} />
              <Input placeholder="Search client..." className="pl-9 h-9 border-border bg-background" />
            </div>
            <Button variant="outline" size="sm" className="gap-2"><Filter size={16}/> Filter</Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="w-full text-sm text-left">
              <thead className="bg-secondary-background/50 text-muted-text text-xs uppercase font-semibold">
                <tr>
                  <th className="px-6 py-4">MSME Name</th>
                  <th className="px-6 py-4">Recommended Product</th>
                  <th className="px-6 py-4">Potential Volume</th>
                  <th className="px-6 py-4">Matching Score</th>
                  <th className="px-6 py-4">Key Driver</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {opportunities.map((op) => (
                  <tr key={op.id} className="hover:bg-white/5 transition-colors group">
                    <td className="px-6 py-4 font-medium text-primary-text">{op.name}</td>
                    <td className="px-6 py-4">
                       <Badge variant="outline" className="border-primary/40 text-primary">{op.recommended}</Badge>
                    </td>
                    <td className="px-6 py-4 font-semibold text-primary-text">{op.amt}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 min-w-[80px] h-2 bg-background rounded-full overflow-hidden">
                           <div className="h-full bg-success" style={{ width: `${op.eligibility}%` }}></div>
                        </div>
                        <span className="font-bold">{op.eligibility}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs italic text-muted-text">{op.reason}</td>
                    <td className="px-6 py-4 text-right">
                      <Button variant="secondary" size="sm" className="group-hover:bg-primary group-hover:text-white">
                        Pitch Product <ArrowRight size={14} className="ml-1" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
