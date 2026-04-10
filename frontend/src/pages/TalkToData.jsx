import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Database, Terminal, Download, Bookmark, MessageSquare, Briefcase, TrendingUp } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

const suggestedPrompts = [
  "Will I face a cash shortage next month?",
  "Which invoices are most likely to be delayed?",
  "Why did my working capital score reduce?",
  "Suggest the best banking product for me.",
  "Compare March and April cash flow."
];

const mockChartData = [
  { name: 'Mar 1', inflow: 4000, outflow: 2400 },
  { name: 'Mar 8', inflow: 3000, outflow: 1398 },
  { name: 'Mar 15', inflow: 2000, outflow: 9800 },
  { name: 'Mar 22', inflow: 2780, outflow: 3908 },
  { name: 'Mar 29', inflow: 1890, outflow: 4800 },
  { name: 'Apr 5', inflow: 2390, outflow: 3800 },
  { name: 'Apr 12', inflow: 3490, outflow: 4300 },
];

export default function TalkToData() {
  const [messages, setMessages] = useState([
    { role: 'ai', content: 'Hello! I am FlowSight AI. You can ask me anything about your cash flow, invoice risks, or banking options. How can I help you today?' }
  ]);
  const [inputVal, setInputVal] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showResultWidget, setShowResultWidget] = useState(false);

  const handleSend = (text = inputVal) => {
    if (!text.trim()) return;
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInputVal('');
    setIsTyping(true);
    setShowResultWidget(false);

    // Mock AI Response
    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [...prev, { 
        role: 'ai', 
        content: `I've analyzed your March and April cash flow data. It looks like you had a significant outflow spike around March 15th, but revenue is slightly recovering in April. I've generated a comparison chart for you.` 
      }]);
      setShowResultWidget(true);
    }, 1500);
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-8rem)]">
      
      {/* Left Chat Area */}
      <Card className="flex-[3] flex flex-col h-full border-border/60">
        <div className="p-4 border-b border-border flex items-center justify-between bg-secondary-background/30 rounded-t-2xl">
          <div className="flex items-center gap-2">
            <Sparkles className="text-secondary" size={20} />
            <h2 className="font-semibold text-lg">AI Financial Assistant</h2>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-text bg-background border border-border px-3 py-1.5 rounded-md">
            <Database size={16} /> Data Source: All Connected Ledgers
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user' 
                    ? 'bg-primary text-white rounded-br-none' 
                    : 'bg-secondary-background border border-border text-primary-text rounded-bl-none'
                }`}>
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                </div>
              </motion.div>
            ))}
            {isTyping && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                <div className="bg-secondary-background border border-border rounded-2xl rounded-bl-none px-4 py-3 flex gap-1">
                  <span className="w-2 h-2 bg-muted-text rounded-full animate-bounce"></span>
                  <span className="w-2 h-2 bg-muted-text rounded-full animate-bounce delay-75"></span>
                  <span className="w-2 h-2 bg-muted-text rounded-full animate-bounce delay-150"></span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="p-4 border-t border-border bg-secondary-background/30 rounded-b-2xl">
          {messages.length === 1 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {suggestedPrompts.map((p, i) => (
                <button 
                  key={i} 
                  onClick={() => handleSend(p)}
                  className="text-xs bg-background border border-border hover:border-primary/50 text-muted-text hover:text-primary transition-colors px-3 py-1.5 rounded-full"
                >
                  {p}
                </button>
              ))}
            </div>
          )}
          <div className="relative flex items-center">
            <Input 
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask anything about your business finances..." 
              className="pr-12 h-12 rounded-xl bg-background border-border focus-visible:ring-primary focus-visible:border-primary"
            />
            <Button 
              size="icon" 
              className="absolute right-1 h-10 w-10 rounded-lg bg-primary hover:bg-primary/90" 
              onClick={() => handleSend()}
            >
              <Send size={18} />
            </Button>
          </div>
        </div>
      </Card>

      {/* Right Intelligence Area */}
      <motion.div 
        initial={false}
        animate={{ width: showResultWidget ? '35%' : '0%', opacity: showResultWidget ? 1 : 0 }}
        className="hidden lg:flex flex-col gap-4 overflow-hidden"
      >
        {showResultWidget && (
          <>
            <Card className="glass-panel overflow-hidden">
              <CardHeader className="pb-2 flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-base flex items-center gap-2"><TrendingUp size={16} className="text-success" /> Generated Insight</CardTitle>
                </div>
                <div className="flex gap-2">
                   <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-text"><Bookmark size={16}/></Button>
                   <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-text"><Download size={16}/></Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="h-48 w-full mt-2">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={mockChartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: '#7C879F', fontSize: 10 }} tickFormatter={(val) => `$${val/1000}k`} />
                      <RechartsTooltip cursor={{fill: 'rgba(255,255,255,0.02)'}} contentStyle={{ backgroundColor: '#121A2F', borderColor: 'rgba(255,255,255,0.08)', borderRadius: '8px' }} />
                      <Bar dataKey="inflow" fill="#16C784" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="outflow" fill="#FF5C5C" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 pt-4 border-t border-border flex justify-between items-center text-sm">
                   <span className="text-muted-text flex items-center gap-1"><Terminal size={14}/> Query Executed</span>
                   <Badge variant="success">98% Confidence</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="glass-panel border-warning/30 bg-warning/5">
              <CardContent className="p-4 space-y-2">
                <div className="flex items-center gap-2 text-warning font-semibold text-sm">
                  <AlertTriangle size={16} /> Follow-up Action Required
                </div>
                <p className="text-sm text-primary-text">
                  The outflow spike on March 15 drops your Working Capital score to 62. Should we explore short-term financing?
                </p>
                <Button variant="outline" size="sm" className="w-full mt-2 border-warning/50 hover:bg-warning/10 text-warning">Explore Financing Options</Button>
              </CardContent>
            </Card>
          </>
        )}
      </motion.div>
    </div>
  );
}
