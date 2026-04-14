'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Book, GraduationCap, Zap, Activity, Clock, Server, CheckCircle2, AlertCircle, Loader2, Settings, ChevronRight, ArrowRight, ShieldCheck, X, ShieldAlert, CreditCard, Plus, Coins } from "lucide-react";
import { generateVideo, generateEbook, generateCourse, checkStatus, getJobStatus, cancelJob, getUserBalance, reloadCredits } from "@/lib/api";
import Link from "next/link";

export default function HomePage() {
  const [topic, setTopic] = useState("");
  const [queuedJobs, setQueuedJobs] = useState<any[]>([]); // {id, status, type, topic}
  const [serverStatus, setServerStatus] = useState<'online' | 'offline'>('offline');
  const [successMessage, setSuccessMessage] = useState("");
  const [balance, setBalance] = useState<number | null>(null);
  const [showRecharge, setShowRecharge] = useState(false);
  const [isRecharging, setIsRecharging] = useState(false);
  const [isHydrated, setIsHydrated] = useState(false);

  // 🏛️ [INDUSTRIAL SANITIZER] Normalize stale result_urls from localStorage
  const sanitizeResultUrl = (url: string | undefined): string | undefined => {
    if (!url) return url;
    // If the URL contains an absolute system path, extract the relative part
    const match = url.match(/(static\/.+\.\w+|courses\/.+\.\w+|final_video\/.+\.\w+)/);
    if (match) {
      return `http://127.0.0.1:8000/download?path=${match[1]}`;
    }
    // If it's already a proper URL (starts with http), return as-is
    if (url.startsWith('http')) return url;
    return undefined;
  };

  // Persistence: Load
  useEffect(() => {
    const saved = localStorage.getItem('vantix_queue');
    if (saved) {
      try {
        const jobs = JSON.parse(saved);
        // 🗑️ [PURGE] Remove cancelled jobs & sanitize stale result_urls
        const clean = jobs
          .filter((job: any) => job.status !== 'cancelled')
          .map((job: any) => ({
            ...job,
            result_url: sanitizeResultUrl(job.result_url)
          }));
        setQueuedJobs(clean);
      } catch (e) {
        console.error("Failed to rehydrate jobs:", e);
        localStorage.removeItem('vantix_queue');
      }
    }
    setIsHydrated(true);
  }, []);

  // Persistence: Save
  useEffect(() => {
    if (isHydrated) {
      localStorage.setItem('vantix_queue', JSON.stringify(queuedJobs));
    }
  }, [queuedJobs, isHydrated]);

  useEffect(() => {
    const checkServer = () => {
      checkStatus()
        .then(() => setServerStatus('online'))
        .catch(() => setServerStatus('offline'));
    };

    const fetchBalance = () => {
      getUserBalance().then(data => setBalance(data.balance)).catch(() => { });
    };

    checkServer();
    fetchBalance();
    const interval = setInterval(() => {
        checkServer();
        fetchBalance();
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Industrial Polling Loop
  useEffect(() => {
    const interval = setInterval(async () => {
      if (queuedJobs.length === 0) return;

      const updatedJobs = await Promise.all(
        queuedJobs.map(async (job) => {
          if (job.status === 'completed' || job.status === 'failed') return job;
          try {
            const status = await getJobStatus(job.id);
            return status ? { ...job, ...status } : job;
          } catch (e) {
            console.error("Polling stall:", e);
            return job;
          }
        })
      );
      setQueuedJobs(updatedJobs);
    }, 3000);
    return () => clearInterval(interval);
  }, [queuedJobs]);

  const handleLaunch = async (type: 'video' | 'ebook' | 'course') => {
    if (!topic) return alert("Vantix Input Error: Topic required.");

    try {
      let res;
      if (type === 'video') res = await generateVideo(topic);
      if (type === 'ebook') res = await generateEbook(topic);
      if (type === 'course') res = await generateCourse(topic);

      if (res && res.job_id) {
        setQueuedJobs(prev => [{ id: res.job_id, status: 'queued', type, topic, timestamp: new Date() }, ...prev]);
        setSuccessMessage(`${type.toUpperCase()} stream synchronized.`);
        // Refresh balance after deduction
        getUserBalance().then(data => setBalance(data.balance));
        setTimeout(() => setSuccessMessage(""), 3000);
      }
    } catch (error: any) {
      if (error?.message?.includes("402") || (error instanceof Response && error.status === 402)) {
         setShowRecharge(true);
      } else {
         console.error(error);
         alert("Factory Interruption: Check your Vantix Power / Backend status.");
      }
    }
  };

  const handleReload = async (amount: number) => {
    setIsRecharging(true);
    try {
      const data = await reloadCredits(amount);
      setBalance(data.balance);
      setShowRecharge(false);
      setSuccessMessage(`Added ${amount} credits to node.`);
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (e) {
      alert("Recharge Failed: Commercial Link Interrupted.");
    } finally {
      setIsRecharging(false);
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await cancelJob(jobId);
      // 🗑️ [PURGE] Remove from queue entirely — cancelled jobs create clutter
      setQueuedJobs(prev => prev.filter(j => j.id !== jobId));
    } catch (e) {
      // Remove from UI regardless — backend may have already purged it
      setQueuedJobs(prev => prev.filter(j => j.id !== jobId));
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="max-w-7xl space-y-16 pb-20"
    >
      {/* Welcome Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-8 py-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="industrial-badge">Vantix Node v1.0</span>
            <div className="h-px w-20 bg-emerald-500/20" />
          </div>
          <h1 className="text-6xl font-black tracking-tight text-white italic">VANTIX</h1>
          <p className="text-slate-400 text-xl max-w-2xl font-medium">Vantix orchestration for high-throughput autonomous media clusters.</p>
        </div>

        <div className="flex items-center gap-6">
          </Link>
          
          <div 
            onClick={() => setShowRecharge(true)}
            className="flex items-center gap-4 px-6 py-4 rounded-3xl glass-card border-emerald-500/20 bg-emerald-500/5 hover:bg-emerald-500/10 cursor-pointer transition-all animate-in fade-in slide-in-from-right-4"
          >
             <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400">
                <Coins size={20} className="animate-bounce" />
             </div>
             <div className="flex flex-col">
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest text-left">Industrial Power</span>
                <span className="text-xl font-bold text-white tabular-nums leading-none">
                  {balance !== null ? balance : <Loader2 size={16} className="animate-spin inline" />}
                </span>
             </div>
             <Plus size={16} className="text-emerald-500/50" />
          </div>

          <div className={`flex flex-col items-center gap-1.5 px-8 py-4 rounded-3xl glass-card border-none ${serverStatus === 'online' ? 'bg-emerald-500/10' : 'bg-rose-500/10'}`}>
             <div className="flex items-center gap-3">
                <Server size={18} className={serverStatus === 'online' ? 'text-emerald-400 accent-glow' : 'text-rose-400'} />
                <span className={`text-xs font-black uppercase tracking-[0.2em] ${serverStatus === 'online' ? 'text-emerald-400' : 'text-rose-400'}`}>{serverStatus}</span>
             </div>
             <span className="text-[8px] text-slate-500 font-bold uppercase">Vantix Pulse Heartbeat</span>
          </div>
        </div>
      </header>      {/* ⚠️ EPHEMERAL SHIELD WARNING */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="glass-card border-amber-500/20 bg-amber-500/5 p-6 rounded-[2rem] flex flex-col md:flex-row items-center gap-6 relative overflow-hidden"
      >
        <div className="p-4 rounded-2xl bg-amber-500/10 text-amber-500 shadow-inner">
          <ShieldAlert size={28} className="animate-pulse" />
        </div>
        <div className="space-y-1 text-center md:text-left">
          <h3 className="text-amber-500 font-black text-sm uppercase tracking-widest italic">Vantix Ephemeral Protocol Active</h3>
          <p className="text-slate-400 text-xs font-medium max-w-3xl leading-relaxed">To maintain zero-retention privacy and industrial cluster efficiency, all assets are automatically destroyed from the factory hard-drives exactly 24 hours after synthesis. <span className="text-amber-500/80 font-bold uppercase tracking-tighter">Download your productions immediately.</span></p>
        </div>
        <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
          <Clock size={120} />
        </div>
      </motion.div>

      {/* Global Input Node */}
      <section className="relative group max-w-4xl">
        <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded-[2.5rem] blur-2xl opacity-0 group-focus-within:opacity-100 transition-all" />
        <div className="relative">
          <input
            type="text"
            placeholder="Input topic, news vector, or research identifier..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="w-full monochrome-input rounded-[2rem] px-10 py-8 text-3xl font-bold bg-slate-900/60 backdrop-blur-3xl border-slate-800/80 outline-none placeholder-slate-700"
          />
          <div className="absolute right-6 top-1/2 -translate-y-1/2 flex items-center gap-3">
             <div className="industrial-badge bg-slate-950/80 border-slate-800">Primary Vector</div>
             <ArrowRight size={24} className="text-slate-700" />
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Rapid Action Clusters */}
        <div className="lg:col-span-1 space-y-6">
          <div className="flex items-center gap-2 mb-4">
             <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Action Synthesis</span>
             <div className="h-px flex-1 bg-slate-800/50" />
          </div>
          
          {[
            { type: 'video', label: 'Short-Video', icon: Play, color: 'emerald', desc: 'Viral visual synthesis.' },
            { type: 'ebook', label: 'E-Book Narrative', icon: Book, color: 'cyan', desc: 'Deep-knowledge layouts.' },
            { type: 'course', label: 'E-Course Factory', icon: GraduationCap, color: 'indigo', desc: 'Multi-chapter curriculum.' }
          ].map((action) => (
            <button
              key={action.type}
              onClick={() => handleLaunch(action.type as any)}
              className={`w-full glass-card p-6 rounded-3xl flex items-center justify-between group hover:border-${action.color}-500/50 transition-all text-left relative overflow-hidden`}
            >
              <div className={`absolute inset-y-0 left-0 w-1 bg-${action.color}-500 transform -translate-x-full group-hover:translate-x-0 transition-transform`} />
              <div className="flex items-center gap-5">
                <div className={`p-4 rounded-2xl bg-${action.color}-500/10 text-${action.color}-500`}>
                  <action.icon size={24} />
                </div>
                <div>
                  <h3 className="font-black text-sm uppercase tracking-widest text-white">{action.label}</h3>
                  <p className="text-[10px] text-slate-500 font-bold">{action.desc}</p>
                </div>
              </div>
              <ChevronRight size={18} className="text-slate-700 group-hover:text-white transition-colors" />
            </button>
          ))}

          <div className="p-8 glass-card rounded-[2rem] bg-emerald-500/5 border-emerald-500/10 space-y-4 mt-12">
             <div className="flex items-center gap-3 text-emerald-400">
                <ShieldCheck size={20} />
                <span className="text-[10px] font-black uppercase tracking-widest">Sovereign Vault</span>
             </div>
             <p className="text-[11px] text-slate-500 leading-relaxed font-medium">Production DNA is cryptographically secured. Credentials propagate autonomously across all factory synthesis tiers.</p>
          </div>
        </div>

        {/* Live Production Stream */}
        <div className="lg:col-span-2 space-y-8">
          <div className="flex items-center justify-between">
             <div className="flex items-center gap-4">
               <Activity size={20} className="text-emerald-500 accent-glow" />
               <h2 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Active Production Stream</h2>
             </div>
             <AnimatePresence>
                {successMessage && (
                  <motion.span 
                    initial={{ opacity: 0, y: 5 }} 
                    animate={{ opacity: 1, y: 0 }} 
                    exit={{ opacity: 0 }}
                    className="text-[10px] font-black text-emerald-400 uppercase italic"
                  >
                    // {successMessage}
                  </motion.span>
                )}
             </AnimatePresence>
          </div>

          <div className="space-y-4">
            <AnimatePresence mode="popLayout">
              {queuedJobs.length === 0 ? (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="glass-card p-20 rounded-[2.5rem] border-dashed border-slate-800/50 flex flex-col items-center justify-center text-center space-y-6"
                >
                   <div className="p-6 rounded-full bg-slate-900 border border-slate-800 text-slate-700">
                      <Zap size={32} />
                   </div>
                   <div className="space-y-1">
                      <h3 className="text-lg font-bold text-slate-500">Node Idle</h3>
                      <p className="text-sm text-slate-600 max-w-xs">Input a vector and synchronize a factory to begin industrial synthesis.</p>
                   </div>
                </motion.div>
              ) : (
                queuedJobs.map((job) => (
                  <motion.div
                    key={job.id}
                    layout
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="glass-card p-8 rounded-3xl flex items-center justify-between gap-6 hover:border-slate-700 transition-all group"
                  >
                    <div className="flex items-center gap-6 min-w-0 flex-1">
                      <div className={`p-4 rounded-2xl ${job.status === 'completed' ? 'bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)]' : job.status === 'failed' ? 'bg-rose-500 text-white' : 'bg-slate-900 text-slate-400'}`}>
                         {job.status === 'completed' ? <CheckCircle2 size={24} /> : job.status === 'failed' ? <AlertCircle size={24} /> : <Loader2 size={24} className="animate-spin" />}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-3 mb-1">
                           <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{job.type} Factory</span>
                           <span className="text-slate-800">|</span>
                           <span className="text-[9px] font-black text-slate-500 uppercase font-mono">{job.id.slice(0, 8)}</span>
                           {(job.status === 'queued' || job.status === 'processing') && (
                             <button 
                               onClick={() => handleCancelJob(job.id)}
                               className="ml-2 p-1 rounded-md bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white transition-all"
                               title="Cancel Synthesis"
                             >
                               <X size={10} />
                             </button>
                           )}
                        </div>
                        <h3 className="text-white font-bold text-lg truncate mb-1">{job.topic}</h3>
                        {job.progress_msg && <p className="text-[10px] text-emerald-500/80 font-black uppercase tracking-widest animate-pulse italic">📡 {job.progress_msg}</p>}
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-3">
                       <div className="text-[10px] font-black text-slate-500 uppercase flex items-center gap-2">
                          <Clock size={12} /> {new Date(job.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                       </div>
                       {job.status === 'completed' && (
                         <div className="flex gap-2">
                           {job.result_url && (
                              <a 
                                href={sanitizeResultUrl(job.result_url) || '#'}
                                download
                                className="px-5 py-2 rounded-xl bg-emerald-500 text-white text-[10px] font-black uppercase tracking-widest hover:bg-emerald-400 transition-all flex items-center gap-2"
                              >
                                <Zap size={12} /> Download Asset
                              </a>
                            )}
                         </div>
                       )}
                       {job.status === 'processing' && (
                         <div className="px-4 py-1 rounded-full bg-emerald-500/10 text-emerald-500 text-[8px] font-black uppercase tracking-widest border border-emerald-500/20">
                            Synthesizing
                         </div>
                       )}
                    </div>
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* 💳 RECHARGE MODAL */}
      <AnimatePresence>
        {showRecharge && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6 sm:p-0">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => !isRecharging && setShowRecharge(false)}
              className="absolute inset-0 bg-slate-950/80 backdrop-blur-md" 
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-[2.5rem] shadow-2xl overflow-hidden"
            >
              <div className="p-8 space-y-8">
                <div className="flex items-center justify-between">
                   <div className="flex items-center gap-3">
                      <div className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-400">
                         <Zap size={24} />
                      </div>
                      <h2 className="text-xl font-black text-white italic tracking-tight underline decoration-emerald-500/30 decoration-4 underline-offset-4">RECHARGE NODE</h2>
                   </div>
                   <button 
                     onClick={() => !isRecharging && setShowRecharge(false)}
                     className="p-2 rounded-xl hover:bg-slate-800 text-slate-500 transition-all"
                   >
                     <X size={20} />
                   </button>
                </div>

                <div className="space-y-4">
                  <p className="text-slate-400 text-sm font-medium">Inject industrial power to restore synthesis capabilities. Select a recharge vector:</p>
                  
                  <div className="grid grid-cols-1 gap-4">
                    {[
                      { amount: 100, price: '10', label: 'Starter Cell', bonus: 'Basic Power' },
                      { amount: 500, price: '45', label: 'Engine Core', bonus: '10% Extraction Bonus' },
                      { amount: 2000, price: '150', label: 'Industrial Grid', bonus: '25% Optimization' }
                    ].map((plan) => (
                      <button
                        key={plan.amount}
                        disabled={isRecharging}
                        onClick={() => handleReload(plan.amount)}
                        className="p-6 rounded-3xl border border-slate-800 hover:border-emerald-500/50 hover:bg-emerald-500/5 transition-all text-left flex items-center justify-between group disabled:opacity-50"
                      >
                         <div className="space-y-1">
                            <h4 className="text-white font-black text-xs uppercase tracking-widest">{plan.label}</h4>
                            <p className="text-[10px] text-slate-500 font-bold">{plan.amount} Credits // {plan.bonus}</p>
                         </div>
                         <div className="text-right">
                            <span className="text-xs font-black text-emerald-400 uppercase tracking-tighter italic">US ${plan.price}</span>
                            <div className="flex items-center justify-end text-[8px] text-slate-600 font-bold uppercase mt-1 group-hover:text-white transition-colors">
                               Init Transfer <ChevronRight size={10} />
                            </div>
                         </div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="p-6 rounded-3xl bg-slate-950/50 border border-slate-800/50 flex items-center gap-4">
                   <ShieldCheck size={20} className="text-slate-600" />
                   <p className="text-[10px] text-slate-600 font-medium leading-relaxed uppercase tracking-widest">Transactions secured by Vantix Cryptographic Ledger. Local simulation active.</p>
                </div>
              </div>
              
              {isRecharging && (
                <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm flex flex-col items-center justify-center space-y-4">
                   <Loader2 className="animate-spin text-emerald-500" size={40} />
                   <span className="text-[10px] font-black text-white uppercase tracking-[0.3em] animate-pulse">Synchronizing Ledger...</span>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
