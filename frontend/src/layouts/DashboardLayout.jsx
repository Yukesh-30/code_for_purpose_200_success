import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, 
  TrendingUp, 
  AlertTriangle, 
  Wallet, 
  Briefcase, 
  MessageSquare, 
  Users, 
  Settings,
  Bell,
  Search,
  ChevronLeft,
  ChevronRight,
  Menu,
  PieChart,
  ShieldAlert,
  BarChart3,
  Eye,
  LogOut,
  AppWindow,
  Upload
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { ThemeToggle } from '../components/ui/ThemeToggle';

const msmeNavItems = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { name: 'Data Central', icon: Upload, path: '/upload-data' },
  { name: 'Cash Flow Forecast', icon: TrendingUp, path: '/forecast' },
  { name: 'Invoice Risk', icon: AlertTriangle, path: '/invoice-risk' },
  { name: 'Working Capital', icon: Wallet, path: '/working-capital' },
  { name: 'Banking Recommendations', icon: Briefcase, path: '/banking-recommendations' },
  { name: 'Talk to Data', icon: MessageSquare, path: '/talk-to-data' },
  { name: 'Team Workspace', icon: Users, path: '/team' },
  { name: 'Settings', icon: Settings, path: '/settings' },
];

const bankNavItems = [
  { name: 'Portfolio Dashboard', icon: LayoutDashboard, path: '/bank/portfolio' },
  { name: 'High-Risk MSMEs', icon: ShieldAlert, path: '/bank/risk-list' },
  { name: 'Risk & Default Prediction', icon: BarChart3, path: '/bank/prediction' },
  { name: 'Lending Opportunities', icon: Wallet, path: '/bank/opportunities' },
  { name: 'Explainability Center', icon: Eye, path: '/bank/explainability' },
  { name: 'Alert Center', icon: Bell, path: '/bank/alerts' },
  { name: 'System Admin', icon: AppWindow, path: '/bank/admin' },
  { name: 'Settings', icon: Settings, path: '/settings' },
];

