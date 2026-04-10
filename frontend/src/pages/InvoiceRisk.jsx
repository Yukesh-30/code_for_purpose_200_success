import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { AlertTriangle, TrendingDown, Search, Filter, Download } from 'lucide-react';
import { Input } from '../components/ui/Input';

const invoices = [
  { id: 'INV-2041', client: 'Acme Corp', amount: 12450, dueDate: '2026-04-12', prob: 85, days: 14, status: 'Critical' },
  { id: 'INV-2045', client: 'Global Tech', amount: 8200, dueDate: '2026-04-15', prob: 72, days: 8, status: 'High Risk' },
  { id: 'INV-2048', client: 'Stark Ind', amount: 3100, dueDate: '2026-04-16', prob: 45, days: 3, status: 'Medium Risk' },
  { id: 'INV-2050', client: 'Nexus Inc', amount: 4100, dueDate: '2026-04-18', prob: 91, days: 21, status: 'Critical' },
  { id: 'INV-2052', client: 'Wayne Ent', amount: 15600, dueDate: '2026-04-20', prob: 12, days: 0, status: 'Low Risk' },
];

export default function InvoiceRisk() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Invoice Risk</h1>
          <p className="text-muted-text mt-1">Predict payment delays before they squeeze your cash flow.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="glass-panel border-danger/30">
          <CardContent className="p-6">
             <p className="text-sm font-medium text-danger mb-1">Critical Value at Risk</p>
             <h3 className="text-3xl font-bold text-primary-text">$16,550</h3>
             <p className="text-xs text-muted-text mt-2">2 Invoices</p>
          </CardContent>
        </Card>
        <Card className="glass-panel border-warning/30">
          <CardContent className="p-6">
             <p className="text-sm font-medium text-warning mb-1">High Risk Value</p>
             <h3 className="text-3xl font-bold text-primary-text">$8,200</h3>
             <p className="text-xs text-muted-text mt-2">1 Invoice</p>
          </CardContent>
        </Card>
        <Card className="glass-panel border-success/30">
          <CardContent className="p-6">
             <p className="text-sm font-medium text-success mb-1">Low Risk Value</p>
             <h3 className="text-3xl font-bold text-primary-text">$15,600</h3>
             <p className="text-xs text-muted-text mt-2">1 Invoice</p>
          </CardContent>
        </Card>
        <Card className="glass-panel">
          <CardContent className="p-6">
             <p className="text-sm font-medium text-muted-text mb-1">Average Delay Predicted</p>
             <h3 className="text-3xl font-bold text-primary-text">9 Days</h3>
             <p className="text-xs text-danger mt-2 flex items-center gap-1"><TrendingDown size={14}/> +2 days vs last month</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Outstanding Invoices Prediction</CardTitle>
          <div className="flex gap-2">
            <div className="relative w-64 hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={16} />
              <Input placeholder="Search client or ID..." className="pl-9 h-9 border-border bg-background" />
            </div>
            <Button variant="outline" size="sm" className="gap-2"><Filter size={16}/> Filter</Button>
            <Button variant="outline" size="sm" className="gap-2"><Download size={16}/> Export</Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded-lg border border-border">
            <table className="w-full text-sm text-left">
              <thead className="bg-secondary-background/50 text-muted-text text-xs uppercase font-semibold">
                <tr>
                  <th className="px-6 py-4">Invoice ID</th>
                  <th className="px-6 py-4">Client</th>
                  <th className="px-6 py-4">Amount</th>
                  <th className="px-6 py-4">Due Date</th>
                  <th className="px-6 py-4">Delay Probability</th>
                  <th className="px-6 py-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {invoices.map((inv) => (
                  <tr key={inv.id} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4 font-medium">{inv.id}</td>
                    <td className="px-6 py-4">{inv.client}</td>
                    <td className="px-6 py-4 font-semibold">${inv.amount.toLocaleString()}</td>
                    <td className="px-6 py-4">{inv.dueDate}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className="w-8">{inv.prob}%</span>
                        <div className="flex-1 h-2 bg-background rounded-full overflow-hidden">
                           <div className={`h-full ${inv.prob > 80 ? 'bg-danger' : inv.prob > 60 ? 'bg-warning' : inv.prob > 30 ? 'bg-secondary' : 'bg-success'}`} style={{ width: `${inv.prob}%` }}></div>
                        </div>
                        <span className="text-xs text-muted-text w-12">{inv.days > 0 ? `+${inv.days}d` : '-'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={inv.status === 'Critical' ? 'danger' : inv.status === 'High Risk' ? 'warning' : inv.status === 'Medium Risk' ? 'outline' : 'success'}>
                        {inv.status}
                      </Badge>
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
