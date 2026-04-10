import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Upload, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  FilePlus,
  CreditCard,
  Briefcase,
  TrendingDown
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useAuth } from '../context/AuthContext';

export default function DataUpload() {
  const { user } = useAuth();
  const [uploadStates, setUploadStates] = useState({
    transactions: { loading: false, result: null, error: null },
    invoices: { loading: false, result: null, error: null },
    expenses: { loading: false, result: null, error: null }
  });

  const handleFileUpload = async (type, file) => {
    if (!file) return;

    setUploadStates(prev => ({
      ...prev,
      [type]: { ...prev[type], loading: true, error: null, result: null }
    }));

    const formData = new FormData();
    formData.append('file', file);
    formData.append('business_id', 1); // Mock business ID for now, should come from user context later

    try {
      const endpoint = type === 'transactions' ? 'bank-transactions' : type;
      const response = await fetch(`http://localhost:5000/upload/${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setUploadStates(prev => ({
          ...prev,
          [type]: { loading: false, result: data, error: null }
        }));
      } else {
        setUploadStates(prev => ({
          ...prev,
          [type]: { loading: false, result: null, error: data.error || 'Upload failed' }
        }));
      }
    } catch (err) {
      setUploadStates(prev => ({
        ...prev,
        [type]: { loading: false, result: null, error: 'Network error or server down' }
      }));
    }
  };

  const uploadSections = [
    {
      id: 'transactions',
      title: 'Bank Transactions',
      description: 'Upload your transaction history (CSV)',
      icon: CreditCard,
      color: 'text-primary'
    },
    {
      id: 'invoices',
      title: 'Sales Invoices',
      description: 'Upload pending and paid invoices (CSV)',
      icon: FilePlus,
      color: 'text-success'
    },
    {
      id: 'expenses',
      title: 'Business Expenses',
      description: 'Upload monthly recurring expenses (CSV)',
      icon: TrendingDown,
      color: 'text-warning'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-bold tracking-tight">Data Central</h1>
        <p className="text-muted-text">Upload your financial data to power our AI forecasting engine.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {uploadSections.map((section) => (
          <Card key={section.id} className="glass-panel border-white/5 overflow-hidden group hover:border-primary/30 transition-all">
            <CardHeader>
              <div className={`w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mb-4 ${section.color}`}>
                <section.icon size={24} />
              </div>
              <CardTitle>{section.title}</CardTitle>
              <CardDescription>{section.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="relative">
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileUpload(section.id, e.target.files[0])}
                  className="hidden"
                  id={`file-input-${section.id}`}
                  disabled={uploadStates[section.id].loading}
                />
                <label
                  htmlFor={`file-input-${section.id}`}
                  className={`
                    flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer
                    transition-all duration-200
                    ${uploadStates[section.id].loading ? 'border-primary/20 bg-primary/5 cursor-wait' : 'border-white/10 hover:border-primary/50 hover:bg-white/5'}
                  `}
                >
                  {uploadStates[section.id].loading ? (
                    <div className="flex flex-col items-center gap-2">
                       <span className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></span>
                       <span className="text-xs text-muted-text">Processing...</span>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center gap-2">
                      <Upload size={24} className="text-muted-text" />
                      <span className="text-sm font-medium">Click to select CSV</span>
                    </div>
                  )}
                </label>
              </div>

              {uploadStates[section.id].result && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 rounded-lg bg-success/10 border border-success/20 text-success text-xs flex items-center gap-2"
                >
                  <CheckCircle2 size={16} />
                  <span>Success: {uploadStates[section.id].result.rows_inserted} rows added</span>
                </motion.div>
              )}

              {uploadStates[section.id].error && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 rounded-lg bg-danger/10 border border-danger/20 text-danger text-xs flex items-center gap-2"
                >
                  <AlertCircle size={16} />
                  <span>{uploadStates[section.id].error}</span>
                </motion.div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="glass-panel border-white/5">
        <CardHeader>
          <CardTitle className="text-xl">Import Instructions & Samples</CardTitle>
          <CardDescription>Follow these templates for perfect AI accuracy.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
               <h4 className="font-semibold text-primary-text flex items-center gap-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-primary" /> Required Columns
               </h4>
               <ul className="space-y-2 text-sm text-muted-text">
                 <li><code className="text-primary-text font-mono">transaction_date, amount, transaction_type</code> (Bank)</li>
                 <li><code className="text-primary-text font-mono">invoice_number, invoice_amount, due_date</code> (Invoices)</li>
                 <li><code className="text-primary-text font-mono">expense_name, amount, expense_date</code> (Expenses)</li>
               </ul>
            </div>
            <div className="space-y-4 text-sm text-muted-text bg-white/5 p-4 rounded-xl border border-white/5">
               <p>Use the sample data provided in the <code className="text-primary">backend/sample_data/</code> folder to test the system immediately.</p>
               <Button variant="outline" size="sm" className="w-full mt-2">
                 Learn more about data security <ArrowRight size={14} className="ml-2"/>
               </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
