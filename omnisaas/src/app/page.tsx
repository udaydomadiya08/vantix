'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Book, GraduationCap, Zap, Activity, Clock, Server, CheckCircle2, AlertCircle, Loader2, Settings, ChevronRight, ArrowRight, ShieldCheck, X, ShieldAlert, CreditCard, Plus, Coins } from "lucide-react";
import { generateVideo, generateEbook, generateCourse, checkStatus, getJobStatus, cancelJob, getUserBalance } from "@/lib/api";
import Link from "next/link";

export default function HomePage() {
  const [topic, setTopic] = useState("");
  const [queuedJobs, setQueuedJobs] = useState<any[]>([]); 
  const [serverStatus, setServerStatus] = useState<'online' | 'offline'>('offline');
  const [successMessage, setSuccessMessage] = useState("");
  const [isHydrated, setIsHydrated] = useState(false);

  const sanitizeResultUrl = (url: string | undefined): string | undefined => {
    if (!url) return url;
    const match = url.match(/(static\/.+\.\w+|courses\/.+\.\w+|final_video\/.+\.\w+)/);
    if (match) return `http://127.0.0.1:8000/download?path=${match[1]}`;
    if (url.startsWith('http')) return url;
    return undefined;
  };

  useEffect(() => {
    const saved = localStorage.getItem('vantix_queue');
    if (saved) {
      try {
        const jobs = JSON.parse(saved);
        const clean = jobs
          .filter((job: any) => job.status !== 'cancelled')
          .map((job: any) => ({ ...job, result_url: sanitizeResultUrl(job.result_url) }));
        setQueuedJobs(clean);
      } catch (e) {
        localStorage.removeItem('vantix_queue');
      }
    }
    setIsHydrated(true);
  }, []);

  useEffect(() => {
    if (isHydrated) localStorage.setItem('vantix_queue', JSON.stringify(queuedJobs));
  }, [queuedJobs, isHydrated]);

  useEffect(() => {
    const checkServer = () => {
      checkStatus().then(() => setServerStatus('online')).catch(() => setServerStatus('offline'));
    };
    checkServer();
    const interval = setInterval(checkServer, 10000);
    return () => clearInterval(interval);
  }, []);

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
            return job;
          }
        })
      );
      setQueuedJobs(updatedJobs);
    }, 3000);
    return () => clearInterval(interval);
  }, [queuedJobs]);

  const handleLaunch = async (type: 'video' | 'ebook' | 'course' | 'thumbnail') => {
    if (!topic) return alert("Vantix Input Error: Topic required.");
    try {
      let res;
      if (type === 'video') res = await generateVideo(topic);
      if (type === 'ebook') res = await generateEbook(topic);
      if (type === 'course') res = await generateCourse(topic);
      if (type === 'thumbnail') res = await generateThumbnail(topic);

      if (res && res.job_id) {
        setQueuedJobs(prev => [{ id: res.job_id, status: 'queued', type, topic, timestamp: new Date() }, ...prev]);
        setSuccessMessage(`${type.toUpperCase()} stream synchronized.`);
        setTimeout(() => setSuccessMessage(""), 3000);
      } else if (res && res.detail && res.detail.error === "vault_locked") {
         alert(`VAULT LOCKED: ${res.detail.message} - Please configure your Groq/OpenRouter keys in the API Vault.`);
         router.push("/settings/defaults"); // Redirect to settings
      }
    } catch (error: any) {
      if (error?.message?.includes("402") || (error instanceof Response && error.status === 402)) {
         alert("Insufficient Industrial Power. Please upgrade your node in the sidebar.");
      } else if (error?.message?.includes("428") || (error instanceof Response && error.status === 428)) {
         alert("VAULT LOCKED: Core AI keys missing. Please synchronize your API Vault.");
         router.push("/settings/defaults");
      } else {
         alert("Factory Interruption: Check your Vantix Power / Backend status.");
      }
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await cancelJob(jobId);
      setQueuedJobs(prev => prev.filter(j => j.id !== jobId));
    } catch (e) {
      setQueuedJobs(prev => prev.filter(j => j.id !== jobId));
    }
  };

  return (
    <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="max-w-7xl space-y-16 pb-20">
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
          <Link href="/settings/defaults" className="p-4 rounded-3xl glass-card text-slate-400 hover:text-white hover:border-emerald-500/50 transition-all group">
            <Settings size={28} className="group-hover:rotate-90 transition-transform" />
          </Link>
          <div className={`flex flex-col items-center gap-1.5 px-8 py-4 rounded-3xl glass-card border-none ${serverStatus === 'online' ? 'bg-emerald-500/10' : 'bg-rose-500/10'}`}>
             <div className="flex items-center gap-3">
                <Server size={18} className={serverStatus === 'online' ? 'text-emerald-400 accent-glow' : 'text-rose-400'} />
                <span className={`text-xs font-black uppercase tracking-[0.2em] ${serverStatus === 'online' ? 'text-emerald-400' : 'text-rose-400'}`}>{serverStatus}</span>
             </div>
             <span className="text-[8px] text-slate-500 font-bold uppercase">Vantix Pulse Heartbeat</span>
          </div>
        </div>
      </header>

      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="glass-card border-amber-500/20 bg-amber-500/5 p-6 rounded-[2rem] flex flex-col md:flex-row items-center gap-6 relative overflow-hidden">
        <div className="p-4 rounded-2xl bg-amber-500/10 text-amber-500 shadow-inner">
          <ShieldAlert size={28} className="animate-pulse" />
        </div>
        <div className="space-y-1 text-center md:text-left">
          <h3 className="text-amber-500 font-black text-sm uppercase tracking-widest italic">Vantix Ephemeral Protocol Active</h3>
          <p className="text-slate-400 text-xs font-medium max-w-3xl leading-relaxed">All assets destroyed exactly 24 hours after synthesis. Download immediately.</p>
        </div>
      </motion.div>

      <section className="relative group max-w-4xl">
        <input
          type="text"
          placeholder="Input topic, news vector, or research identifier..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="w-full monochrome-input rounded-[2rem] px-10 py-8 text-3xl font-bold bg-slate-900/60 backdrop-blur-3xl border-slate-800/80 outline-none placeholder-slate-700"
        />
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        <div className="lg:col-span-1 space-y-6">
          <div className="flex items-center gap-2 mb-4">
             <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Action Synthesis</span>
             <div className="h-px flex-1 bg-slate-800/50" />
          </div>
          {[
            { type: 'video', label: 'Short-Video', icon: Play, color: 'emerald', desc: 'Viral visual synthesis.' },
            { type: 'ebook', label: 'E-Book Narrative', icon: Book, color: 'cyan', desc: 'Deep-knowledge layouts.' },
            { type: 'course', label: 'E-Course Factory', icon: GraduationCap, color: 'indigo', desc: 'Multi-chapter curriculum.' },
            { type: 'thumbnail', label: 'Thumbnail Oracle', icon: LayoutGrid, color: 'rose', desc: 'High-CTR visual synthesis.' }
          ].map((action) => (
            <button key={action.type} onClick={() => handleLaunch(action.type as any)} className={`w-full glass-card p-6 rounded-3xl flex items-center justify-between group hover:border-${action.color}-500/50 transition-all text-left relative overflow-hidden`}>
              <div className="flex items-center gap-5 font-bold uppercase tracking-widest">
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
        </div>

        <div className="lg:col-span-2 space-y-8">
          <div className="flex items-center justify-between">
             <div className="flex items-center gap-4">
               <Activity size={20} className="text-emerald-500 accent-glow" />
               <h2 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Active Production Stream</h2>
             </div>
             <AnimatePresence>
                {successMessage && (
                  <motion.span initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="text-[10px] font-black text-emerald-400 uppercase italic">
                    {successMessage}
                  </motion.span>
                )}
             </AnimatePresence>
          </div>

          <div className="space-y-4">
            <AnimatePresence mode="popLayout">
              {queuedJobs.length === 0 ? (
                <div className="glass-card p-20 rounded-[2.5rem] border-dashed border-slate-800/50 flex flex-col items-center justify-center text-center space-y-6">
                   <Zap size={32} className="text-slate-700" />
                   <h3 className="text-lg font-bold text-slate-500 uppercase tracking-widest">Node Idle</h3>
                </div>
              ) : (
                queuedJobs.map((job) => (
                  <motion.div key={job.id} layout initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }} className="glass-card p-8 rounded-3xl flex items-center justify-between gap-6 hover:border-slate-700 transition-all group">
                    <div className="flex items-center gap-6 min-w-0 flex-1">
                      <div className={`p-4 rounded-2xl ${job.status === 'completed' ? 'bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)]' : job.status === 'failed' ? 'bg-rose-500 text-white' : 'bg-slate-900 text-slate-400'}`}>
                         {job.status === 'completed' ? <CheckCircle2 size={24} /> : job.status === 'failed' ? <AlertCircle size={24} /> : <Loader2 size={24} className="animate-spin" />}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-3 mb-1">
                           <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{job.type} Factory</span>
                           {job.status === 'queued' && <button onClick={() => handleCancelJob(job.id)} className="ml-2 p-1 rounded-md bg-rose-500/10 text-rose-500"><X size={10} /></button>}
                        </div>
                        <h3 className="text-white font-bold text-lg truncate mb-1 uppercase tracking-tight">{job.topic}</h3>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-3 font-mono text-[10px]">
                       <Clock size={12} className="text-slate-600" />
                       {job.status === 'completed' && job.result_url && (
                          <a href={sanitizeResultUrl(job.result_url) || '#'} className="px-5 py-2 rounded-xl bg-emerald-500/10 text-emerald-500 text-[10px] font-black uppercase tracking-widest hover:bg-emerald-500 hover:text-white transition-all">Download</a>
                       )}
                    </div>
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
