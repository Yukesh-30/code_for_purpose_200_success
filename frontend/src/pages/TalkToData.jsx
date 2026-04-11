import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Sparkles, Database, Terminal, Download, MessageSquare,
  TrendingUp, AlertTriangle, RefreshCw, ChevronDown, CheckCircle2,
  BarChart3, Zap, ShieldAlert, ArrowRight, TrendingDown, Lightbulb
} from 'lucide-react';
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area,
  PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid,
  Tooltip as RTooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { intelligenceAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

const SUGGESTED = [
  'What was my cashflow last month?',
  'Why did my cashflow decline over the last 2 months compared to the previous 2 months, which vendors and expense categories contributed most, and will I run out of cash in 30 days? What are top 3 actions?',
  'Forecast cashflow for next 30 days',
  'Find unusual transactions in last 90 days',
  'Show me pending invoices',
  'What is my current risk score?',
  'What vendor payments are due?',
];

const fmt = (n) => {
  if (n == null) return '—';
  const num = parseFloat(n);
  if (isNaN(num)) return n;
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(num);
};

// ── Recommendations widget ────────────────────────────────────────────────────
function RecommendationsWidget({ recs }) {
  if (!recs?.length) return null;
  const impactColor = { high: 'text-danger', medium: 'text-warning', low: 'text-success' };
  return (
    <div className="bg-secondary-background border border-border rounded-2xl px-4 py-3 space-y-3">
      <div className="flex items-center gap-2 text-sm font-semibold text-primary-text">
        <Lightbulb size={15} className="text-warning" /> Top {recs.length} Recommended Actions
      </div>
      {recs.map((r, i) => (
        <div key={i} className="flex items-start gap-3 p-3 bg-background/50 rounded-xl border border-border">
          <span className={`text-xs font-bold mt-0.5 w-5 h-5 rounded-full flex items-center justify-center shrink-0
            ${r.impact === 'high' ? 'bg-danger/20 text-danger' : r.impact === 'medium' ? 'bg-warning/20 text-warning' : 'bg-success/20 text-success'}`}>
            {i + 1}
          </span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-primary-text">{r.action}</p>
            <p className="text-xs text-muted-text mt-0.5 leading-relaxed">{r.reason}</p>
          </div>
          <Badge variant={r.impact === 'high' ? 'danger' : r.impact === 'medium' ? 'warning' : 'success'}
            className="shrink-0 text-xs">{r.impact}</Badge>
        </div>
      ))}
    </div>
  );
}

// ── Driver analysis widget ────────────────────────────────────────────────────
function DriverWidget({ driver }) {
  if (!driver || !driver.top_vendors?.length) return null;
  return (
    <div className="bg-secondary-background border border-border rounded-2xl px-4 py-3 space-y-3">
      <div className="flex items-center gap-2 text-sm font-semibold text-primary-text">
        <BarChart3 size={15} className="text-primary" /> Cashflow Drivers
      </div>
      {driver.top_vendors?.length > 0 && (
        <div>
          <p className="text-xs text-muted-text mb-2 font-medium uppercase tracking-wide">Top Vendors by Spend</p>
          {driver.top_vendors.slice(0, 3).map((v, i) => (
            <div key={i} className="flex items-center gap-2 mb-1.5">
              <span className="text-xs text-muted-text w-4">{i+1}.</span>
              <span className="text-xs text-primary-text flex-1 truncate">{v.vendor}</span>
              <span className="text-xs font-semibold text-danger">{fmt(v.spend)}</span>
              <span className="text-xs text-muted-text w-10 text-right">{v.pct?.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      )}
      {driver.top_categories?.length > 0 && (
        <div>
          <p className="text-xs text-muted-text mb-2 font-medium uppercase tracking-wide">Top Expense Categories</p>
          {driver.top_categories.slice(0, 3).map((c, i) => (
            <div key={i} className="flex items-center gap-2 mb-1.5">
              <span className="text-xs text-muted-text w-4">{i+1}.</span>
              <span className="text-xs text-primary-text flex-1 truncate">{c.category}</span>
              <span className="text-xs font-semibold text-warning">{fmt(c.spent)}</span>
              <span className="text-xs text-muted-text w-10 text-right">{c.pct?.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      )}
      {driver.net_pct_change !== undefined && (
        <div className={`flex items-center gap-2 text-xs p-2 rounded-lg ${driver.net_change < 0 ? 'bg-danger/10 text-danger' : 'bg-success/10 text-success'}`}>
          {driver.net_change < 0 ? <TrendingDown size={13} /> : <TrendingUp size={13} />}
          Cashflow {driver.direction} by {fmt(driver.net_change)} ({Math.abs(driver.net_pct_change).toFixed(1)}%) vs previous period
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }) {
  const map = {
    success: 'success', needs_clarification: 'warning',
    insufficient_data: 'warning', blocked: 'danger',
    error: 'danger', out_of_scope: 'outline',
  };
  return <Badge variant={map[status] || 'default'}>{status?.replace(/_/g, ' ')}</Badge>;
}

const COLORS = ['#4F8CFF', '#16C784', '#FF5C5C', '#F5A524', '#6C63FF', '#00C2FF', '#FF9F43', '#EE5A24'];

function ChartWidget({ chart }) {
  if (!chart || chart.type === 'none' || !chart.series?.length) return null;
  const data  = chart.series.slice(0, 60);
  const yKeys = chart.y || [];

  // ── Pie chart ──────────────────────────────────────────────────────────────
  if (chart.type === 'pie') {
    const xKey = chart.x || Object.keys(data[0])[0];
    const yKey = yKeys[0] || Object.keys(data[0])[1];
    const pieData = data.map(r => ({ name: String(r[xKey] || ''), value: parseFloat(r[yKey] || 0) }));
    return (
      <div className="h-56 w-full mt-3">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={pieData} cx="50%" cy="50%" outerRadius={80} dataKey="value"
              label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}
              labelLine={false}>
              {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
            </Pie>
            <RTooltip contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: 12 }}
              formatter={v => [fmt(v)]} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // ── Area chart ─────────────────────────────────────────────────────────────
  if (chart.type === 'area') {
    return (
      <div className="h-52 w-full mt-3">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              {yKeys.map((k, i) => (
                <linearGradient key={k} id={`grad_${i}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={COLORS[i % COLORS.length]} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={COLORS[i % COLORS.length]} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey={chart.x} axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} minTickGap={20} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
            <RTooltip contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: 12 }}
              formatter={v => [fmt(v)]} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            {yKeys.map((k, i) => (
              <Area key={k} type="monotone" dataKey={k} stroke={COLORS[i % COLORS.length]}
                strokeWidth={2} fill={`url(#grad_${i})`} dot={false} />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // ── Line chart ─────────────────────────────────────────────────────────────
  if (chart.type === 'line') {
    return (
      <div className="h-52 w-full mt-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey={chart.x} axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} minTickGap={20} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
            <RTooltip contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: 12 }}
              formatter={v => [fmt(v)]} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            {yKeys.map((k, i) => (
              <Line key={k} type="monotone" dataKey={k} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // ── Bar chart ──────────────────────────────────────────────────────────────
  if (chart.type === 'bar') {
    return (
      <div className="h-48 w-full mt-3">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey={chart.x} axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
            <RTooltip contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px', fontSize: 12 }}
              formatter={v => [fmt(v)]} />
            {yKeys.map((k, i) => (
              <Bar key={k} dataKey={k} fill={COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  }

  // ── Table ──────────────────────────────────────────────────────────────────
  if (chart.type === 'table' && data.length) {
    const cols = Object.keys(data[0]).slice(0, 6);
    return (
      <div className="mt-3 overflow-x-auto rounded-lg border border-border max-h-48">
        <table className="w-full text-xs">
          <thead className="bg-secondary-background/80 text-muted-text uppercase">
            <tr>{cols.map(c => <th key={c} className="px-3 py-2 text-left">{c.replace(/_/g, ' ')}</th>)}</tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.slice(0, 10).map((row, i) => (
              <tr key={i} className="hover:bg-white/5">
                {cols.map(c => <td key={c} className="px-3 py-2 text-primary-text">{String(row[c] ?? '—').slice(0, 30)}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }
  return null;
}

function AIMessage({ msg }) {
  const [showSQL, setShowSQL] = useState(false);
  const r = msg.response;

  return (
    <div className="flex justify-start">
      <div className="max-w-[90%] space-y-2">
        {/* Main bubble */}
        <div className="bg-secondary-background border border-border rounded-2xl rounded-bl-none px-4 py-3">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={14} className="text-secondary" />
            <span className="text-xs text-muted-text font-medium">FlowSight AI</span>
            {r && <StatusBadge status={r.status} />}
            {r?.analysis_method && (
              <Badge variant="outline" className="text-[10px] ml-1 bg-primary/10 border-primary/30 text-primary">
                 <Zap size={10} className="inline mr-1" />
                 {r.analysis_method.replace(/_/g, ' ')}
              </Badge>
            )}
            {r?.confidence > 0 && (
              <span className="text-[11px] text-muted-text ml-auto font-mono bg-background border border-border px-1.5 py-0.5 rounded">
                {(r.confidence * 100).toFixed(0)}% conf
              </span>
            )}
          </div>
          <div className="text-sm leading-relaxed text-primary-text whitespace-pre-line">
            {msg.content.split(/(\*\*[^*]+\*\*)/).map((part, i) =>
              part.startsWith('**') && part.endsWith('**')
                ? <strong key={i} className="text-primary-text font-semibold">{part.slice(2,-2)}</strong>
                : part
            )}
          </div>          {r?.explanation && r.explanation !== msg.content && (
            <p className="text-xs text-muted-text mt-2 leading-relaxed">{r.explanation}</p>
          )}
        </div>

        {/* Chart */}
        {r?.chart && r.chart.type !== 'none' && (
          <div className="bg-secondary-background border border-border rounded-2xl px-4 py-3">
            <div className="flex items-center gap-2 mb-1">
              <BarChart3 size={14} className="text-primary" />
              <span className="text-xs text-muted-text">Visualization</span>
              <span className="text-xs text-muted-text ml-auto">{r.supporting_data?.row_count} rows</span>
            </div>
            <ChartWidget chart={r.chart} />
          </div>
        )}

        {/* Driver analysis */}
        {r?.driver_analysis && <DriverWidget driver={r.driver_analysis} />}

        {/* Recommendations */}
        {r?.recommendations?.length > 0 && <RecommendationsWidget recs={r.recommendations} />}

        {/* SQL toggle */}
        {r?.sql && (
          <div className="bg-secondary-background border border-border rounded-xl overflow-hidden">
            <button
              onClick={() => setShowSQL(v => !v)}
              className="w-full flex items-center gap-2 px-4 py-2 text-xs text-muted-text hover:text-primary-text transition-colors"
            >
              <Terminal size={13} />
              <span>Generated SQL</span>
              <ChevronDown size={13} className={`ml-auto transition-transform ${showSQL ? 'rotate-180' : ''}`} />
            </button>
            {showSQL && (
              <pre className="px-4 pb-3 text-xs text-success font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed">
                {r.sql}
              </pre>
            )}
          </div>
        )}

        {/* Warnings */}
        {r?.warnings?.length > 0 && (
          <div className="flex items-start gap-2 text-xs text-warning bg-warning/10 border border-warning/20 rounded-xl px-3 py-2">
            <AlertTriangle size={13} className="mt-0.5 shrink-0" />
            <span>{r.warnings.join(' • ')}</span>
          </div>
        )}

        {/* Follow-up suggestions */}
        {r?.follow_up_questions?.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {r.follow_up_questions.map((q, i) => (
              <button key={i} onClick={() => msg.onFollowUp?.(q)}
                className="text-xs bg-background border border-border hover:border-primary/50 text-muted-text hover:text-primary transition-colors px-2.5 py-1 rounded-full">
                {q}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function TalkToData() {
  const { user } = useAuth();
  const businessId = user?.business_id || 1;

  const [messages, setMessages] = useState([{
    id: 0, role: 'ai',
    content: "Hey! I'm FlowSight AI 👋\n\nI can answer questions about your business finances — cashflow, invoices, expenses, forecasts, anomalies, risk scores, and more.\n\nJust ask me anything, like you'd ask a colleague.",
    response: null,
  }]);
  const [input, setInput]       = useState('');
  const [loading, setLoading]   = useState(false);
  const [history, setHistory]   = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (text = input) => {
    const q = text.trim();
    if (!q || loading) return;
    setInput('');

    const userMsg = { id: Date.now(), role: 'user', content: q };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    // Detect intent to route to right endpoint
    const lower = q.toLowerCase();
    let response;
    try {
      if (lower.includes('forecast') || lower.includes('predict') || lower.includes('next') || lower.includes('future')) {
        const days = lower.match(/(\d+)\s*day/)?.[1];
        response = await intelligenceAPI.forecast(businessId, days ? parseInt(days) : 30);
      } else if (lower.includes('anomal') || lower.includes('unusual') || lower.includes('abnormal') || lower.includes('spike')) {
        const days = lower.match(/(\d+)\s*day/)?.[1];
        response = await intelligenceAPI.anomaly(businessId, days ? parseInt(days) : 90);
      } else {
        response = await intelligenceAPI.chat(businessId, q, history, true);
      }

      const aiContent = response.answer || 'Here is what I found.';
      const aiMsg = {
        id: Date.now() + 1, role: 'ai', content: aiContent, response,
        onFollowUp: (fq) => send(fq),
      };
      setMessages(prev => [...prev, aiMsg]);
      setHistory(prev => [
        ...prev,
        { role: 'user', content: q },
        { role: 'assistant', content: aiContent },
      ].slice(-10));
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1, role: 'ai',
        content: `Something went wrong: ${err.message}. Check that the backend is running on port 5000.`,
        response: null,
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([{
      id: 0, role: 'ai',
      content: "Chat cleared. What would you like to know about your business?",
      response: null,
    }]);
    setHistory([]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <Card className="flex flex-col h-full border-border/60 overflow-hidden">

        {/* Header */}
        <div className="px-5 py-3 border-b border-border flex items-center justify-between bg-secondary-background/30 shrink-0">
          <div className="flex items-center gap-2">
            <Sparkles className="text-secondary" size={18} />
            <h2 className="font-semibold">AI Financial Assistant</h2>
            <Badge variant="success" className="text-xs">Live</Badge>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-muted-text bg-background border border-border px-3 py-1.5 rounded-md">
              <Database size={13} /> Business #{businessId}
            </div>
            <Button variant="ghost" size="icon" onClick={clearChat} className="h-8 w-8 text-muted-text hover:text-primary-text">
              <RefreshCw size={15} />
            </Button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div key={msg.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
                {msg.role === 'user' ? (
                  <div className="flex justify-end">
                    <div className="max-w-[75%] bg-primary text-white rounded-2xl rounded-br-none px-4 py-3 text-sm">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  <AIMessage msg={msg} />
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="bg-secondary-background border border-border rounded-2xl rounded-bl-none px-4 py-3 flex items-center gap-2">
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:0.15s]" />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:0.3s]" />
                <span className="text-xs text-muted-text ml-1">Thinking…</span>
              </div>
            </motion.div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Suggested prompts — only on fresh chat */}
        {messages.length <= 1 && (
          <div className="px-5 pb-2 flex flex-wrap gap-2 shrink-0">
            {SUGGESTED.map((p, i) => (
              <button key={i} onClick={() => send(p)}
                className="text-xs bg-background border border-border hover:border-primary/50 text-muted-text hover:text-primary transition-colors px-3 py-1.5 rounded-full">
                {p}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="px-5 py-3 border-t border-border bg-secondary-background/30 shrink-0">
          <div className="relative flex items-center">
            <Input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
              placeholder="Ask anything about your business finances…"
              disabled={loading}
              className="pr-12 h-12 rounded-xl bg-background border-border focus-visible:ring-primary"
            />
            <Button
              size="icon"
              disabled={loading || !input.trim()}
              onClick={() => send()}
              className="absolute right-1 h-10 w-10 rounded-lg bg-primary hover:bg-primary/90 disabled:opacity-40"
            >
              {loading ? <RefreshCw size={16} className="animate-spin" /> : <Send size={16} />}
            </Button>
          </div>
          <p className="text-xs text-muted-text mt-1.5 text-center">
            All answers come from your real data — nothing is made up
          </p>
        </div>
      </Card>
    </div>
  );
}
