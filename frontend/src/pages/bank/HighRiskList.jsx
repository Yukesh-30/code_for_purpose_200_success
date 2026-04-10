import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Search, Filter, AlertTriangle, ArrowUpRight, TrendingDown } from 'lucide-react';
import { Input } from '../../components/ui/Input';

const riskyMSMEs = [
  { id: 'MSME-402', name: 'Zylos Manufacturing', industry: 'Logistics', loanAmount: '$450,000', riskScore: 88, trend: 'Increasing', reason: 'Declining Cash Reserves' },
  { id: 'MSME-115', name: 'GreenLeaf Agrotech', industry: 'Agriculture', loanAmount: '$120,000', riskScore: 74, trend: 'Stable', reason: 'Seasonal Revenue Drop' },
  { id: 'MSME-098', name: 'Stellar Retail', industry: 'Consumer Goods', loanAmount: '$85,000', riskScore: 92, trend: 'Increasing', reason: 'High Debt-to-Income' },
  { id: 'MSME-551', name: 'Nexus Solutions', industry: 'Software', loanAmount: '$210,000', riskScore: 68, trend: 'Decreasing', reason: 'Slow Receivable Cycle' },
  { id: 'MSME-221', name: 'Titan Heavy Ind', industry: 'Manufacturing', loanAmount: '$1.2M', riskScore: 81, trend: 'Increasing', reason: 'Working Capital Gap' },
];

export default function HighRiskList() {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">High-Risk MSMEs</h1>
          <p className="text-muted-text mt-1">Real-time monitoring of clients flagged for financial stress.</p>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Priority Monitoring List</CardTitle>
          <div className="flex gap-2">
            <div className="relative w-64 hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={16} />
              <Input placeholder="Search company or sector..." className="pl-9 h-9 border-border bg-background" />
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
                  <th className="px-6 py-4">Industry</th>
                  <th className="px-6 py-4">Exposure</th>
                  <th className="px-6 py-4">Risk Level</th>
                  <th className="px-6 py-4">Predominant Issue</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {riskyMSMEs.map((client) => (
                  <tr key={client.id} className="hover:bg-white/5 transition-colors group">
                    <td className="px-6 py-4">
                      <div className="font-medium text-primary-text">{client.name}</div>
                      <div className="text-xs text-muted-text">{client.id}</div>
                    </td>
                    <td className="px-6 py-4">{client.industry}</td>
                    <td className="px-6 py-4 font-semibold text-primary-text">{client.loanAmount}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 min-w-[100px] h-2 bg-background rounded-full overflow-hidden">
                           <div className={`h-full ${client.riskScore > 85 ? 'bg-danger' : 'bg-warning'}`} style={{ width: `${client.riskScore}%` }}></div>
                        </div>
                        <Badge variant={client.riskScore > 85 ? 'danger' : 'warning'}>
                          {client.riskScore}
                        </Badge>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs">
                      <div className="flex items-center gap-1 text-danger">
                        <AlertTriangle size={14} /> {client.reason}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Button variant="ghost" size="sm" onClick={() => navigate(`/bank/customer/${client.id}`)} className="group-hover:text-primary">
                        Details <ArrowUpRight size={14} className="ml-1" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="glass-panel border-info/20">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-info/10 rounded-full text-info"><TrendingDown size={20} /></div>
            <div>
              <p className="text-sm font-semibold">Macro Portfolio impact</p>
              <p className="text-xs text-muted-text">A 5% interest rate hike would move 12 more MSMEs to 'Critical'.</p>
            </div>
          </CardContent>
        </Card>
        <Card className="glass-panel border-success/20">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="p-3 bg-success/10 rounded-full text-success"><ArrowUpRight size={20} /></div>
            <div>
              <p className="text-sm font-semibold">Recommended Mitigations</p>
              <p className="text-xs text-muted-text">Offer restructuring to 'Agriculture' sector clients before monsoon season.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
