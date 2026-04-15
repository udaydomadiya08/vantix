'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Play, Book, GraduationCap, Zap, Activity, Clock, Server, 
  CheckCircle2, AlertCircle, Loader2, Settings, ChevronRight, 
  ArrowRight, ShieldCheck, X, ShieldAlert, CreditCard, Plus, 
  Coins, LayoutGrid, Sparkles, Globe, Cpu, BarChart3, Rocket, 
  Hourglass, Flame
} from "lucide-react";
import { 
  generateVideo, generateEbook, generateCourse, generateThumbnail, 
  checkStatus, getJobStatus, cancelJob, getUserBalance 
} from "@/lib/api";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

// --- 🏙️ [COMPONENT] VANTIX LANDING NODE ---
function LandingPage() {
  const router = useRouter();

  const factories = [
    { 
      title: "Short-Video Factory", 
      label: "Viral Synthesis", 
      icon: Play, 
      color: "emerald",
      path: "/shorts",
      desc: "Generate high-retention viral content using industrial-grade motion templates and AI narration."
    },
    { 
      title: "E-Book Synthesizer", 
      label: "Deep Narrative", 
      icon: Book, 
      color: "cyan",
      path: "/ebooks",
      desc: "Transform topics into comprehensive, multi-chapter industrial guides with AI-generated art." 
    },
    { 
      title: "E-Course Foundry", 
      label: "Autonomous Curriculum", 
      icon: GraduationCap, 
      color: "indigo",
      path: "/courses",
      desc: "Orchestrate entire educational streams with logical structure and high-fidelity layouts." 
    }
  ];

  return (
    <div className="min-h-screen bg-[#020617] text-white selection:bg-emerald-500/30 font-sans">
      {/* 🚀 Hero Section */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[600px] bg-emerald-500/5 blur-[120px] rounded-full" />
        <div className="max-w-7xl mx-auto text-center relative space-y-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-black uppercase tracking-[0.2em]"
          >
            <Sparkles size={14} />
            Autonomous Media Synthesis Active
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-6xl md:text-8xl font-black italic tracking-tighter leading-none"
          >
            VANTIX <br />
            <span className="text-emerald-500 underline decoration-emerald-500/20 decoration-8 underline-offset-8">INDUSTRIAL</span>
          </motion.h1>

          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-slate-400 text-xl md:text-2xl max-w-3xl mx-auto font-medium leading-relaxed"
          >
            Orchestrate high-throughput media clusters with zero operating costs. 
            The world's first BYOK-native autonomous synthesis platform.
          </motion.p>

          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col md:flex-row items-center justify-center gap-6 pt-8"
          >
            <button 
              onClick={() => router.push('/auth/login')}
              className="px-10 py-5 rounded-[2rem] bg-emerald-500 text-white font-black uppercase tracking-widest hover:scale-105 transition-all shadow-[0_0_30px_rgba(16,185,129,0.4)] flex items-center gap-3"
            >
              Initiate Connection
              <ArrowRight size={20} />
            </button>
            <button 
              className="px-10 py-5 rounded-[2rem] bg-slate-900 border border-slate-800 text-slate-400 font-black uppercase tracking-widest hover:bg-slate-800 transition-all font-sans"
            >
              View Documentation
            </button>
          </motion.div>
        </div>
      </section>

      {/* 🏭 Factory Showcase */}
      <section className="py-24 px-6 bg-slate-900/40 border-y border-slate-800">
        <div className="max-w-7xl mx-auto space-y-16">
          <div className="text-center space-y-4">
            <h2 className="text-xs font-black text-emerald-400 uppercase tracking-[0.3em]">Industrial Nodes</h2>
            <p className="text-4xl font-black italic tracking-tight">The Synthesis Cluster</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {factories.map((factory, i) => (
              <Link
                key={factory.title}
                href={factory.path}
                className="block"
              >
                <motion.div 
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="glass-card p-10 rounded-[3rem] border-slate-800 hover:border-emerald-500/50 transition-all flex flex-col h-full space-y-6 group cursor-pointer"
                >
                  <div className={`p-4 rounded-2xl bg-${factory.color}-500/10 text-${factory.color}-400 w-fit group-hover:scale-110 transition-transform`}>
                    <factory.icon size={32} />
                  </div>
                  <div className="space-y-4">
                    <div>
                      <span className={`text-[10px] font-black text-${factory.color}-500 uppercase tracking-widest block mb-1 underline decoration-2 underline-offset-4`}>{factory.label}</span>
                      <h3 className="text-2xl font-black italic tracking-tight">{factory.title}</h3>
                    </div>
                    <p className="text-slate-500 font-medium text-sm leading-relaxed">{factory.desc}</p>
                  </div>
                </motion.div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* 🛠️ Technical Node */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
          <div className="space-y-10">
            <div className="space-y-4">
              <h2 className="text-xs font-black text-emerald-400 uppercase tracking-[0.3em]">Economic Protocol</h2>
              <p className="text-5xl font-black italic tracking-tight leading-tight">Zero Operating Costs. <br />Infinite Scale.</p>
            </div>
            
            <div className="space-y-8">
              {[
                { icon: Cpu, title: "Bring Your Own Key (BYOK)", desc: "Link your Groq and OpenRouter keys directly to the VANTIX vault. We process, you own the costs." },
                { icon: BarChart3, title: "Synthesis Taxation", desc: "Pay only for what you synthesize using our industrial credit ledger. No monthly subscriptions." },
                { icon: ShieldCheck, title: "Ephemeral Security", desc: "All data is purged every 24 hours. Minimal footprint, maximum privacy." }
              ].map(item => (
                <div key={item.title} className="flex gap-6">
                   <div className="p-3 h-fit rounded-xl bg-slate-900 border border-slate-800 text-emerald-400">
                      <item.icon size={24} />
                   </div>
                   <div className="space-y-1">
                      <h4 className="font-black italic uppercase tracking-wider">{item.title}</h4>
                      <p className="text-slate-500 text-sm font-medium">{item.desc}</p>
                   </div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative">
             <div className="absolute inset-0 bg-emerald-500/10 blur-[100px] rounded-full" />
             <div className="glass-card p-8 rounded-[3rem] border-slate-800 bg-slate-900/60 relative overflow-hidden font-sans">
                <div className="space-y-6">
                   <div className="flex items-center justify-between border-b border-slate-800 pb-6">
                      <div className="flex items-center gap-3">
                         <div className="h-4 w-4 rounded-full bg-emerald-500 animate-pulse" />
                         <span className="text-xs font-black uppercase tracking-widest text-white">Production Log</span>
                      </div>
                      <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">v1.1.0-Orchestra</span>
                   </div>
                   
                   <div className="space-y-4 font-mono text-[10px]">
                      <div className="text-emerald-500/60 leading-relaxed">[NODE_INFO] Initializing VANTIX Synthesis Engine...</div>
                      <div className="text-slate-400 leading-relaxed">[VAULT_AUTH] BYOK Handshake Successful: Groq v3-Llama-70b</div>
                      <div className="text-slate-400 leading-relaxed">[TRAFFIC] Load Balancing: High Efficiency Mode Active</div>
                      <div className="text-cyan-400 leading-relaxed">[QUEUE] Job ID: 8ff2... Position: #1 (Ready in 45s)</div>
                      <div className="text-slate-400/50 leading-relaxed">--------------------------------------------------</div>
                      <div className="text-white animate-pulse">_</div>
                   </div>
                </div>
             </div>
          </div>
        </div>
      </section>

      {/* 💳 Pricing Preview */}
      <section className="py-24 px-6 bg-slate-900/40 border-t border-slate-800 text-center">
         <div className="max-w-4xl mx-auto space-y-12">
            <div className="space-y-4">
               <h2 className="text-xs font-black text-emerald-400 uppercase tracking-[0.3em]">Commercial Link</h2>
               <p className="text-4xl font-black italic tracking-tight">Industrial Power Tiers</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
               {['Starter ($10)', 'Engine Core ($45)', 'Industrial Grid ($150)'].map(tier => (
                 <div key={tier} className="p-6 rounded-2xl bg-slate-900 border border-slate-800 text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-emerald-400 hover:border-emerald-500/50 transition-all cursor-default">
                   {tier}
                 </div>
               ))}
            </div>

            <button 
              onClick={() => router.push('/auth/login')}
              className="px-12 py-6 rounded-[2.5rem] bg-emerald-500 text-white font-black uppercase tracking-widest hover:brightness-110 transition-all shadow-xl group"
            >
              Start Synthesis Now
              <Plus size={18} className="inline-block ml-3 group-hover:rotate-90 transition-transform" />
            </button>
         </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-900 text-center">
         <p className="text-[10px] font-black text-slate-700 uppercase tracking-[0.5em]">VANTIX BYOK-NATIVE MEDIA CLUSTER © 2026</p>
      </footer>
    </div>
  );
}

// --- 🏗️ [COMPONENT] VANTIX INDUSTRIAL DASHBOARD ---
function Dashboard() {
  const [topic, setTopic] = useState("");
  const [queuedJobs, setQueuedJobs] = useState<any[]>([]); 
  const [serverStatus, setServerStatus] = useState<'online' | 'offline'>('offline');
  const [successMessage, setSuccessMessage] = useState("");
  const [quotaError, setQuotaError] = useState<any>(null);
  const [isHydrated, setIsHydrated] = useState(false);
  const router = useRouter();

  const sanitizeResultUrl = (url: string | undefined): string | undefined => {
    if (!url) return url;
    const match = url.match(/(static\/.+\.\w+|courses\/.+\.\w+|final_video\/.+\.\w+)/);
    if (match) return `https://udaydomadiya-vantix-core.hf.space/download?path=${match[1]}`;
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
    // 🛡️ [SYNC LOCK] Only save to local storage AFTER we have loaded from it
    if (isHydrated && queuedJobs.length >= 0) {
       localStorage.setItem('vantix_queue', JSON.stringify(queuedJobs));
    }
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
    setSuccessMessage(`⚙️ Synthesizing ${type.toUpperCase()} node...`);
    
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
         router.push("/settings/api"); 
      }
    } catch (error: any) {
      setSuccessMessage("");
      const status = error instanceof Response ? error.status : (error.response?.status || 0);
      
      if (status === 429) {
          setQuotaError(true);
      } else if (status === 402) {
         alert("INSUFFICIENT POWER: Your industrial balance is depleted. Please recharge your node to continue synthesis.");
         router.push("/recharge");
      } else if (status === 428) {
         alert("VAULT LOCKED: Core AI keys (Groq/OpenRouter) missing. Redirecting to your Sovereign Vault...");
         router.push("/settings/api");
      } else {
         alert("FACTORY INTERRUPTION: Infrastructure unreachable. Check your Vantix Power / Backend status.");
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

  const formatWaitTime = (seconds: number) => {
    if (!seconds) return "Calculating...";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const hasHeavyTraffic = queuedJobs.some(j => j.position > 1);

  return (
    <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="max-w-7xl space-y-16 pb-20 font-sans">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-8 py-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <span className="industrial-badge">Vantix Node v1.1.0</span>
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

      {/* 🚦 PLATFORM HEALTH & QUOTA ALERTS */}
      <AnimatePresence>
        {hasHeavyTraffic && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
            <div className="bg-indigo-500/10 border border-indigo-500/20 p-5 rounded-3xl flex items-center gap-4 text-indigo-400">
               <Hourglass size={20} className="animate-spin-slow" />
               <div className="flex-1">
                 <p className="text-xs font-black uppercase tracking-widest">Industrial Congestion Detected</p>
                 <p className="text-[10px] font-medium opacity-60">Wait times may be higher due to global synthesis traffic. Current load: Balanced.</p>
               </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="glass-card border-amber-500/20 bg-amber-500/5 p-6 rounded-[2rem] flex flex-col md:flex-row items-center gap-6 relative overflow-hidden">
        <div className="p-4 rounded-2xl bg-amber-500/10 text-amber-500 shadow-inner">
          <ShieldAlert size={28} className="animate-pulse" />
        </div>
        <div className="space-y-1 text-center md:text-left font-sans">
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
          className="w-full monochrome-input rounded-[2rem] px-10 py-8 text-3xl font-bold bg-slate-900/60 backdrop-blur-3xl border-slate-800/80 outline-none placeholder-slate-700 font-sans"
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
              <div className="flex items-center gap-5 font-bold uppercase tracking-widest font-sans">
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
                  <motion.div key={job.id} layout initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }} className="glass-card p-8 rounded-3xl flex items-center justify-between gap-6 hover:border-slate-700 transition-all group overflow-hidden relative">
                    {job.status === 'queued' && (
                        <div className="absolute top-0 left-0 h-1 bg-emerald-500/30 w-full overflow-hidden">
                            <motion.div initial={{ x: "-100%" }} animate={{ x: "100%" }} transition={{ repeat: Infinity, duration: 2, ease: "linear" }} className="h-full w-1/3 bg-emerald-500" />
                        </div>
                    )}

                    <div className="flex items-center gap-6 min-w-0 flex-1">
                      <div className={`p-4 rounded-2xl ${job.status === 'completed' ? 'bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)]' : job.status === 'failed' ? 'bg-rose-500 text-white' : 'bg-slate-900 text-slate-400'}`}>
                         {job.status === 'completed' ? <CheckCircle2 size={24} /> : job.status === 'failed' ? <AlertCircle size={24} /> : <Loader2 size={24} className="animate-spin" />}
                      </div>
                      <div className="min-w-0 font-sans">
                        <div className="flex items-center gap-3 mb-1">
                           <span className="text-[9px] font-black text-slate-500 uppercase tracking-widest">{job.type} Factory</span>
                           {job.status === 'queued' && <button onClick={() => handleCancelJob(job.id)} className="ml-2 p-1 rounded-md bg-rose-500/10 text-rose-500"><X size={10} /></button>}
                        </div>
                        <h3 className="text-white font-bold text-lg truncate mb-1 uppercase tracking-tight">{job.topic}</h3>
                        
                        {job.status === 'queued' && (
                           <div className="flex items-center gap-4">
                             <div className="flex items-center gap-1.5 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
                               <Server size={10} />
                               Position: #{job.position || 1}
                             </div>
                             <div className="flex items-center gap-1.5 text-[10px] font-black text-slate-500 uppercase tracking-widest">
                               <Clock size={10} />
                               Wait: {formatWaitTime(job.est_wait)}
                             </div>
                           </div>
                        )}
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

      {/* 🛡️ QUOTA EXCEEDED MODAL */}
      <AnimatePresence>
        {quotaError && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/80 backdrop-blur-md">
            <motion.div initial={{ opacity: 0, scale: 0.9, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.9 }} className="glass-card max-w-lg w-full p-10 rounded-[3rem] border-rose-500/30 text-center space-y-8">
               <div className="p-6 rounded-full bg-rose-500/10 text-rose-500 w-fit mx-auto shadow-[0_0_30px_rgba(244,63,94,0.2)]">
                  <Flame size={48} className="animate-pulse" />
               </div>
               <div className="space-y-4">
                  <h2 className="text-4xl font-black italic tracking-tighter uppercase text-white leading-none">Industrial Quota <br /> Reached</h2>
                  <p className="text-slate-400 font-medium leading-relaxed">Your synthesis engine is cooling down. Standard nodes are limited to 3 synthesis jobs per industrial hour to ensure global stability.</p>
               </div>
               
               <div className="p-6 rounded-3xl bg-slate-900/50 border border-slate-800 space-y-2">
                  <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Cooling Period Active</p>
                  <p className="text-xl font-bold text-white tabular-nums">Next slot in ~15 minutes</p>
               </div>

               <button onClick={() => setQuotaError(null)} className="w-full py-5 rounded-[2rem] bg-rose-500 text-white font-black uppercase tracking-widest hover:brightness-110 transition-all">
                  Understood
               </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function RootPage() {
  const { isAuthenticated } = useAuth();
  
  if (isAuthenticated) {
    return <Dashboard />;
  }
  
  return <LandingPage />;
}
