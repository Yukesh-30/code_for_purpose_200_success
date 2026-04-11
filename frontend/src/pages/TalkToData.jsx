import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Sparkles,
  Database,
  Terminal,
  Download,
  Bookmark,
  MessageSquare,
  TrendingUp,
  Plus,
  History,
  ChevronRight,
  AlertCircle,
  ShieldAlert,
  Briefcase,
  BarChart3,
  Search,
  Loader2,
  Menu,
  X,
  Layers,
  Layout
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, LineChart, Line, AreaChart, Area, PieChart, Pie, Cell } from 'recharts';
import { useAuth } from '../context/AuthContext';

const COLORS = ['#4F8CFF', '#6C63FF', '#16C784', '#F5A524', '#FF5C5C', '#00C2FF'];

const promptCategories = [
  {
    title: "Financial Forecasting",
    icon: <TrendingUp className="text-secondary" size={20} />,
    prompts: [
      "Will I face a cash shortage next month?",
      "Compare March and April cash flow."
    ]
  },
  {
    title: "Risk & Strategy",
    icon: <ShieldAlert className="text-success" size={20} />,
    prompts: [
      "Which invoices are most likely to be delayed?",
      "Why did my working capital score reduce?"
    ]
  },
  {
    title: "Banking Products",
    icon: <Briefcase className="text-warning" size={20} />,
    prompts: [
      "Suggest the best banking product for me."
    ]
  }
];

