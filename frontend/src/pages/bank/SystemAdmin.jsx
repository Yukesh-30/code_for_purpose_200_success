import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { Button } from '../../components/ui/Button';
import { Activity, ShieldCheck, Database, HardDrive, Cpu, Settings, Lock } from 'lucide-react';

export default function SystemAdmin() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Administration</h1>
          <p className="text-muted-text mt-1">Platform health, API connectivity, and global configuration.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="glass-panel">
          <CardContent className="p-6">
             <div className="flex items-center gap-3 mb-2">
                <Activity className="text-success" size={20}/>
                <h3 className="font-bold text-sm">System Uptime</h3>
             </div>
             <p className="text-2xl font-bold">99.98%</p>
             <p className="text-xs text-muted-text mt-1 text-success">All systems operational</p>
          </CardContent>
        </Card>
        <Card className="glass-panel">
          <CardContent className="p-6">
             <div className="flex items-center gap-3 mb-2">
                <ShieldCheck className="text-primary" size={20}/>
                <h3 className="font-bold text-sm">Security Level</h3>
             </div>
             <p className="text-2xl font-bold">Encrypted</p>
             <p className="text-xs text-muted-text mt-1">TLS 1.3 | SOC2 Compliant</p>
          </CardContent>
        </Card>
        <Card className="glass-panel">
          <CardContent className="p-6">
             <div className="flex items-center gap-3 mb-2">
                <Database className="text-info" size={20}/>
                <h3 className="font-bold text-sm">Data Connectors</h3>
             </div>
             <p className="text-2xl font-bold">18 Active</p>
             <p className="text-xs text-muted-text mt-1 text-info">2 syncs in progress</p>
          </CardContent>
        </Card>
        <Card className="glass-panel">
          <CardContent className="p-6">
             <div className="flex items-center gap-3 mb-2">
                <Cpu className="text-secondary" size={20}/>
                <h3 className="font-bold text-sm">AI Engine</h3>
             </div>
             <p className="text-2xl font-bold">v3.4.2</p>
             <p className="text-xs text-muted-text mt-1">Llama 3 Balanced Instance</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* API Health */}
        <Card>
          <CardHeader>
            <CardTitle>Connected Ledger APIs</CardTitle>
          </CardHeader>
          <CardContent>
             <div className="space-y-4">
               {[
                 { name: 'Xero Connection', status: 'Healthy', latency: '42ms' },
                 { name: 'QuickBooks Ledger', status: 'Healthy', latency: '85ms' },
                 { name: 'FreshBooks API', status: 'Degraded', latency: '420ms' },
                 { name: 'Internal Banking DB', status: 'Healthy', latency: '12ms' },
               ].map((api, i) => (
                 <div key={i} className="flex justify-between items-center p-3 bg-secondary-background/50 rounded-lg border border-border">
                   <div className="flex items-center gap-3">
                     <HardDrive size={16} className="text-muted-text" />
                     <span className="text-sm font-medium">{api.name}</span>
                   </div>
                   <div className="flex items-center gap-4">
                     <span className="text-xs text-muted-text">{api.latency}</span>
                     <Badge variant={api.status === 'Healthy' ? 'success' : 'warning'}>{api.status}</Badge>
                   </div>
                 </div>
               ))}
             </div>
             <Button variant="outline" className="w-full mt-4 text-xs">Run System Diagnostics</Button>
          </CardContent>
        </Card>

        {/* Configurations */}
        <Card>
          <CardHeader>
            <CardTitle>Global Risk Configuration</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
             <div className="flex items-center justify-between">
                <div>
                   <p className="text-sm font-semibold">Automatic Flagging Threshold</p>
                   <p className="text-xs text-muted-text">Score {'>'} 80 triggers manual review alert.</p>
                </div>
                <Button variant="outline" size="sm"><Settings size={14} className="mr-2"/> Configure</Button>
             </div>
             <div className="flex items-center justify-between">
                <div>
                   <p className="text-sm font-semibold">AI Prediction Confidence Cut-off</p>
                   <p className="text-xs text-muted-text">Hide results with less than 70% confidence.</p>
                </div>
                <Button variant="outline" size="sm"><Settings size={14} className="mr-2"/> Configure</Button>
             </div>
             <div className="flex items-center justify-between">
                <div>
                   <p className="text-sm font-semibold">Data Anonymization</p>
                   <p className="text-xs text-muted-text">Full GDPR/CCPA masking for training data.</p>
                </div>
                <Badge variant="success" className="gap-1"><Lock size={12}/> Enabled</Badge>
             </div>
             <div className="pt-4 border-t border-border">
                <Button className="w-full gap-2">Update Global Policies</Button>
             </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
