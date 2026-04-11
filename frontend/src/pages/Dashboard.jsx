import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Wallet, AlertTriangle, TrendingUp, TrendingDown, Zap, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';

const fmt = (n) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n ?? 0);

function Skeleton({ className = '' }) {
  return <div className={`animate-pulse bg-white/10 rounded-lg ${className}`} />;
}

export default function Dashboard() {
  const { user } = useAuth();
  const bid = user?.business_id || 1;

  const { data, loading, error, refetch } = useApi(
    () => fetch(`/stats?business_id=${bid}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    }).then(r => r.json()),
    [bid]
  );

  const balance   = data?.balance ?? 0;
  const cf        = data?.cashflow ?? {};
  const risk      = data?.risk_score ?? {};
  const invoices  = data?.invoices ?? [];
  const overdue   = invoices.filter(i => i.status === 'overdue');
  const pending   = invoices.filter(i => i.status === 'pending');

  const riskBand  = risk.overall_risk_band || 'unknown';
  const riskColor = { safe: 'success', moderate: 'warning', high: 'danger', critical: 'danger' }[riskBand] || 'default';
  const liqScore  = risk.liquidity_score ?? '—';

  const chartData = (cf.history || []).map(h => ({
    date:    String(h.date || '').slice(5),
    inflow:  h.inflow,
    outflow: h.outflow,
    net:     h.net,
  }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
          <p className="text-muted-text mt-1">Live financial intelligence for your business.</p>
        </div>
        <Button onClick={refetch} variant="outline" className="gap-2" disabled={loading}>
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} /> Refresh
        </Button>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm flex items-center gap-2">
          <AlertTriangle size={15} /> {error}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
        <Card className="glass-panel">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-text mb-1">Closing Balance</p>
                {loading ? <Skeleton className="h-9 w-32 mt-1" /> :
                  <h3 className="text-3xl font-bold text-primary-text">{fmt(balance)}</h3>}
              </div>
              <div className="p-2 bg-secondary-background rounded-lg"><Wallet className="text-primary" size={22} /></div>
            </div>
          </CardContent>
        </Card>

        <Card className={`glass-panel ${(cf.net ?? 0) < 0 ? 'border-danger/40' : 'border-success/30'}`}>
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-text mb-1">Net Cashflow (30d)</p>
                {loading ? <Skeleton className="h-9 w-32 mt-1" /> :
                  <h3 className={`text-3xl font-bold ${(cf.net ?? 0) >= 0 ? 'text-success' : 'text-danger'}`}>
                    {fmt(cf.net)}
                  </h3>}
              </div>
              <div className="p-2 bg-secondary-background rounded-lg">
                {(cf.net ?? 0) >= 0
                  ? <TrendingUp className="text-success" size={22} />
                  : <TrendingDown className="text-danger" size={22} />}
              </div>
            </div>
            {!loading && (
              <div className="mt-2 flex gap-3 text-xs text-muted-text">
                <span className="text-success">↑ {fmt(cf.inflow)}</span>
                <span className="text-danger">↓ {fmt(cf.outflow)}</span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="glass-panel">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-text mb-1">Invoice Status</p>
                {loading ? <Skeleton className="h-9 w-24 mt-1" /> :
                  <h3 className="text-3xl font-bold text-warning">{overdue.length} Overdue</h3>}
              </div>
              <div className="p-2 bg-secondary-background rounded-lg">
                <AlertTriangle className="text-warning" size={22} />
              </div>
            </div>
            {!loading && (
              <p className="text-xs text-muted-text mt-2">{pending.length} pending · {invoices.length} total</p>
            )}
          </CardContent>
        </Card>

        <Card className="glass-panel">
          <CardContent className="p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-text mb-1">Liquidity Score</p>
                {loading ? <Skeleton className="h-9 w-20 mt-1" /> :
                  <h3 className="text-3xl font-bold text-primary-text">
                    {liqScore}<span className="text-lg text-muted-text">/100</span>
                  </h3>}
              </div>
              <div className="p-2 bg-secondary-background rounded-lg">
                <TrendingUp className="text-info" size={22} />
              </div>
            </div>
            {!loading && <div className="mt-2"><Badge variant={riskColor}>{riskBand} risk</Badge></div>}
          </CardContent>
        </Card>
      </div>

      {/* Charts + Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Cashflow chart */}
        <Card className="col-span-1 lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle>Cashflow — Last 30 Days</CardTitle>
              <p className="text-sm text-muted-text mt-1">Daily inflow vs outflow from bank transactions.</p>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="h-[280px] flex items-center justify-center">
                <RefreshCw size={24} className="animate-spin text-primary" />
              </div>
            ) : chartData.length === 0 ? (
              <div className="h-[280px] flex items-center justify-center text-muted-text text-sm">
                No transaction data for this period.
              </div>
            ) : (
              <div className="h-[280px] w-full mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="inflowGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#16C784" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#16C784" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="outflowGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#FF5C5C" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="#FF5C5C" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="date" axisLine={false} tickLine={false}
                      tick={{ fill: '#7C879F', fontSize: 11 }} dy={8} minTickGap={15} />
                    <YAxis axisLine={false} tickLine={false}
                      tick={{ fill: '#7C879F', fontSize: 11 }} dx={-8}
                      tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: 12 }}
                      formatter={v => [fmt(v)]}
                    />
                    <Area type="monotone" dataKey="inflow"  stroke="#16C784" strokeWidth={2} fill="url(#inflowGrad)"  name="Inflow" />
                    <Area type="monotone" dataKey="outflow" stroke="#FF5C5C" strokeWidth={2} fill="url(#outflowGrad)" name="Outflow" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right column */}
        <div className="space-y-5">

          {/* Risk Scores */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Risk Scores</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {loading ? <Skeleton className="h-24 w-full" /> : (
                <>
                  {[
                    { label: 'Liquidity',      val: risk.liquidity_score,       color: 'bg-primary' },
                    { label: 'Default Risk',   val: risk.default_risk_score,    color: 'bg-danger' },
                    { label: 'Overdraft Risk', val: risk.overdraft_risk_score,  color: 'bg-warning' },
                    { label: 'Working Cap.',   val: risk.working_capital_score, color: 'bg-success' },
                  ].map(({ label, val, color }) => (
                    <div key={label}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-muted-text">{label}</span>
                        <span className="font-semibold">{val ?? '—'}</span>
                      </div>
                      <div className="h-1.5 bg-background rounded-full overflow-hidden">
                        <div className={`h-full ${color} rounded-full`} style={{ width: `${val || 0}%` }} />
                      </div>
                    </div>
                  ))}
                  <div className="pt-1 flex justify-between items-center">
                    <span className="text-xs text-muted-text">Overall</span>
                    <Badge variant={riskColor}>{riskBand}</Badge>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* AI Insight */}
          <Card className="border-info/30">
            <CardHeader className="pb-3">
              <CardTitle className="text-info flex items-center gap-2 text-base">
                <Zap size={18} /> AI Insight
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? <Skeleton className="h-16 w-full" /> : (
                <div className="space-y-2 text-sm">
                  {(cf.net ?? 0) < 0 && (
                    <p className="text-danger flex items-start gap-1">
                      <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                      Negative cashflow of {fmt(Math.abs(cf.net))} this period. Review vendor expenses.
                    </p>
                  )}
                  {overdue.length > 0 && (
                    <p className="text-warning flex items-start gap-1">
                      <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                      {overdue.length} overdue invoice{overdue.length > 1 ? 's' : ''} — prioritise collection.
                    </p>
                  )}
                  {(cf.net ?? 0) >= 0 && overdue.length === 0 && (
                    <p className="text-success">Cashflow is positive and invoices are on track.</p>
                  )}
                  {(data?.recommendations ?? []).slice(0, 1).map((r, i) => (
                    <p key={i} className="text-muted-text border-t border-border pt-2 mt-2">
                      💡 <strong>{r.product}</strong> — {r.reason?.slice(0, 80)}
                    </p>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Overdue invoices */}
          {!loading && overdue.length > 0 && (
            <Card className="border-danger/30">
              <CardHeader className="pb-3">
                <CardTitle className="text-base text-danger flex items-center gap-2">
                  <AlertTriangle size={16} /> Overdue Invoices
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {overdue.slice(0, 3).map((inv, i) => (
                  <div key={i} className="flex justify-between items-center text-sm p-2 bg-secondary-background/50 rounded-lg">
                    <div>
                      <p className="font-medium text-xs">{inv.invoice_number}</p>
                      <p className="text-xs text-muted-text">{inv.customer_name}</p>
                    </div>
                    <span className="font-bold text-danger text-xs">{fmt(inv.amount)}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
