'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  BarChart3, Users, Coins, Zap, ShieldCheck, 
  Search, ArrowUpRight, TrendingUp, LayoutGrid, 
  Loader2, Play, Book, GraduationCap, AlertCircle,
  ExternalLink, User
} from "lucide-react";
import { getAdminStats, getAdminUsers } from "@/lib/api";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, usersData] = await Promise.all([
          getAdminStats(),
          getAdminUsers()
        ]);
        
        if (statsData.detail || usersData.detail) {
          setError("Sovereign Access Denied. Master Node Identity Required.");
          return;
        }

        setStats(statsData);
        setUsers(usersData);
      } catch (err) {
        setError("Commercial Link Failure. Admin Node Unreachable.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center space-y-4">
        <Loader2 size={48} className="text-emerald-500 animate-spin" />
        <p className="text-xs font-black uppercase tracking-[0.3em] text-slate-500">Synchronizing Command Center...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center space-y-6 text-center px-4">
        <div className="p-6 rounded-full bg-red-500/10 text-red-500 mb-2">
           <ShieldCheck size={48} />
        </div>
        <h1 className="text-2xl font-black text-white italic underline decoration-red-500 decoration-4 underline-offset-8">SECURITY PROTOCOL ACTIVE</h1>
        <p className="text-slate-400 max-w-md font-medium">{error}</p>
        <button 
          onClick={() => router.push("/")}
          className="px-8 py-3 rounded-2xl bg-slate-800 text-white text-[10px] font-black uppercase tracking-widest hover:bg-slate-700 transition-all"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-12 pb-20">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-8 pt-4">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
             <div className="p-3 rounded-2xl bg-indigo-500/10 text-indigo-400">
                <LayoutGrid size={28} />
             </div>
             <h1 className="text-4xl font-black italic tracking-tighter text-white">COMMAND CENTER</h1>
          </div>
          <p className="text-slate-400 text-sm font-medium tracking-wide">Ecosystem-wide production oversight and commercial ledger.</p>
        </div>

        <div className="flex items-center gap-4">
           <div className="glass-card px-6 py-4 rounded-2xl bg-slate-900/40 border-slate-800 flex items-center gap-4">
              <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.8)]" />
              <span className="text-[10px] font-black text-white uppercase tracking-widest">Oracle Links Stable</span>
           </div>
        </div>
      </header>

      {/* Metric Cluster */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { label: 'Total Revenue', value: stats.total_invoiced, prefix: '$', color: 'emerald', icon: Coins },
          { label: 'Total Jobs', value: stats.total_jobs, prefix: '', color: 'cyan', icon: Zap },
          { label: 'Active Nodes', value: stats.users, prefix: '', color: 'indigo', icon: Users },
          { label: 'System Credits', value: stats.balance, prefix: '', color: 'rose', icon: BarChart3 },
        ].map((metric) => (
          <div key={metric.label} className="glass-card p-6 rounded-3xl bg-slate-900/40 border-slate-800 hover:border-slate-700 transition-all group">
             <div className="flex items-center justify-between mb-4">
                <div className={`p-2.5 rounded-xl bg-${metric.color}-500/10 text-${metric.color}-400`}>
                   <metric.icon size={20} />
                </div>
                <TrendingUp size={16} className="text-slate-600 group-hover:text-emerald-500 transition-colors" />
             </div>
             <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest block mb-1">{metric.label}</span>
             <div className="text-2xl font-black text-white tabular-nums italic tracking-tighter">
                {metric.prefix}{metric.value.toLocaleString()}
             </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* User Ledger */}
        <div className="lg:col-span-2 space-y-6">
           <div className="flex items-center justify-between">
              <h2 className="text-xs font-black text-indigo-400 uppercase tracking-[0.3em]">User Ledger</h2>
              <div className="flex items-center gap-2 text-slate-500 text-[10px] font-black uppercase tracking-widest">
                 <Search size={12} />
                 <span>Search Nodes</span>
              </div>
           </div>

           <div className="glass-card rounded-[2.5rem] bg-slate-900/40 border-slate-800 overflow-hidden">
              <table className="w-full text-left">
                 <thead>
                    <tr className="border-b border-slate-800">
                       <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Node Node</th>
                       <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Power Level</th>
                       <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Vault Status</th>
                       <th className="px-8 py-6 text-[10px] font-black text-slate-500 uppercase tracking-widest">Operation</th>
                    </tr>
                 </thead>
                 <tbody className="divide-y divide-slate-800/50">
                    {users.map((user) => (
                      <tr key={user.username} className="hover:bg-white/[0.02] transition-colors group">
                         <td className="px-8 py-6">
                            <div className="flex items-center gap-3">
                               <div className="h-8 w-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400">
                                  <User size={16} />
                               </div>
                               <span className="text-white font-bold text-sm tracking-tight">{user.username}</span>
                            </div>
                         </td>
                         <td className="px-8 py-6">
                            <div className="flex items-center gap-2">
                               <span className="text-white font-black tabular-nums">{user.balance}</span>
                               <span className="text-[10px] font-black text-emerald-500 uppercase tracking-tighter">Credits</span>
                            </div>
                         </td>
                         <td className="px-8 py-6">
                            <div className="flex items-center gap-2">
                               <div className={`h-1.5 w-1.5 rounded-full ${user.keys_configured > 0 ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-slate-600'}`} />
                               <span className="text-xs font-bold text-slate-400">{user.keys_configured} Keys Linked</span>
                            </div>
                         </td>
                         <td className="px-8 py-6">
                            <button className="p-2 rounded-xl bg-slate-800/50 text-slate-500 hover:text-white hover:bg-slate-700 transition-all opacity-0 group-hover:opacity-100">
                               <ExternalLink size={16} />
                            </button>
                         </td>
                      </tr>
                    ))}
                 </tbody>
              </table>
           </div>
        </div>

        {/* Synthesis Distribution */}
        <div className="space-y-6">
           <h2 className="text-xs font-black text-emerald-400 uppercase tracking-[0.3em]">Factory Load</h2>
           
           <div className="glass-card p-10 rounded-[3rem] bg-slate-900/40 border-slate-800 space-y-8">
              {[
                { label: 'Video Synthesizer', count: stats.job_breakdown.video, icon: Play, color: 'rose' },
                { label: 'E-Book Generator', count: stats.job_breakdown.ebook, icon: Book, color: 'indigo' },
                { label: 'Course Factory', count: stats.job_breakdown.course, icon: GraduationCap, color: 'cyan' },
                { label: 'Thumbnail Oracle', count: stats.job_breakdown.thumbnail, icon: LayoutGrid, color: 'amber' },
              ].map((factory) => (
                <div key={factory.label} className="space-y-3">
                   <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                         <factory.icon size={16} className={`text-${factory.color}-400`} />
                         <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{factory.label}</span>
                      </div>
                      <span className="text-white font-black tabular-nums italic text-sm">{factory.count}</span>
                   </div>
                   <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${(factory.count / (stats.total_jobs || 1)) * 100}%` }}
                        className={`h-full bg-${factory.color}-500 shadow-[0_0_15px_rgba(59,130,246,0.3)]`}
                      />
                   </div>
                </div>
              ))}

              <div className="pt-6 border-t border-slate-800 flex items-center justify-between">
                 <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Industrial Throughput</span>
                 <span className="text-emerald-500 font-black italic">{stats.total_jobs} Total Units</span>
              </div>
           </div>

           <div className="glass-card p-8 rounded-[2.5rem] bg-emerald-500/5 border-emerald-500/20">
              <div className="flex items-center gap-3 mb-3">
                 <AlertCircle size={20} className="text-emerald-400" />
                 <span className="text-[10px] font-black text-white uppercase tracking-widest">Platform Status</span>
              </div>
              <p className="text-xs text-slate-400 font-medium leading-relaxed">System operating at peak efficiency. Synthesis taxation is currently yielding <span className="text-white font-bold">{Math.round(stats.total_jobs * 5)} estimated platform credits</span> in operating fees.</p>
           </div>
        </div>
      </div>
    </div>
  );
}
