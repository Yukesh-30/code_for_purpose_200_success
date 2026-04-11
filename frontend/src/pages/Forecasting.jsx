import React, { useState } from 'react';
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Sparkles, Calendar, TrendingUp, TrendingDown, RefreshCw, AlertTriangle } from 'lucide-react';
import { intelligenceAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';

const fmt = (n) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n ?? 0);

const HORIZONS = [
  { label: '30 Days', days: 30 },
  { label: '60 Days', days: 60 },
  { label: '90 Days', days: 90 },
];

export default function Forecasting() {
  const { user } = useAuth();
  const businessId = user?.business_id || 1;
  const [horizon, setHorizon] = useState(30);

  const { data, loading, error, refetch } = useApi(
    () => intelligenceAPI.forecast(businessId, horizon),
    [businessId, horizon]
  );

  const rows   = data?.supporting_data?.rows || [];
  const analysis = data ? (() => {
    // parse analysis from answer/explanation
    const a = {};
    if (data.answer) {
      const balMatch = data.answer.match(/([\d,.-]+)/);
      if (balMatch) a.ending_balance = parseFloat(balMatch[1].replace(/,/g, ''));
    }
    return a;
  })() : {};

  // Build chart data
  const chartData = rows.map(r => ({
    date: r.forecast_date?.slice(5) || r.date,
    inflow:   parseFloat(r.predicted_inflow   || 0),
    outflow:  parseFloat(r.predicted_outflow  || 0),
    balance:  parseFloat(r.predicted_closing_balance || 0),
    net:      parseFloat(r.predicted_net_cashflow || 0),
  }));

  const lastRow   = rows[rows.length - 1];
  const firstRow  = rows[0];
  const endBal    = parseFloat(lastRow?.predicted_closing_balance || 0);
  const startBal  = parseFloat(firstRow?.predicted_closing_balance || 0);
  const balChange = endBal - startBal;
  const avgNet    = rows.length ? rows.reduce((s, r) => s + parseFloat(r.predicted_net_cashflow || 0), 0) / rows.length : 0;
  const avgIn     = rows.length ? rows.reduce((s, r) => s + parseFloat(r.predicted_inflow || 0), 0) / rows.length : 0;
  const avgOut    = rows.length ? rows.reduce((s, r) => s + parseFloat(r.predicted_outflow || 0), 0) / rows.length : 0;
  const negDays   = rows.filter(r => parseFloat(r.predicted_net_cashflow || 0) < 0).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Liquidity Forecast</h1>
          <p className="text-muted-text mt-1">AI-powered cashflow projection from your real transaction history.</p>
        </div>
        <div className="flex items-center gap-2">
          {HORIZONS.map(h => (
            <Button key={h.days} variant={horizon === h.days ? 'default' : 'outline'}
              onClick={() => setHorizon(h.days)} className="gap-2">
              <Calendar size={14} /> {h.label}
            </Button>
          ))}
          <Button variant="ghost" size="icon" onClick={refetch} disabled={loading}>
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          </Button>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="glass-panel">
          <CardContent className="p-5">
            <p className="text-xs text-muted-text mb-1">Projected End Balance</p>
            <p className="text-2xl font-bold text-primary-text">{loading ? '…' : fmt(endBal)}</p>
            <p className={`text-xs mt-1 flex items-center gap-1 ${balChange >= 0 ? 'text-success' : 'text-danger'}`}>
              {balChange >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
              {loading ? '…' : fmt(Math.abs(balChange))} over {horizon} days
            </p>
          </CardContent>
        </Card>
        <Card className="glass-panel">
          <CardContent className="p-5">
            <p className="text-xs text-muted-text mb-1">Avg Daily Inflow</p>
            <p className="text-2xl font-bold text-success">{loading ? '…' : fmt(avgIn)}</p>
          </CardContent>
        </Card>
        <Card className="glass-panel">
          <CardContent className="p-5">
            <p className="text-xs text-muted-text mb-1">Avg Daily Outflow</p>
            <p className="text-2xl font-bold text-danger">{loading ? '…' : fmt(avgOut)}</p>
          </CardContent>
        </Card>
        <Card className={`glass-panel ${negDays > 5 ? 'border-danger/40' : 'border-success/30'}`}>
          <CardContent className="p-5">
            <p className="text-xs text-muted-text mb-1">Negative Cash Days</p>
            <p className={`text-2xl font-bold ${negDays > 5 ? 'text-danger' : 'text-success'}`}>
              {loading ? '…' : negDays}
            </p>
            <p className="text-xs text-muted-text mt-1">out of {horizon} days</p>
          </CardContent>
        </Card>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-xl bg-danger/10 border border-danger/30 text-danger text-sm flex items-center gap-2">
          <AlertTriangle size={16} /> {error}
        </div>
      )}

      {/* Main chart */}
      <Card className="glass-panel">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div>
            <CardTitle>Cash Flow Projection — Next {horizon} Days</CardTitle>
            <p className="text-sm text-muted-text mt-1">
              {data?.explanation || 'Rolling-average baseline from your transaction history.'}
            </p>
          </div>
          {data?.status && <Badge variant={data.status === 'success' ? 'success' : 'warning'}>{data.status}</Badge>}
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="h-[380px] flex items-center justify-center">
              <div className="flex flex-col items-center gap-3 text-muted-text">
                <RefreshCw size={28} className="animate-spin text-primary" />
                <span className="text-sm">Querying {horizon}-day forecast…</span>
              </div>
            </div>
          ) : chartData.length === 0 ? (
            <div className="h-[380px] flex items-center justify-center text-muted-text text-sm">
              No forecast data available. Upload more transaction history.
            </div>
          ) : (
            <div className="h-[380px] w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="balGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#4F8CFF" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#4F8CFF" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 11 }} dy={8} minTickGap={20} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 11 }} dx={-8} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: 12 }}
                    formatter={(v, name) => [fmt(v), name]}
                  />
                  <Legend wrapperStyle={{ fontSize: 12, paddingTop: 12 }} />
                  <Area type="monotone" dataKey="balance" stroke="#4F8CFF" strokeWidth={2.5} fill="url(#balGrad)" name="Closing Balance" />
                  <Line type="monotone" dataKey="inflow"  stroke="#16C784" strokeWidth={1.5} dot={false} name="Inflow" />
                  <Line type="monotone" dataKey="outflow" stroke="#FF5C5C" strokeWidth={1.5} dot={false} name="Outflow" />
                  <Line type="monotone" dataKey={() => 0} stroke="#FF5C5C" strokeWidth={1} strokeDasharray="4 4" dot={false} name="Zero Line" legendType="none" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* AI summary */}
          {data?.answer && !loading && (
            <div className="mt-5 p-4 bg-secondary-background border border-border rounded-xl flex items-start gap-3">
              <Sparkles size={16} className="text-secondary mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-semibold text-primary-text">AI Summary</p>
                <p className="text-sm text-muted-text mt-1">{data.answer}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
