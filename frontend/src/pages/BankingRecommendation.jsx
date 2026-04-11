import React from 'react';
import { Card, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { CheckCircle2, Zap, ArrowRight, Wallet, TrendingUp, RefreshCw, AlertTriangle, ShieldCheck, CreditCard } from 'lucide-react';
import { intelligenceAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';

const fmt = (n) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n ?? 0);

function Skeleton({ className = '' }) {
  return <div className={`animate-pulse bg-white/10 rounded-lg ${className}`} />;
}

// Map DB product names to icons + colors
const PRODUCT_META = {
  'Invoice Financing':       { icon: Wallet,      color: 'primary', benefits: ['Funds within 24hrs','No collateral required','Protects against delay risk'] },
  'Overdraft Facility':      { icon: CreditCard,  color: 'warning', benefits: ['Instant access to funds','Pay interest only on usage','Revolving credit line'] },
  'Supply Chain Finance':    { icon: TrendingUp,  color: 'info',    benefits: ['Extend payment terms','Strengthen vendor relations','Improve working capital'] },
  'Working Capital Loan':    { icon: ShieldCheck, color: 'success', benefits: ['Fixed repayment schedule','Competitive interest rates','Builds business credit'] },
  'Term Loan':               { icon: TrendingUp,  color: 'secondary', benefits: ['Long-term financing','Fixed EMI','Asset-backed options available'] },
};

function getProductMeta(name) {
  for (const [key, val] of Object.entries(PRODUCT_META)) {
    if (name?.toLowerCase().includes(key.toLowerCase())) return { ...val, name: key };
  }
  return { icon: Zap, color: 'primary', benefits: ['Tailored for your business','AI-matched product','Fast approval process'], name };
}

export default function BankingRecommendation() {
  const { user } = useAuth();
  const bid = user?.business_id || 1;

  const recs    = useApi(() => intelligenceAPI.chat(bid, 'Suggest the best banking product for me', [], false), [bid]);
  const risk    = useApi(() => intelligenceAPI.chat(bid, 'What is my current risk score?', [], false), [bid]);
  const forecast = useApi(() => intelligenceAPI.forecast(bid, 30), [bid]);

  // Pull recommendations from DB via /chat → banking_product_recommendations table
  const recRows = recs.data?.supporting_data?.rows || [];

  // Fallback: derive from risk + forecast if no DB recs
  const riskRows  = risk.data?.supporting_data?.rows || [];
  const latestRisk = riskRows[0] || {};
  const fcRows    = forecast.data?.supporting_data?.rows || [];
  const negDays   = fcRows.filter(r => parseFloat(r.predicted_net_cashflow || 0) < 0).length;

  const loading = recs.loading || risk.loading || forecast.loading;

  // Build display products — prefer DB rows, fallback to derived
  const products = recRows.length > 0
    ? recRows.map((r, i) => ({
        name:       r.recommended_product,
        description: r.reason,
        confidence: parseFloat(r.confidence_score || 75),
        recommended: i === 0,
        ...getProductMeta(r.recommended_product),
      }))
    : [
        negDays > 5 && {
          name: 'Invoice Financing', description: `Your forecast shows ${negDays} negative cashflow days. Invoice financing can bridge the gap immediately.`,
          confidence: 88, recommended: true, ...getProductMeta('Invoice Financing'),
        },
        (latestRisk.overdraft_risk_score > 40) && {
          name: 'Overdraft Facility', description: `Overdraft risk score is ${latestRisk.overdraft_risk_score}. A pre-approved overdraft line provides a safety net.`,
          confidence: 75, recommended: false, ...getProductMeta('Overdraft Facility'),
        },
        {
          name: 'Working Capital Loan', description: 'Flexible working capital to manage day-to-day operational expenses and vendor payments.',
          confidence: 65, recommended: false, ...getProductMeta('Working Capital Loan'),
        },
      ].filter(Boolean);

  const refetchAll = () => { recs.refetch(); risk.refetch(); forecast.refetch(); };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Banking Matching</h1>
          <p className="text-muted-text mt-1">AI-recommended financial products based on your live risk profile and forecast.</p>
        </div>
        <Button variant="ghost" size="icon" onClick={refetchAll} disabled={loading}>
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </Button>
      </div>

      {/* Context banner */}
      <div className="p-5 rounded-2xl glass-panel border border-border bg-gradient-to-r from-primary/10 to-transparent flex items-start gap-4">
        <div className="p-3 bg-primary/20 text-primary rounded-xl shrink-0"><Zap size={22} /></div>
        <div className="flex-1">
          <h3 className="font-semibold text-primary-text">Why these recommendations?</h3>
          {loading ? <Skeleton className="h-4 w-3/4 mt-2" /> : (
            <p className="text-sm text-secondary-text mt-1">
              {negDays > 0
                ? <>Your forecast shows <strong className="text-danger">{negDays} negative cashflow days</strong> ahead. {' '}</>
                : 'Your cashflow looks stable. '}
              {latestRisk.overall_risk_band
                ? <>Risk band is <strong className={latestRisk.overall_risk_band === 'safe' ? 'text-success' : 'text-warning'}>{latestRisk.overall_risk_band}</strong>. </>
                : ''}
              Applying today ensures funds clear before obligations are due.
            </p>
          )}
        </div>
        {!loading && latestRisk.overall_risk_band && (
          <Badge variant={{ safe: 'success', moderate: 'warning', high: 'danger', critical: 'danger' }[latestRisk.overall_risk_band] || 'default'}>
            {latestRisk.overall_risk_band} risk
          </Badge>
        )}
      </div>

      {/* Product cards */}
      {loading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => <Skeleton key={i} className="h-72 w-full rounded-2xl" />)}
        </div>
      ) : products.length === 0 ? (
        <div className="p-8 text-center text-muted-text text-sm border border-border rounded-2xl">
          No recommendations available. Upload more financial data to get personalised suggestions.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {products.map((p, i) => {
            const Icon = p.icon || Zap;
            return (
              <Card key={i} className={`relative overflow-hidden transition-all ${p.recommended ? 'ring-2 ring-primary border-transparent' : 'border-border hover:border-primary/30'}`}>
                {p.recommended && (
                  <div className="absolute top-0 right-0 bg-primary text-white text-xs font-bold px-3 py-1 rounded-bl-xl">
                    Top Match
                  </div>
                )}
                <CardContent className="p-7">
                  <div className="flex items-start gap-4 mb-5">
                    <div className={`p-3.5 rounded-2xl bg-${p.color}/10 text-${p.color} shrink-0`}>
                      <Icon size={28} />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-primary-text">{p.name}</h2>
                      <p className="text-sm text-muted-text mt-1 leading-relaxed">{p.description}</p>
                    </div>
                  </div>

                  <div className="space-y-2.5 mb-6">
                    {(p.benefits || []).map((b, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-secondary-text">
                        <CheckCircle2 className="text-success shrink-0" size={15} /> {b}
                      </div>
                    ))}
                  </div>

                  <div className="pt-5 border-t border-border flex items-center justify-between">
                    <div>
                      <p className="text-xs text-muted-text mb-1">Pre-approval Confidence</p>
                      <div className="flex items-center gap-3">
                        <span className="text-2xl font-bold">{Math.round(p.confidence)}%</span>
                        <div className="w-20 h-2 bg-background rounded-full overflow-hidden">
                          <div className="h-full bg-success rounded-full transition-all duration-700"
                            style={{ width: `${p.confidence}%` }} />
                        </div>
                      </div>
                    </div>
                    <Button className="gap-2">Apply Now <ArrowRight size={15} /></Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Risk detail footer */}
      {!risk.loading && riskRows.length > 0 && (
        <Card className="glass-panel">
          <CardContent className="p-5">
            <h4 className="font-semibold text-sm mb-4 flex items-center gap-2">
              <AlertTriangle size={15} className="text-warning" /> Your Risk Profile (Latest)
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Liquidity Score',    val: latestRisk.liquidity_score,       color: 'text-primary' },
                { label: 'Default Risk',       val: latestRisk.default_risk_score,    color: 'text-danger' },
                { label: 'Overdraft Risk',     val: latestRisk.overdraft_risk_score,  color: 'text-warning' },
                { label: 'Working Capital',    val: latestRisk.working_capital_score, color: 'text-success' },
              ].map(({ label, val, color }) => (
                <div key={label} className="p-3 bg-secondary-background/50 rounded-xl text-center">
                  <p className="text-xs text-muted-text mb-1">{label}</p>
                  <p className={`text-2xl font-bold ${color}`}>{val ?? '—'}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
