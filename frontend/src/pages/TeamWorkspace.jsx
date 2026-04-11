import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, UserPlus, MoreVertical, Mail, Star, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useAuth } from '../context/AuthContext';

export default function TeamWorkspace() {
  const { user } = useAuth();
  const [members, setMembers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [inviteData, setInviteData] = useState({ name: '', email: '', role: 'Viewer' });
  const [openMenuId, setOpenMenuId] = useState(null);

  const fetchMembers = async () => {
    try {
      const res = await fetch(`http://localhost:5000/team/members?business_id=${user.business_id}`);
      const data = await res.json();
      if (res.ok) setMembers(data.members || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (user?.business_id) {
      fetchMembers();
    }
  }, [user]);

  const handleInvite = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:5000/team/invite`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...inviteData, business_id: user.business_id })
      });
      if (res.ok) {
        setIsModalOpen(false);
        setInviteData({ name: '', email: '', role: 'Viewer' });
        fetchMembers();
      } else {
        alert("Failed to invite member. Perhaps email already in team?");
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleRemoveMember = async (userId) => {
    try {
      const res = await fetch(`http://localhost:5000/team/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ business_id: user.business_id, user_id: userId })
      });
      if (res.ok) {
        fetchMembers();
      } else {
        alert("Failed to remove member.");
      }
    } catch (e) {
      console.error(e);
    }
    setOpenMenuId(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight">Team Workspace</h1>
          <p className="text-muted-text">Manage access and collaborate with your team.</p>
        </div>
        <Button className="gap-2 shrink-0" onClick={() => setIsModalOpen(true)}>
          <UserPlus size={16} /> Invite Member
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="glass-panel border-white/5 bg-gradient-to-br from-primary/10 to-transparent">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="p-3 bg-primary/20 rounded-xl text-primary">
              <Users size={24} />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-text">Total Members</p>
              <h3 className="text-2xl font-bold">{members.length}</h3>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="glass-panel border-white/5 overflow-hidden">
        <CardHeader className="border-b border-white/5 pb-4">
          <CardTitle>Directory</CardTitle>
        </CardHeader>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-white/5 text-muted-text font-medium border-b border-white/5">
              <tr>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Role</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member, i) => (
                <motion.tr 
                  key={member.id} 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-white font-bold text-xs uppercase">
                        {member.name.charAt(0)}
                      </div>
                      <div>
                        <p className="font-semibold text-primary-text">{member.name}</p>
                        <p className="text-xs text-muted-text flex items-center gap-1">
                          <Mail size={10}/> {member.email}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 rounded-md bg-white/5 border border-white/10 text-xs font-medium capitalize">
                      {member.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${member.status === 'Active' ? 'bg-success' : 'bg-warning'}`} />
                      <span className={member.status === 'Active' ? 'text-success' : 'text-warning'}>
                        {member.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right relative">
                    <button 
                      onClick={() => setOpenMenuId(openMenuId === member.id ? null : member.id)}
                      className="p-2 hover:bg-white/10 rounded-lg text-muted-text transition-colors"
                    >
                      <MoreVertical size={16} />
                    </button>
                    {openMenuId === member.id && (
                      <div className="absolute right-6 mt-2 w-32 bg-surface border border-white/10 rounded-lg shadow-xl overflow-hidden z-10 top-10">
                        <button 
                          onClick={() => handleRemoveMember(member.id)} 
                          className="w-full text-left px-4 py-2 text-sm text-error hover:bg-white/5 transition-colors font-medium"
                        >
                          Remove Member
                        </button>
                      </div>
                    )}
                  </td>
                </motion.tr>
              ))}
              {members.length === 0 && (
                <tr>
                   <td colSpan="4" className="px-6 py-8 text-center text-muted-text">No members found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <AnimatePresence>
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-surface border border-white/10 rounded-2xl p-6 w-full max-w-md shadow-2xl"
            >
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold">Invite Member</h2>
                <button onClick={() => setIsModalOpen(false)} className="text-muted-text hover:text-white">
                  <X size={20} />
                </button>
              </div>
              <form onSubmit={handleInvite} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-text">Full Name</label>
                  <input 
                    required
                    type="text" 
                    className="w-full bg-background border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary"
                    value={inviteData.name}
                    onChange={(e) => setInviteData({...inviteData, name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-text">Email Address</label>
                  <input 
                    required
                    type="email" 
                    className="w-full bg-background border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary"
                    value={inviteData.email}
                    onChange={(e) => setInviteData({...inviteData, email: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-text">Role</label>
                  <select 
                    className="w-full bg-background border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary appearance-none"
                    value={inviteData.role}
                    onChange={(e) => setInviteData({...inviteData, role: e.target.value})}
                  >
                    <option value="Admin">Admin</option>
                    <option value="Editor">Editor</option>
                    <option value="Viewer">Viewer</option>
                  </select>
                </div>
                <Button type="submit" className="w-full mt-2" disabled={loading}>
                  {loading ? 'Sending Invite...' : 'Send Invite'}
                </Button>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
