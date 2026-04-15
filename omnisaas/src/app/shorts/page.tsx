'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Smartphone, Monitor, User, Wand2, Loader2, Video, FileText, Newspaper, Target, Info, ChevronRight, Zap, Image as ImageIcon, X, CheckCircle2 } from "lucide-react";
import { generateVideo, generateThumbnail, getJobStatus, cancelJob, getUserDefaults } from "@/lib/api";

type ProductionMode = 'topic' | 'script' | 'news' | 'niche';

export default function ShortsPage() {
    const [mode, setMode] = useState<ProductionMode>("topic");
    const [topic, setTopic] = useState("");
    const [script, setScript] = useState("");
    const [niche, setNiche] = useState("Finance");
    const [horizontal, setHorizontal] = useState(false);
    const [withAvatar, setWithAvatar] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isGeneratingThumb, setIsGeneratingThumb] = useState(false);
    const [activeJobId, setActiveJobId] = useState<string | null>(null);
    const [jobStatus, setJobStatus] = useState<any>(null);

    // 🧬 Inherit Settings from Vantix Vault
    useEffect(() => {
        let isMounted = true;
        getUserDefaults().then(data => {
            if (isMounted && data && data.video) {
                setHorizontal(data.video.horizontal);
                setWithAvatar(data.video.include_avatar);
            }
        }).catch(console.error);
        return () => { isMounted = false; };
    }, []);

    // 🛰️ Synthesis Tracking Loop
    useEffect(() => {
        const interval = setInterval(async () => {
            if (!activeJobId) return;
            try {
                const status = await getJobStatus(activeJobId);
                if (status) {
                    setJobStatus(status);
                }
            } catch (e) {
                console.error("Tracking stall:", e);
            }
        }, 3000);
        return () => clearInterval(interval);
    }, [activeJobId]);

    const handleLaunch = async () => {
        const finalTopic = mode === 'niche' ? niche : topic;
        const config: any = { 
            mode, 
            horizontal, 
            avatar: withAvatar,
            script: mode === 'script' ? script : null,
            niche: mode === 'niche' ? niche : null
        };

        if (isProcessing) return; // 🛡️ [GUARD] Prevent Double-Fire
        setIsProcessing(true);
        setActiveJobId(null);
        setJobStatus(null);

        try {
            console.log("🚀 [FACTORY]: Initiating Short-Video Production...", finalTopic);
            const res = await generateVideo(finalTopic, config);
            
            if (res && res.job_id) {
                console.log("✅ [FACTORY]: Production Stream Active. Job ID:", res.job_id);
                setActiveJobId(res.job_id);
                const saved = localStorage.getItem('vantix_queue');
                const jobs = saved ? JSON.parse(saved) : [];
                localStorage.setItem('vantix_queue', JSON.stringify([{ id: res.job_id, status: 'queued', type: 'video', topic: finalTopic, timestamp: new Date() }, ...jobs]));
                setSuccessMessage("🚀 Production stream initiated successfully!");
                setTimeout(() => setSuccessMessage(""), 5000);

                // 🎨 [OPTIONAL] High-CTR Thumbnail Synthesis (Sovereign Node)
                try {
                    await generateThumbnail(finalTopic);
                } catch (tErr) {
                    console.warn("🎨 [THUMBNAIL]: Independent node interruption.", tErr);
                }
            }
        } catch (error: any) {
            // 🛡️ [FILTER] If a job has already started, ignore secondary network noise
            if (activeJobId) {
                console.log("📡 [INFRASTRUCTURE]: Secondary network noise filtered.");
                return;
            }
            const status = error.status || (error instanceof Response ? error.status : (error.response?.status || 0));
            if (status === 402) {
                alert("INSUFFICIENT POWER: Industrial balance depleted. Please recharge your node.");
            } else if (status === 428) {
                // 🛰️ [HEAL] Industrial Identity Synchronization
                const stored = localStorage.getItem("vantix_api_keys");
                if (stored) {
                    try {
                        const keys = JSON.parse(stored);
                        const { syncUserKeys } = await import("@/lib/api");
                        await syncUserKeys(keys);
                        console.log("🛠️ [HEAL]: Identity Synced. Retrying production stream...");
                        return handleLaunch(); // Recursive Auto-Retry (Silent)
                    } catch (e) {
                        console.error("Vault Heal Failed:", e);
                    }
                }
                alert("VAULT LOCKED: Groq/OpenRouter keys missing. Please synchronize manually in the Sovereign Vault.");
            } else if (status === 422) {
                const detail = JSON.stringify(error.detail);
                alert(`UNPROCESSABLE IDENTITY: The server rejected this production cluster. DETAIL: ${detail}`);
            } else {
                alert("INDUSTRIAL INTERRUPTION: Infrastructure node unreachable. Check backend status.");
            }
        } finally {
            setIsProcessing(false);
        }
    };

    const handleThumbnailEntry = async () => {
        const targetTopic = mode === 'niche' ? niche : topic;
        if (!targetTopic) return alert("Vantix Error: Topic node required for thumbnail synthesis.");

        setIsGeneratingThumb(true);
        setActiveJobId(null);
        setJobStatus(null);

        try {
            const res = await generateThumbnail(targetTopic);
            if (res && res.job_id) {
                setActiveJobId(res.job_id);
                const saved = localStorage.getItem('vantix_queue');
                const jobs = saved ? JSON.parse(saved) : [];
                localStorage.setItem('vantix_queue', JSON.stringify([{ id: res.job_id, status: 'queued', type: 'thumbnail', topic: targetTopic, timestamp: new Date() }, ...jobs]));
            }
        } catch (e) {
            alert("Industrial Interruption: Thumbnail node failed.");
        } finally {
            setIsGeneratingThumb(false);
        }
    };

    const handleCancel = async () => {
        if (!activeJobId) return;
        try {
            await cancelJob(activeJobId);
            setJobStatus((prev: any) => ({ ...prev, status: 'cancelled' }));
        } catch (e) {
            console.error("Kill signal failed:", e);
        }
    };

    const modes = [
        { id: 'topic', label: 'Narrative Flow', icon: Sparkles, desc: 'Concept to viral script.' },
        { id: 'script', label: 'Hardcoded Script', icon: FileText, desc: 'Precise visual control.' },
        { id: 'news', label: 'Hyper-News', icon: Newspaper, desc: 'Real-time research mode.' },
        { id: 'niche', label: 'Trend Capture', icon: Target, desc: 'Niche-specific discovery.' },
    ];

    const niches = ["Finance", "Technology", "Health", "Motivation", "History", "Luxury"];

    return (
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-6xl space-y-12 pb-20"
        >
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <span className="industrial-badge">Short Video Engine</span>
                        <div className="h-px w-12 bg-emerald-500/30" />
                    </div>
                    <h1 className="text-5xl font-black tracking-tighter text-white flex items-center gap-4">
                        <Video className="text-emerald-500 accent-glow" size={40} />
                        Production Cockpit
                    </h1>
                    <p className="text-slate-400 text-lg max-w-xl">Multi-vector synthesis for high-throughput social content streams.</p>
                </div>
            </header>

            {/* Mode Selector */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {modes.map((m) => (
                    <button
                        key={m.id}
                        onClick={() => setMode(m.id as ProductionMode)}
                        className={`glass-card p-6 rounded-3xl flex flex-col items-center text-center gap-4 transition-all group relative overflow-hidden ${mode === m.id ? 'border-emerald-500/50 bg-emerald-500/5' : 'hover:border-slate-700'}`}
                    >
                        {mode === m.id && <div className="absolute inset-x-0 bottom-0 h-1 bg-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.5)]" />}
                        <m.icon size={28} className={mode === m.id ? 'text-emerald-500 accent-glow' : 'text-slate-500 group-hover:text-slate-300'} />
                        <div className="space-y-1">
                            <div className={`text-[11px] font-black uppercase tracking-[0.2em] ${mode === m.id ? 'text-emerald-400' : 'text-slate-400'}`}>{m.label}</div>
                            <div className="text-[10px] text-slate-600 font-bold leading-tight hidden md:block">{m.desc}</div>
                        </div>
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
                <div className="lg:col-span-2 space-y-8">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={mode}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            className="glass-card p-8 md:p-10 rounded-[2.5rem] space-y-8"
                        >
                            {mode === 'topic' || mode === 'news' ? (
                                <div className="space-y-6">
                                    <div className="flex items-center justify-between">
                                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">
                                            {mode === 'topic' ? 'Narrative Concept' : 'Source Intelligence Retrieval'}
                                        </label>
                                        <span className="industrial-badge text-[8px] opacity-50">Active Prompt Layer</span>
                                    </div>
                                    <textarea
                                        value={topic}
                                        onChange={(e) => setTopic(e.target.value)}
                                        placeholder={mode === 'topic' ? "What is the core message? (e.g., 'The dark side of coffee production')" : "Enter news headline or source URL..."}
                                        className="w-full monochrome-input rounded-2xl p-6 text-white min-h-[200px] text-xl leading-relaxed outline-none"
                                    />
                                </div>
                            ) : mode === 'script' ? (
                                <div className="space-y-6">
                                    <div className="flex items-center justify-between">
                                        <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Manual Directive Script</label>
                                        <span className="industrial-badge text-[8px] opacity-50">Literal Orchestration</span>
                                    </div>
                                    <textarea
                                        value={script}
                                        onChange={(e) => setScript(e.target.value)}
                                        placeholder="Paste your formatted script here..."
                                        className="w-full monochrome-input rounded-2xl p-6 text-white min-h-[300px] text-sm font-mono leading-relaxed outline-none"
                                    />
                                    <div className="flex items-center gap-2 p-4 bg-slate-950/50 rounded-2xl border border-slate-800">
                                        <Info size={14} className="text-emerald-500" />
                                        <p className="text-[10px] text-slate-500 italic uppercase tracking-wider">The engine will JIT-coordinate assets to match your narrative pace.</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em]">Trend-Vector Targeting</label>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                        {niches.map(n => (
                                            <button
                                                key={n}
                                                onClick={() => setNiche(n)}
                                                className={`p-4 rounded-2xl border text-[10px] font-black uppercase tracking-widest transition-all ${niche === n ? 'bg-emerald-500/10 border-emerald-500 text-emerald-400 shadow-lg' : 'bg-slate-950/30 border-slate-800 text-slate-500 hover:border-slate-700'}`}
                                            >
                                                {n}
                                            </button>
                                        ))}
                                    </div>
                                    <input
                                        type="text"
                                        placeholder="Add custom niche modifiers..."
                                        value={topic}
                                        onChange={(e) => setTopic(e.target.value)}
                                        className="w-full monochrome-input rounded-xl px-6 py-4 text-sm outline-none"
                                    />
                                </div>
                            )}
                        </motion.div>
                    </AnimatePresence>

                    {/* Layout Controls */}
                    <div className="grid grid-cols-2 gap-4">
                        <button
                            onClick={() => setHorizontal(false)}
                            className={`glass-card flex flex-col items-center gap-4 p-8 rounded-3xl transition-all relative overflow-hidden ${!horizontal ? 'border-emerald-500/50 bg-emerald-500/5' : ''}`}
                        >
                             {!horizontal && <div className="absolute top-0 right-0 p-2"><Zap size={12} className="text-emerald-500 accent-glow" /></div>}
                            <Smartphone size={32} className={!horizontal ? 'text-emerald-500 accent-glow' : 'text-slate-600'} />
                            <div className={`text-[10px] font-black uppercase tracking-[0.2em] ${!horizontal ? 'text-white' : 'text-slate-500'}`}>Vertical (9:16)</div>
                        </button>
                        <button
                            onClick={() => setHorizontal(true)}
                            className={`glass-card flex flex-col items-center gap-4 p-8 rounded-3xl transition-all relative overflow-hidden ${horizontal ? 'border-emerald-500/50 bg-emerald-500/5' : ''}`}
                        >
                            {horizontal && <div className="absolute top-0 right-0 p-2"><Zap size={12} className="text-emerald-500 accent-glow" /></div>}
                            <Monitor size={32} className={horizontal ? 'text-emerald-500 accent-glow' : 'text-slate-600'} />
                            <div className={`text-[10px] font-black uppercase tracking-[0.2em] ${horizontal ? 'text-white' : 'text-slate-500'}`}>Horizontal (16:9)</div>
                        </button>
                    </div>
                </div>

                <div className="space-y-8">
                    {/* Settings Summary Card */}
                    <div className="glass-card rounded-[2.5rem] p-8 space-y-8 sticky top-8">
                        <div className="space-y-6">
                            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                Model Parameters
                            </h3>
                            
                            <button
                                onClick={() => setWithAvatar(!withAvatar)}
                                className={`w-full flex items-center justify-between p-5 rounded-2xl border transition-all ${withAvatar ? 'bg-emerald-500/10 border-emerald-500 text-white shadow-lg' : 'bg-slate-950/30 border-slate-800 text-slate-500 hover:border-slate-700'}`}
                            >
                                <div className="flex items-center gap-3">
                                    <User size={18} className={withAvatar ? 'text-emerald-400' : 'text-slate-600'} />
                                    <span className="font-black text-[10px] uppercase tracking-widest">AI Presence</span>
                                </div>
                                <div className={`w-10 h-5 rounded-full relative transition-all ${withAvatar ? 'bg-emerald-500' : 'bg-slate-800'}`}>
                                    <div className={`absolute top-1 w-3 h-3 rounded-full bg-white transition-all ${withAvatar ? 'left-6' : 'left-1'}`} />
                                </div>
                            </button>
                        </div>
                    </div>

                    <div className="p-6 bg-slate-950/50 rounded-2xl border border-slate-800/50 space-y-5">
                        <div className="flex items-center gap-3 text-emerald-400">
                            <Sparkles size={16} />
                            <span className="text-[10px] font-black uppercase tracking-[0.2em]">DNA Summary</span>
                        </div>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center text-[10px] uppercase font-bold">
                                <span className="text-slate-500">Node</span>
                                <span className="text-slate-200">Short Video</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] uppercase font-bold">
                                <span className="text-slate-500">Engine</span>
                                <span className="text-emerald-500">{mode}</span>
                            </div>
                            <div className="flex justify-between items-center text-[10px] uppercase font-bold">
                                <span className="text-slate-500">Visuals</span>
                                <span className="text-slate-200">{horizontal ? '16:9' : '9:16'}</span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        <button
                            onClick={handleLaunch}
                            disabled={isProcessing || isGeneratingThumb}
                            className="relative group overflow-hidden bg-white text-black py-6 rounded-2xl font-black text-xs uppercase tracking-[0.2em] shadow-2xl transition-all active:scale-95 disabled:opacity-50"
                        >
                            <div className="absolute inset-0 bg-emerald-500 transform -translate-x-full group-hover:translate-x-0 transition-transform" />
                            <div className="relative flex items-center justify-center gap-2 group-hover:text-white transition-colors">
                                {isProcessing ? <Loader2 className="animate-spin" size={16} /> : <Wand2 size={16} />}
                                {isProcessing ? 'Working...' : 'Launch Video'}
                            </div>
                        </button>
                        <button
                            onClick={handleThumbnailEntry}
                            disabled={isProcessing || isGeneratingThumb}
                            className="relative group overflow-hidden bg-slate-900 text-white border border-slate-700 py-6 rounded-2xl font-black text-xs uppercase tracking-[0.2em] shadow-2xl transition-all active:scale-95 disabled:opacity-50"
                        >
                            <div className="absolute inset-0 bg-indigo-600 transform translate-y-full group-hover:translate-y-0 transition-transform" />
                            <div className="relative flex items-center justify-center gap-2 transition-colors">
                                {isGeneratingThumb ? <Loader2 className="animate-spin" size={16} /> : <ImageIcon size={16} />}
                                {isGeneratingThumb ? 'Rendering...' : 'Thumbnail'}
                            </div>
                        </button>
                    </div>
                    
                    <div className="flex items-center gap-2 justify-center text-[9px] text-slate-600 font-black uppercase tracking-widest">
                        <ChevronRight size={10} className="text-emerald-500" />
                        Industrial Cluster: Graduation v101.5
                    </div>

                    {/* 🛰️ REAL-TIME PRODUCTION TRACKER */}
                    <AnimatePresence>
                        {activeJobId && (
                            <motion.div 
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="glass-card p-8 rounded-[2rem] border-emerald-500/20 bg-emerald-500/5 space-y-6"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg ${jobStatus?.status === 'completed' ? 'bg-emerald-500 text-white' : jobStatus?.status === 'cancelled' ? 'bg-rose-500 text-white' : 'bg-slate-900 text-emerald-500'}`}>
                                            {jobStatus?.status === 'completed' ? <CheckCircle2 size={16} /> : jobStatus?.status === 'cancelled' ? <X size={16} /> : <Loader2 size={16} className="animate-spin" />}
                                        </div>
                                        <h4 className="text-[10px] font-black uppercase tracking-[0.2em] text-white">Live Synthesis Tracker</h4>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className="text-[9px] font-mono text-slate-500">ID: {activeJobId.slice(0, 8)}</span>
                                        {(jobStatus?.status === 'queued' || jobStatus?.status === 'processing') && (
                                            <button 
                                                onClick={handleCancel}
                                                className="p-1.5 rounded-md bg-rose-500/10 text-rose-500 hover:bg-rose-500 hover:text-white transition-all"
                                                title="Kill Process"
                                            >
                                                <X size={12} />
                                            </button>
                                        )}
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex items-center justify-between text-[10px] font-bold uppercase">
                                        <span className="text-slate-500">Node Status</span>
                                        <span className={jobStatus?.status === 'completed' ? 'text-emerald-400' : 'text-orange-400 animate-pulse'}>
                                            {jobStatus?.status || 'Queued'}
                                        </span>
                                    </div>
                                    <div className="h-1.5 w-full bg-slate-900 rounded-full overflow-hidden">
                                        <motion.div 
                                            initial={{ width: 0 }}
                                            animate={{ width: jobStatus?.status === 'completed' ? '100%' : '60%' }}
                                            className="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"
                                        />
                                    </div>
                                </div>

                                {jobStatus?.result_url && (
                                    <motion.a
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        href={jobStatus.result_url}
                                        target="_blank"
                                        className="w-full flex items-center justify-center gap-3 py-4 rounded-2xl bg-emerald-500 text-white font-black text-[10px] uppercase tracking-widest hover:bg-emerald-400 transition-all shadow-xl shadow-emerald-500/10"
                                    >
                                        <Zap size={14} /> Download Final Asset
                                    </motion.a>
                                )}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </motion.div>
    );
}
