import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Bell, Shield, Wallet, Link as LinkIcon, Save } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useAuth } from '../context/AuthContext';

export default function Settings() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'integrations', label: 'Integrations', icon: LinkIcon },
    { id: 'billing', label: 'Billing', icon: Wallet },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-text">Manage your account preferences and integrations.</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar Nav */}
        <div className="w-full lg:w-64 flex flex-col gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                activeTab === tab.id
                  ? 'bg-primary text-white shadow-lg shadow-primary/20'
                  : 'hover:bg-white/5 text-muted-text hover:text-primary-text'
              }`}
            >
              <tab.icon size={18} />
              <span className="font-medium text-sm">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="flex-1">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'profile' && (
              <Card className="glass-panel border-white/5">
                <CardHeader>
                  <CardTitle>Profile Information</CardTitle>
                  <CardDescription>Update your personal details here.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm text-muted-text">Full Name</label>
                      <input type="text" defaultValue={user?.name} className="w-full bg-background border border-white/10 rounded-lg px-4 py-2 text-primary-text focus:outline-none focus:border-primary" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm text-muted-text">Email</label>
                      <input type="email" defaultValue={user?.email} className="w-full bg-background border border-white/10 rounded-lg px-4 py-2 text-primary-text focus:outline-none focus:border-primary" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm text-muted-text">Role</label>
                    <input type="text" disabled defaultValue={user?.role} className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-muted-text cursor-not-allowed" />
                  </div>
                  <Button className="mt-4 gap-2">
                    <Save size={16} /> Save Changes
                  </Button>
                </CardContent>
              </Card>
            )}

            {activeTab === 'notifications' && (
              <Card className="glass-panel border-white/5">
                <CardHeader>
                  <CardTitle>Notification Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {['Email Alerts for Cash Gaps', 'Weekly AI Reports', 'New Invoice Tracking'].map((item, i) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-white/5 bg-white/5">
                      <span className="text-sm font-medium">{item}</span>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                      </label>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {activeTab === 'integrations' && (
              <Card className="glass-panel border-white/5">
                <CardHeader>
                  <CardTitle>Connected Software</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    { name: 'Xero Accounting', status: 'Connect', col: 'text-primary' },
                    { name: 'Stripe Payments', status: 'Connect', col: 'text-primary' },
                    { name: 'Razorpay', status: 'Connect', col: 'text-primary' }
                  ].map((item, i) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-white/5 bg-white/5">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-surface flex items-center justify-center border border-white/10">
                           <LinkIcon size={16} className="text-muted-text" />
                        </div>
                        <span className="font-semibold text-sm">{item.name}</span>
                      </div>
                      <Button variant={item.status === 'Connected' ? 'outline' : 'primary'} size="sm" className={item.col}>
                        {item.status}
                      </Button>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}
            
            {/* Fallback for others */}
            {['security', 'billing'].includes(activeTab) && (
              <Card className="glass-panel border-white/5 flex items-center justify-center p-12">
                <p className="text-muted-text">This section is currently under construction.</p>
              </Card>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
