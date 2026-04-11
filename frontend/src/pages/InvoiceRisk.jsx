import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { AlertTriangle, TrendingDown, Search, Download, RefreshCw } from 'lucide-react';
import { intelligenceAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';

const fmt = (n) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n ?? 0);

function riskLevel(status, delayDays) {
  if (status === 'overdue' || delayDays > 15) return { label: 'Critical',   variant: 'danger',   prob: 90 };
  if (delayDays > 7)                          return { label: 'High Risk',  variant: 'warning',  prob: 72 };
  if (status === 'pending')                   return { label: 'Pending',    variant: 'outline',  prob: 40 };
  return                                             { label: 'Paid',       variant: 'success',  prob: 5  };
}

function Skeleton({ className = '' }) {
  return <div className={`animate-pulse bg-white/10 rounded-lg ${className}`} />;
}

export default function InvoiceRisk() {
  const { user } = useAuth();
  const bid = user?.business_id || 1;
  const [search, setSearch] = useState('');

  const { data, loading, error, refetch } = useApi(
    () => intelligenceAPI.chat(bid, 'Show me all invoices', [], false),
    [bid]
  );

  const rows = data?.supporting_data?.rows || [];

  const filtered = rows.filter(r =>
    !search ||
    String(r.invoice_number).toLowerCase().includes(search.toLowerCase()) ||
    String(r.customer_name).toLowerCase().includes(search.toLowerCase())
  );

  // KPI aggregates
  const critical  = rows.filter(r => r.status === 'overdue' || r.delay_days > 15);
  const highRisk  = rows.filter(r => r.status === 'pending' && r.delay_days > 7);
  const paid      = rows.filter(r => r.status === 'paid');
  const totalAt   = critical.reduce((s, r) => s + parseFloat(r.invoice_amount || 0), 0);
  const avgDelay  = rows.length
    ? (rows.reduce((s, r) => s + (r.delay_days || 0), 0) / rows.length).toFixed(1)
    : 0;

  const exportCSV = () => {
    if (!rows.length) return;
    const cols = ['invoice_number','customer_name','invoice_amount','due_date','status','delay_days'];
    const csv  = [cols.join(','), ...rows.map(r => cols.map(c => r[c] ?? '').join(','))].join('\n');
    const a    = document.createElement('a');
    a.href     = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'invoices.csv';
    a.click();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Invoice Risk</h1>
          <p className="text-muted-text mt-1">Real-time invoice status and delay risk from your database.</p>
        </div>
        <Button variant="ghost" size="icon" onClick={refetch} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </Button>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="glass-panel border-danger/30">
          <CardContent className="p-5">
            <p className="text-xs font-medium text-danger mb-1">Critical / Overdue</p>
            {loading ? <Skeleton className="h-8 w-24" /> : (
              <>
                <h3 className="text-2xl font-bold">{fmt(totalAt)}</h3>
                <p className="text-xs text-muted-text mt-1">{critical.length} invoice{critical.length !== 1 ? 's' : ''}</p>
              </>
            )}
          </CardContent>
        </Card>
        <Card className="glass-panel border-warning/30">
          <CardContent className="p-5">
            <p className="text-xs font-medium text-warning mb-1">High Risk (Pending)</p>
            {loading ? <Skeleton className="h-8 w-24" /> : (
              <>
                <h3 className="text-2xl font-bold">{highRisk.length}</h3>
                <p className="text-xs text-muted-text mt-1">invoices at risk</p>
              </>
            )}
          </CardContent>
        </Card>
        <Card className="glass-panel border-success/30">
          <CardContent className="p-5">
            <p className="text-xs font-medium text-success mb-1">Paid</p>
            {loading ? <Skeleton className="h-8 w-24" /> : (
              <>
                <h3 className="text-2xl font-bold">{paid.length}</h3>
                <p className="text-xs text-muted-text mt-1">of {rows.length} total</p>
              </>
            )}
          </CardContent>
        </Card>
        <Card className="glass-panel">
          <CardContent className="p-5">
            <p className="text-xs font-medium text-muted-text mb-1">Avg Delay</p>
            {loading ? <Skeleton className="h-8 w-16" /> : (
              <>
                <h3 className="text-2xl font-bold">{avgDelay} <span className="text-base text-muted-text">days</span></h3>
                <p className="text-xs text-danger mt-1 flex items-center gap-1">
                  <TrendingDown size={12} /> across all invoices
                </p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm flex items-center gap-2">
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {/* Table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>All Invoices</CardTitle>
          <div className="flex gap-2">
            <div className="relative w-56 hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={15} />
              <Input value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Search invoice or client…" className="pl-9 h-9 border-border bg-background text-sm" />
            </div>
            <Button variant="outline" size="sm" className="gap-2" onClick={exportCSV}>
              <Download size={15} /> Export
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : filtered.length === 0 ? (
            <p className="text-center text-muted-text py-12 text-sm">No invoices found.</p>
          ) : (
            <div className="overflow-x-auto rounded-lg border border-border">
              <table className="w-full text-sm text-left">
                <thead className="bg-secondary-background/50 text-muted-text text-xs uppercase font-semibold">
                  <tr>
                    {['Invoice ID','Client','Amount','Invoice Date','Due Date','Delay Days','Status'].map(h => (
                      <th key={h} className="px-5 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filtered.map((inv, i) => {
                    const { label, variant, prob } = riskLevel(inv.status, inv.delay_days);
                    return (
                      <tr key={i} className="hover:bg-white/5 transition-colors">
                        <td className="px-5 py-3 font-medium font-mono text-xs">{inv.invoice_number}</td>
                        <td className="px-5 py-3">{inv.customer_name}</td>
                        <td className="px-5 py-3 font-semibold">{fmt(inv.invoice_amount)}</td>
                        <td className="px-5 py-3 text-muted-text">{inv.invoice_date}</td>
                        <td className="px-5 py-3 text-muted-text">{inv.due_date}</td>
                        <td className="px-5 py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 bg-background rounded-full overflow-hidden">
                              <div className={`h-full rounded-full ${prob > 80 ? 'bg-danger' : prob > 50 ? 'bg-warning' : prob > 20 ? 'bg-secondary' : 'bg-success'}`}
                                style={{ width: `${prob}%` }} />
                            </div>
                            <span className="text-xs text-muted-text">{inv.delay_days ?? 0}d</span>
                          </div>
                        </td>
                        <td className="px-5 py-3">
                          <Badge variant={variant}>{label}</Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
