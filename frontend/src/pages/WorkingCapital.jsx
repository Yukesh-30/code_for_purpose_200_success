import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { ShieldCheck, Briefcase, RefreshCw, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react';
import { intelligenceAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';

const fmt = (n) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n ?? 0);

const COLORS = ['#4F8CFF', '#6C63FF', '#16C784', '#F5A524', '#FF5C5C', '#00C2FF'];

function Skeleton({ className = '' }) {
  return <div className={`animate-pulse bg-white/10 rounded-lg ${className}`} />;
}

export default function WorkingCapital() {
  const { user } = useAuth();
  const bid = user?.business_id || 1;

  const risk     = useApi(() => intelligenceAPI.chat(bid, 'What is my current risk score?', [], false), [bid]);
  const vendors  = useApi(() => intelligenceAPI.chat(bid, 'What vendor payments are due?', [], false), [bid]);
  const loans    = useApi(() => intelligenceAPI.chat(bid, 'Show my loan EMI obligations', [], false), [bid]);
  const expenses = useApi(() => intelligenceAPI.chat(bid, 'What are my expenses this month?', [], false), [bid]);

  const riskRows    = risk.data?.supporting_data?.rows || [];
  const vendorRows  = vendors.data?.supporting_data?.rows || [];
  const loanRows    = loans.data?.supporting_data?.rows || [];
  const expenseRows = expenses.data?.supporting_data?.rows || [];

  const latestRisk  = riskRows[0] || {};
  const liqScore    = latestRisk.liquidity_score ?? 0;
  const riskBand    = latestRisk.overall_risk_band || 'unknown';
  const riskColor   = { safe: 'success', moderate: 'warning', high: 'danger', critical: 'danger' }[riskBand] || 'default';

  // Expense breakdown for pie
  const expByCategory = expenseRows.reduce((acc, r) => {
    const cat = r.expense_category || 'Other';
    acc[cat] = (acc[cat] || 0) + parseFloat(r.amount || 0);
    return acc;
  }, {});
  const pieData = Object.entries(expByCategory)
    .map(([name, value]) => ({ name, value: Math.round(value) }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 6);

  const totalVendor = vendorRows.reduce((s, r) => s + parseFloat(r.payment_amount || 0), 0);
  const totalEMI    = loanRows.reduce((s, r) => s + parseFloat(r.emi_amount || 0), 0);
  const totalExp    = expenseRows.reduce((s, r) => s + parseFloat(r.amount || 0), 0);

  const loading = risk.loading || vendors.loading || loans.loading;

  const refetchAll = () => { risk.refetch(); vendors.refetch(); loans.refetch(); expenses.refetch(); };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Working Capital</h1>
          <p className="text-muted-text mt-1">Live operational liquidity and upcoming obligations.</p>
        </div>
        <Button variant="ghost" size="icon" onClick={refetchAll} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Liquidity Score Gauge */}
        <Card className="glass-panel flex flex-col items-center justify-center p-8 text-center relative overflow-hidden">
          <div className="absolute top-4 right-4">
            {risk.loading ? <Skeleton className="h-6 w-20" /> : <Badge variant={riskColor}>{riskBand} risk</Badge>}
          </div>

          {/* Gauge visual */}
          <div className="relative w-44 h-24 mb-4 mt-6">
            <div className="absolute inset-0 border-[14px] border-border rounded-t-full border-b-0" />
            <div
              className={`absolute inset-0 border-[14px] rounded-t-full border-b-0 transition-all duration-700
                ${liqScore > 70 ? 'border-success' : liqScore > 40 ? 'border-warning' : 'border-danger'}`}
              style={{ clipPath: `polygon(0 0, ${liqScore}% 0, ${liqScore}% 100%, 0 100%)` }}
            />
            <div className="absolute bottom-[-8px] left-1/2 -translate-x-1/2 text-4xl font-bold text-primary-text">
              {risk.loading ? '…' : liqScore}
            </div>
          </div>

          <h3 className="text-lg font-semibold mt-4">Liquidity Score</h3>
          <p className="text-sm text-muted-text max-w-[200px] mt-2">
            {liqScore > 70 ? 'Healthy liquidity. You can cover upcoming obligations.' :
             liqScore > 40 ? 'Moderate risk. Monitor upcoming payments closely.' :
             'Low liquidity. Immediate action recommended.'}
          </p>

          {/* Sub-scores */}
          {!risk.loading && riskRows.length > 0 && (
            <div className="mt-4 w-full space-y-2 text-left">
              {[
                { label: 'Default Risk',    val: latestRisk.default_risk_score,    color: 'bg-danger' },
                { label: 'Overdraft Risk',  val: latestRisk.overdraft_risk_score,  color: 'bg-warning' },
                { label: 'Working Capital', val: latestRisk.working_capital_score, color: 'bg-success' },
              ].map(({ label, val, color }) => (
                <div key={label}>
                  <div className="flex justify-between text-xs mb-0.5">
                    <span className="text-muted-text">{label}</span>
                    <span className="font-medium">{val ?? '—'}</span>
                  </div>
                  <div className="h-1 bg-background rounded-full overflow-hidden">
                    <div className={`h-full ${color} rounded-full`} style={{ width: `${val || 0}%` }} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Expense Breakdown Pie */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Expense Breakdown (This Month)</CardTitle>
          </CardHeader>
          <CardContent>
            {expenses.loading ? (
              <div className="h-48 flex items-center justify-center">
                <RefreshCw size={22} className="animate-spin text-primary" />
              </div>
            ) : pieData.length === 0 ? (
              <p className="text-sm text-muted-text text-center py-8">No expense data available.</p>
            ) : (
              <div className="flex flex-col md:flex-row items-center gap-6">
                <div className="w-[180px] h-[180px] shrink-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={80}
                        paddingAngle={4} dataKey="value" stroke="none">
                        {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: 12 }}
                        formatter={(v) => [fmt(v)]}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex-1 space-y-3 w-full">
                  {pieData.map((item, i) => (
                    <div key={i} className="flex justify-between items-center text-sm">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                        <span className="text-primary-text">{item.name}</span>
                      </div>
                      <span className="font-semibold">{fmt(item.value)}</span>
                    </div>
                  ))}
                  <div className="pt-2 border-t border-border flex justify-between text-sm font-bold">
                    <span>Total</span>
                    <span>{fmt(totalExp)}</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Obligations Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Obligations</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-20 w-full" />)}
            </div>
          ) : (
            <div className="relative border-l-2 border-border ml-4 space-y-6">

              {/* Vendor payments */}
              {vendorRows.slice(0, 3).map((v, i) => (
                <div key={i} className="relative pl-6">
                  <span className="absolute -left-[11px] bg-warning rounded-full w-5 h-5 flex items-center justify-center ring-4 ring-background">
                    <Briefcase size={10} className="text-white" />
                  </span>
                  <div className="bg-secondary-background/50 border border-border rounded-xl p-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-semibold text-sm">{v.vendor_name}</span>
                      <span className="font-bold text-warning">{fmt(v.payment_amount)}</span>
                    </div>
                    <p className="text-xs text-muted-text">Due: {v.due_date} · Status: {v.status}</p>
                  </div>
                </div>
              ))}

              {/* Loan EMIs */}
              {loanRows.slice(0, 2).map((l, i) => (
                <div key={i} className="relative pl-6">
                  <span className="absolute -left-[11px] bg-danger rounded-full w-5 h-5 flex items-center justify-center ring-4 ring-background">
                    <ShieldCheck size={10} className="text-white" />
                  </span>
                  <div className="bg-secondary-background/50 border border-border rounded-xl p-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-semibold text-sm">{l.loan_type} — {l.lender_name}</span>
                      <span className="font-bold text-danger">{fmt(l.emi_amount)}</span>
                    </div>
                    <p className="text-xs text-muted-text">
                      Due: {l.due_date} · Outstanding: {fmt(l.outstanding_amount)} · Rate: {l.interest_rate}%
                    </p>
                  </div>
                </div>
              ))}

              {vendorRows.length === 0 && loanRows.length === 0 && (
                <p className="pl-6 text-sm text-muted-text">No upcoming obligations found.</p>
              )}
            </div>
          )}

          {/* Summary footer */}
          {!loading && (totalVendor > 0 || totalEMI > 0) && (
            <div className="mt-6 pt-4 border-t border-border grid grid-cols-2 gap-4">
              <div className="p-3 bg-secondary-background/50 rounded-xl">
                <p className="text-xs text-muted-text">Total Vendor Dues</p>
                <p className="text-lg font-bold text-warning mt-1">{fmt(totalVendor)}</p>
              </div>
              <div className="p-3 bg-secondary-background/50 rounded-xl">
                <p className="text-xs text-muted-text">Total EMI Obligations</p>
                <p className="text-lg font-bold text-danger mt-1">{fmt(totalEMI)}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