export default function TalkToData() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputVal, setInputVal] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingSessions, setIsLoadingSessions] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [isLanding, setIsLanding] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [lastResponse, setLastResponse] = useState(null);
  const chatContainerRef = useRef(null);

  // Fetch sessions on mount
  useEffect(() => {
    fetchSessions();
  }, [user]);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const fetchSessions = async () => {
    if (!user?.token) return;
    setIsLoadingSessions(true);
    try {
      const resp = await fetch('http://localhost:5000/chat/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({ business_id: 1 })
      });
      const data = await resp.json();
      if (data.sessions) setSessions(data.sessions);
    } catch (err) {
      console.error("Failed to fetch sessions", err);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const startNewChat = async () => {
    if (!user?.token) return;
    setIsLoading(true);
    try {
      const resp = await fetch('http://localhost:5000/chat/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({ business_id: 1, session_name: `Analysis ${new Date().toLocaleDateString()}` })
      });
      const data = await resp.json();
      if (data.session_id) {
        setCurrentSessionId(data.session_id);
        setMessages([]);
        setIsLanding(false);
        setLastResponse(null);
        setSidebarOpen(false);
        fetchSessions();
        return data.session_id;
      }
    } catch (err) {
      console.error("Failed to start chat", err);
    } finally {
      setIsLoading(false);
    }
    return null;
  };

  const loadSession = async (sessionId) => {
    if (!user?.token) return;
    try {
      setCurrentSessionId(sessionId);
      setIsLanding(false);
      setIsLoadingHistory(true);
      setSidebarOpen(false);
      const resp = await fetch('http://localhost:5000/chat/history', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({ session_id: sessionId })
      });
      const data = await resp.json();
      if (data.messages) {
        setMessages(data.messages.map(m => ({
          role: m.role,
          content: m.text
        })));
      }
    } catch (err) {
      console.error("Failed to load history", err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleSend = async (text = inputVal, sessionId = currentSessionId) => {
    if (!text.trim() || !sessionId || !user?.token) return;

    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInputVal('');
    setIsLoading(true);

    try {
      const resp = await fetch('http://localhost:5000/chat/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({
          session_id: sessionId,
          query: text
        })
      });
      const data = await resp.json();

      if (data.error) {
        setMessages(prev => [...prev, { role: 'ai', content: `Error: ${data.error}` }]);
      } else {
        setMessages(prev => [...prev, {
          role: 'ai',
          content: data.explanation || data.insight?.answer
        }]);
        setLastResponse(data);
      }
    } catch (err) {
      console.error("Chat error", err);
      setMessages(prev => [...prev, { role: 'ai', content: "Sorry, I encountered an error connecting to the intelligence engine." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderChart = () => {
    if (!lastResponse?.data || lastResponse.data.length === 0) return null;
    const chartData = lastResponse.data.slice(0, 15);
    const keys = Object.keys(chartData[0]).filter(k => typeof chartData[0][k] === 'number');
    const categoryKey = Object.keys(chartData[0]).find(k => typeof chartData[0][k] === 'string') || 'id';
    const chartType = lastResponse.insight?.chart_type || 'bar';

    if (chartType === 'pie') {
      return (
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={chartData} cx="50%" cy="50%" outerRadius={60} fill="#8884d8" dataKey={keys[0]} nameKey={categoryKey} label>
              {chartData.map((e, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
            </Pie>
            <RechartsTooltip />
          </PieChart>
        </ResponsiveContainer>
      );
    }

    if (chartType === 'line' || chartType === 'area') {
      const ChartComponent = chartType === 'line' ? LineChart : AreaChart;
      const DataComponent = chartType === 'line' ? Line : Area;
      return (
        <ResponsiveContainer width="100%" height="100%">
          <ChartComponent data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey={categoryKey} hide />
            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} />
            <RechartsTooltip contentStyle={{ backgroundColor: '#121A2F', borderRadius: '8px', border: 'none' }} />
            {keys.map((key, i) => (
              <DataComponent key={key} type="monotone" dataKey={key} stroke={COLORS[i % COLORS.length]} fill={chartType === 'area' ? COLORS[i % COLORS.length] : 'none'} fillOpacity={0.3} strokeWidth={2} />
            ))}
          </ChartComponent>
        </ResponsiveContainer>
      );
    }

    return (
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey={categoryKey} hide />
          <YAxis axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} />
          <RechartsTooltip contentStyle={{ backgroundColor: '#121A2F', borderRadius: '8px', border: 'none' }} />
          {keys.map((key, i) => <Bar key={key} dataKey={key} fill={COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} />)}
        </BarChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="relative flex flex-col h-[calc(100vh-6rem)] overflow-hidden theme-gradient">

      {/* Decorative background elements */}
      <div className="bg-blob bg-primary left-[-10%] top-[-10%] opacity-10"></div>
      <div className="bg-blob bg-secondary right-[-10%] top-[40%] opacity-10 animation-delay-2000"></div>
      <div className="bg-blob bg-success left-[20%] bottom-[-10%] opacity-10 animation-delay-4000"></div>

      {/* Floating Sidebar Trigger */}
      <div className="absolute top-4 left-4 z-20 flex gap-2">
        <Button
          variant="outline"
          size="icon"
          className="bg-secondary-background/80 backdrop-blur-md border-white/10 shadow-lg rounded-xl h-10 w-10 text-muted-text hover:text-primary transition-all duration-300"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? <X size={20} /> : <History size={20} />}
        </Button>
        <Button
          variant="outline"
          size="icon"
          className="bg-secondary-background/80 backdrop-blur-md border-white/10 shadow-lg rounded-xl h-10 w-10 text-muted-text hover:text-primary transition-all duration-300"
          onClick={startNewChat}
        >
          <Plus size={20} />
        </Button>
      </div>

      {/* Floating Sidebar Panel */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: -400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -400, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="absolute top-16 left-4 z-30 w-80 max-h-[calc(100%-6rem)] flex flex-col bg-secondary-background/95 backdrop-blur-2xl border border-white/10 shadow-2xl rounded-3xl overflow-hidden"
          >
            <div className="p-5 border-b border-white/5 flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-[0.2em] text-muted-text">Historical Analysis</h3>
              <Badge variant="outline" className="text-[10px] opacity-50 bg-white/5 border-none">{sessions.length}</Badge>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-1 custom-scrollbar">
              {isLoadingSessions ? (
                <div className="flex flex-col gap-2 p-2">
                  {[1, 2, 3, 4].map(i => (
                    <div key={i} className="h-12 w-full bg-white/5 animate-pulse rounded-xl" />
                  ))}
                </div>
              ) : (
                sessions.map(s => (
                  <button
                    key={s.id}
                    onClick={() => loadSession(s.id)}
                    className={`w-full text-left px-5 py-3.5 rounded-2xl text-xs transition-all duration-300 flex items-center gap-3 group ${currentSessionId === s.id ? 'bg-primary/20 text-primary border border-primary/20 shadow-lg shadow-primary/5' : 'text-muted-text hover:bg-white/5 hover:text-primary-text'
                      }`}
                  >
                    <div className={`w-2 h-2 rounded-full ${currentSessionId === s.id ? 'bg-primary animate-pulse' : 'bg-white/10'}`} />
                    <span className="truncate flex-1 font-medium">{s.session_name}</span>
                    <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 transition-all duration-300 transform group-hover:translate-x-1" />
                  </button>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex-1 flex overflow-hidden relative z-10">
        <AnimatePresence mode="wait">
          {isLanding ? (
            <motion.div
              key="landing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex-1 flex flex-col items-center justify-center p-8 text-center"
            >
              <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: "spring", stiffness: 200, delay: 0.1 }}
                className="mb-8 w-24 h-24 rounded-[2.5rem] bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-2xl shadow-primary/20 relative group"
              >
                <div className="absolute inset-0 bg-primary blur-2xl opacity-20 group-hover:opacity-40 transition-opacity duration-500 rounded-[2.5rem]"></div>
                <Sparkles size={48} className="text-white relative z-10" />
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-5xl font-bold mb-6 tracking-tight text-gradient"
              >
                FlowSight Intelligence
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-secondary-text max-w-lg mb-12 text-xl font-medium leading-relaxed"
              >
                Unlock deep insights across your financial landscape. Start a conversation with your raw data.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="mb-16"
              >
                <Button
                  size="lg"
                  onClick={startNewChat}
                  className="h-16 px-10 rounded-2xl bg-gradient-to-r from-primary to-secondary text-white font-bold text-lg shadow-2xl shadow-primary/30 hover:shadow-primary/50 hover:scale-[1.02] transition-all duration-300 flex items-center gap-4 group"
                >
                  <MessageSquare size={24} />
                  Start New Intelligence Session
                  <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </Button>
              </motion.div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl w-full"
              >
                {promptCategories.map((cat, i) => (
                  <Card key={i} className="bg-white/5 border-white/5 backdrop-blur-lg hover:bg-white/10 hover:border-white/20 transition-all duration-500 rounded-3xl overflow-hidden group">
                    <CardHeader className="p-6 pb-2">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-2xl bg-white/5 flex items-center justify-center group-hover:scale-110 transition-transform duration-500">
                          {cat.icon}
                        </div>
                        <h3 className="font-bold text-sm tracking-wide text-primary-text">{cat.title}</h3>
                      </div>
                    </CardHeader>
                    <CardContent className="p-6 pt-0 space-y-3">
                      {cat.prompts.map((p, idx) => (
                        <button
                          key={idx}
                          onClick={async () => {
                            const sid = await startNewChat();
                            if (sid) handleSend(p, sid);
                          }}
                          className="w-full text-left p-4 bg-white/5 border border-white/5 rounded-2xl text-[13px] text-muted-text hover:text-white hover:bg-primary/10 hover:border-primary/20 transition-all duration-300 flex items-center justify-between group/btn"
                        >
                          <span className="truncate flex-1">{p}</span>
                          <Send size={14} className="opacity-0 group-hover/btn:opacity-100 transition-all duration-300 -translate-x-2 group-hover/btn:translate-x-0" />
                        </button>
                      ))}
                    </CardContent>
                  </Card>
                ))}
              </motion.div>
            </motion.div>
          ) : (
            <motion.div
              key="chat"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex-1 flex h-full overflow-hidden"
            >
              {/* Chat Panel */}
              <div className="flex-1 flex flex-col h-full bg-background/30 backdrop-blur-sm overflow-hidden relative">

                {/* Header Info */}
                <div className="h-16 border-b border-white/5 flex items-center justify-center px-6 relative">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-success animate-pulse shadow-[0_0_8px_rgba(22,199,132,0.8)]" />
                    <span className="text-xs font-bold uppercase tracking-[0.3em] text-muted-text">Neural Engine Active</span>
                  </div>
                </div>

                {/* Messages Container */}
                <div ref={chatContainerRef} className="flex-1 overflow-y-auto px-8 py-10 space-y-10 custom-scrollbar">
                  {messages.length === 0 && isLoadingHistory ? (
                    <div className="flex flex-col gap-6 max-w-3xl mx-auto">
                      <div className="h-24 w-4/5 bg-white/5 animate-pulse rounded-3xl" />
                      <div className="h-20 w-2/3 bg-white/5 animate-pulse rounded-3xl self-end" />
                      <div className="h-24 w-3/4 bg-white/5 animate-pulse rounded-3xl" />
                    </div>
                  ) : (
                    <div className="max-w-4xl mx-auto w-full space-y-8">
                      {messages.map((msg, idx) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`max-w-[85%] group relative flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                            <div className={`text-[10px] mb-2 font-black uppercase tracking-[0.2em] text-muted-text opacity-50 group-hover:opacity-100 transition-opacity flex gap-2 items-center ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                              {msg.role === 'user' ? (
                                <><span>Analyst</span><div className="w-4 h-[1px] bg-white/20" /></>
                              ) : (
                                <><span>FlowSight AI</span><div className="w-4 h-[1px] bg-white/20" /></>
                              )}
                            </div>
                            <div className={`rounded-3xl px-6 py-4.5 text-[15px] leading-relaxed shadow-xl border ${msg.role === 'user'
                              ? 'bg-primary text-white border-primary/20 rounded-tr-none shadow-primary/10'
                              : 'bg-secondary-background/80 border-white/10 text-primary-text rounded-tl-none shadow-black/20 backdrop-blur-md'
                              }`}>
                              {msg.content}
                            </div>
                          </div>
                        </motion.div>
                      ))}
                      {isLoading && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                          <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-none px-6 py-4 flex gap-2 items-center">
                            <div className="flex gap-1.5">
                              <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce" />
                              <span className="w-1.5 h-1.5 bg-primary/80 rounded-full animate-bounce [animation-delay:0.2s]" />
                              <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce [animation-delay:0.4s]" />
                            </div>
                            <span className="text-[11px] font-bold uppercase tracking-widest text-primary ml-4">Crunching Data...</span>
                          </div>
                        </motion.div>
                      )}
                    </div>
                  )}
                </div>

                {/* Input Area */}
                <div className="p-10 max-w-5xl mx-auto w-full relative">
                  <div className="absolute inset-x-10 bottom-10 h-32 bg-gradient-to-t from-background to-transparent pointer-events-none opacity-50"></div>
                  <div className="relative z-10 p-2 bg-secondary-background/60 backdrop-blur-2xl border border-white/10 rounded-[2rem] shadow-2xl group focus-within:border-primary/50 transition-all duration-500">
                    <div className="flex items-center">
                      <div className="pl-4 pr-2">
                        <Database size={20} className="text-muted-text group-focus-within:text-primary transition-colors" />
                      </div>
                      <Input
                        value={inputVal}
                        onChange={(e) => setInputVal(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Deep dive into your financial data..."
                        className="border-none bg-transparent focus-visible:ring-0 text-lg h-14 px-4 placeholder:text-muted-text/30"
                        disabled={isLoading}
                      />
                      <Button
                        size="icon"
                        onClick={() => handleSend()}
                        className={`h-12 w-12 rounded-2xl transition-all duration-500 mr-1 ${inputVal.trim() ? 'bg-primary scale-100 opacity-100 shadow-lg shadow-primary/20' : 'bg-white/5 scale-95 opacity-50 cursor-not-allowed'}`}
                        disabled={!inputVal.trim() || isLoading}
                      >
                        {isLoading ? <Loader2 size={20} className="animate-spin text-white" /> : <Send size={20} />}
                      </Button>
                    </div>
                  </div>
                  <div className="flex justify-center mt-4">
                    <p className="text-[11px] text-muted-text uppercase tracking-[0.3em] font-bold opacity-30 flex items-center gap-4">
                      <span className="w-12 h-[1px] bg-white/10"></span>
                      Intelligent Context Injection Enabled
                      <span className="w-12 h-[1px] bg-white/10"></span>
                    </p>
                  </div>
                </div>
              </div>

              {/* Data Intelligence Overlay - Only shows if there is SQL/Data */}
              <AnimatePresence>
                {lastResponse && lastResponse.tables_used?.length > 0 && (
                  <motion.div
                    initial={{ x: 400, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: 400, opacity: 0 }}
                    transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                    className="hidden 2xl:flex flex-col w-[450px] border-l border-white/5 bg-secondary-background/40 backdrop-blur-xl p-8 space-y-8 overflow-y-auto custom-scrollbar"
                  >
                    <div className="flex items-center justify-between pb-2 border-b border-white/5">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/20">
                          <BarChart3 size={20} className="text-primary" />
                        </div>
                        <div>
                          <h3 className="font-black text-sm tracking-tight uppercase">Intelligence Deck</h3>
                          <p className="text-[10px] text-muted-text uppercase tracking-widest">Real-time Data Synthesis</p>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-6">
                      <Card className="bg-white/5 border-white/10 overflow-hidden shadow-2xl rounded-3xl">
                        <CardHeader className="p-6 flex flex-row items-center justify-between pb-0">
                          <span className="text-[11px] font-black uppercase tracking-widest text-muted-text">Data Visualization</span>
                          <Badge className="text-[10px] bg-primary/10 text-primary border-none uppercase px-3 py-1 font-black">{lastResponse.insight?.chart_type}</Badge>
                        </CardHeader>
                        <CardContent className="h-64 p-6 pt-4">
                          {renderChart()}
                        </CardContent>
                      </Card>

                      <Card className="bg-white/5 border-white/10 rounded-3xl overflow-hidden shadow-2xl">
                        <CardHeader className="p-6 pb-2">
                          <div className="flex items-center gap-2">
                            <Terminal size={14} className="text-primary" />
                            <span className="text-[11px] font-black uppercase tracking-widest text-muted-text">Synthesized Query</span>
                          </div>
                        </CardHeader>
                        <CardContent className="p-6 pt-0">
                          <div className="bg-black/60 rounded-2xl p-4 border border-white/5 group relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-1 h-full bg-primary/40 group-hover:bg-primary transition-colors"></div>
                            <code className="text-[11px] font-mono text-primary/80 break-words block leading-relaxed custom-scrollbar max-h-32 overflow-y-auto">
                              {lastResponse.sql}
                            </code>
                          </div>
                          <div className="mt-4 flex flex-wrap gap-2">
                            {lastResponse.tables_used.map(t => (
                              <Badge key={t} variant="secondary" className="text-[10px] bg-white/5 text-muted-text border-white/10 px-3 py-1 rounded-full font-bold">
                                {t}
                              </Badge>
                            ))}
                          </div>
                        </CardContent>
                      </Card>

                      <Card className="bg-primary/5 border-primary/20 rounded-3xl shadow-[0_0_40px_rgba(79,140,255,0.05)] border-dashed border-2">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center">
                                <Database size={20} className="text-primary" />
                              </div>
                              <div>
                                <span className="text-[11px] font-black uppercase tracking-widest text-primary block mb-1">Context Clarity</span>
                                <div className="flex gap-1">
                                  {[1, 2, 3, 4, 5].map(i => (
                                    <div key={i} className={`h-1.5 w-6 rounded-full ${i <= (lastResponse.insight?.confidence / 0.2) ? 'bg-primary' : 'bg-primary/10'}`}></div>
                                  ))}
                                </div>
                              </div>
                            </div>
                            <span className="text-2xl font-black text-primary">{Math.round((lastResponse.insight?.confidence || 0.95) * 100)}%</span>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