export default function DashboardLayout() {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const navItems = user?.role === 'bank' ? bankNavItems : msmeNavItems;

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="flex h-screen theme-gradient text-primary-text overflow-hidden">
      
      {/* Sidebar */}
      <motion.aside 
        initial={{ width: 280 }}
        animate={{ width: isSidebarOpen ? 280 : 80 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="flex flex-col bg-secondary-background border-r border-border h-full relative z-20"
      >
        <div className="h-16 flex items-center justify-between px-4 border-b border-border">
          {isSidebarOpen ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2 font-bold text-xl text-gradient">
              <TrendingUp className="text-primary" size={24} />
              FlowSight AI
            </motion.div>
          ) : (
            <div className="mx-auto">
              <TrendingUp className="text-primary" size={28} />
            </div>
          )}
        </div>

        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) => `
                flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200
                ${isActive 
                  ? 'bg-gradient-to-r from-primary to-secondary text-white shadow-lg shadow-primary/20' 
                  : 'text-muted-text hover:bg-white/5 hover:text-primary-text'
                }
              `}
            >
              <item.icon size={20} className="shrink-0" />
              {isSidebarOpen && (
                <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="font-medium text-sm whitespace-nowrap">
                  {item.name}
                </motion.span>
              )}
            </NavLink>
          ))}
          
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 text-muted-text hover:bg-danger/10 hover:text-danger mt-4"
          >
            <LogOut size={20} className="shrink-0" />
            {isSidebarOpen && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="font-medium text-sm whitespace-nowrap">
                Logout
              </motion.span>
            )}
          </button>
        </nav>

        {/* User Profile Mini */}
        <div className="p-4 border-t border-border flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full bg-gradient-to-tr ${user?.role === 'bank' ? 'from-secondary to-info' : 'from-primary to-secondary'} flex items-center justify-center shrink-0`}>
            <span className="font-bold text-sm text-white">{user?.avatar || '??'}</span>
          </div>
          {isSidebarOpen && (
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-semibold truncate text-white">{user?.name || 'Guest'}</p>
              <p className="text-xs text-muted-text truncate">{user?.role === 'bank' ? 'Bank Admin' : 'MSME Owner'}</p>
            </div>
          )}
        </div>

        {/* Toggle Button */}
        <button 
          onClick={() => setSidebarOpen(!isSidebarOpen)}
          className="absolute -right-3 top-20 bg-card border border-border rounded-full p-1.5 text-muted-text hover:text-primary-text shadow-md z-30"
        >
          {isSidebarOpen ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
        </button>
      </motion.aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        
        {/* Topbar */}
        <header className="h-16 flex items-center justify-between px-6 theme-gradient/80 backdrop-blur-md border-b border-border z-10">
          <div className="flex items-center gap-4 flex-1">
            <div className="relative w-full max-w-md hidden md:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-text" size={18} />
              <Input placeholder="Search insights, invoices, or ask AI..." className="pl-10 bg-secondary-background/50 border-none rounded-full h-10" />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <div className="relative">
              <Button variant="ghost" size="icon" className="relative rounded-full" onClick={() => { setShowNotifications(!showNotifications); setShowQuickActions(false); }}>
                <Bell size={20} />
                <span className="absolute top-2 right-2 w-2 h-2 bg-danger rounded-full border border-background"></span>
              </Button>
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-72 bg-card border border-border rounded-lg shadow-xl z-50 p-4">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-semibold text-primary-text">Notifications</h4>
                    <span className="text-xs text-primary cursor-pointer hover:underline">Mark all as read</span>
                  </div>
                  <ul className="text-sm space-y-2">
                    <li className="p-3 bg-secondary-background/50 border border-border rounded-lg flex gap-3 items-start">
                      <div className="w-2 h-2 mt-1.5 rounded-full bg-danger shrink-0"></div>
                      <div>
                        <p className="font-medium text-primary-text">Invoice #INV-2050 at High Risk</p>
                        <p className="text-xs text-muted-text mt-1">Predicted delay of 21 days for Nexus Inc.</p>
                      </div>
                    </li>
                    <li className="p-3 bg-secondary-background/50 border border-border rounded-lg flex gap-3 items-start">
                      <div className="w-2 h-2 mt-1.5 rounded-full bg-warning shrink-0"></div>
                      <div>
                        <p className="font-medium text-primary-text">Cash Gap Approaching</p>
                        <p className="text-xs text-muted-text mt-1">-$12,450 projected on Apr 24.</p>
                      </div>
                    </li>
                  </ul>
                </div>
              )}
            </div>
            
            <div className="relative">
              <Button className="hidden md:flex rounded-full" onClick={() => { setShowQuickActions(!showQuickActions); setShowNotifications(false); }}>Quick Action</Button>
              {showQuickActions && (
                 <div className="absolute right-0 mt-2 w-56 bg-card border border-border rounded-lg shadow-xl z-50 py-2">
                   <h4 className="px-4 py-2 text-xs font-semibold text-muted-text uppercase tracking-wider">Shortcuts</h4>
                   <button className="w-full text-left px-4 py-2 hover:bg-secondary-background text-sm text-primary-text flex items-center gap-2" onClick={() => { navigate('/upload-data'); setShowQuickActions(false); }}>
                     <Upload size={16} className="text-secondary" /> Upload ERP Data
                   </button>
                   <button className="w-full text-left px-4 py-2 hover:bg-secondary-background text-sm text-primary-text flex items-center gap-2" onClick={() => { navigate('/talk-to-data'); setShowQuickActions(false); }}>
                     <MessageSquare size={16} className="text-primary" /> Ask AI Assistant
                   </button>
                   <button className="w-full text-left px-4 py-2 hover:bg-secondary-background text-sm text-primary-text flex items-center gap-2" onClick={() => { navigate('/banking-recommendations'); setShowQuickActions(false); }}>
                     <Wallet size={16} className="text-success" /> Explore Funding
                   </button>
                 </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-background">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="max-w-7xl mx-auto h-full"
          >
            <Outlet />
          </motion.div>
        </main>
      </div>

    </div>
  );
}
