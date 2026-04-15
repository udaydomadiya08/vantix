'use client';

import { useState } from "react";
import { GraduationCap, BookOpen, Layers, Zap, Wand2, Loader2, Sparkles, Smartphone, Monitor, User, Info } from "lucide-react";
import { generateCourse } from "@/lib/api";

export default function CoursesPage() {
    const [topic, setTopic] = useState("");
    const [horizontal, setHorizontal] = useState(false);
    const [includeAvatar, setIncludeAvatar] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);

    const handleLaunch = async () => {
        if (!topic) return alert("Vantix Input Error: Course subject required.");
        setIsProcessing(true);
        try {
            console.log("🚀 [FACTORY]: Initiating Autonomous Curriculum Foundry...", topic);
            const config = {
                horizontal,
                include_avatar: includeAvatar
            };
            const res = await generateCourse(topic, config);
            if (res && res.job_id) {
                console.log("✅ [FACTORY]: Course Orchestra Stream Active. Job ID:", res.job_id);
                // 🛰️ [SYNC] Hydrate Global Dashboard Ledger
                const saved = localStorage.getItem('vantix_queue');
                const jobs = saved ? JSON.parse(saved) : [];
                localStorage.setItem('vantix_queue', JSON.stringify([{ 
                    id: res.job_id, 
                    status: 'queued', 
                    type: 'course', 
                    topic: topic, 
                    timestamp: new Date() 
                }, ...jobs]));
                alert("INDUSTRIAL SUCCESS: Course series enqueued. Return to Dashboard to track progress.");
            }
        } catch (error: any) {
            const status = error.status || (error instanceof Response ? error.status : (error.response?.status || 0));
            if (status === 402) {
                alert("INSUFFICIENT POWER: Node balance depleted. Recharge your industrial balance to continue.");
            } else if (status === 428) {
                // 🛰️ [HEAL] Industrial Identity Synchronization
                const stored = localStorage.getItem("vantix_api_keys");
                if (stored) {
                    try {
                        const keys = JSON.parse(stored);
                        const { syncUserKeys } = await import("@/lib/api");
                        await syncUserKeys(keys);
                        console.log("🛠️ [HEAL]: Identity Synced. Retrying curriculum stream...");
                        return handleLaunch(); // Recursive Auto-Retry (Silent)
                    } catch (e) {
                        console.error("Vault Heal Failed:", e);
                    }
                }
                alert("VAULT LOCKED: Core AI keys missing. Please synchronize manually in the Sovereign Vault.");
            } else if (status === 422) {
                const detail = JSON.stringify(error.detail);
                alert(`UNPROCESSABLE IDENTITY: The server rejected this curriculum cluster. DETAIL: ${detail}`);
            } else {
                alert("INDUSTRIAL INTERRUPTION: Infrastructure node unreachable. Check backend status.");
            }
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="max-w-4xl space-y-12 pb-20">
            <header className="space-y-2">
                <h1 className="text-4xl font-bold tracking-tight text-white flex items-center gap-4">
                    <GraduationCap className="text-violet-500" size={32} />
                    Course Factory
                </h1>
                <p className="text-slate-400 text-lg">Industrial-grade parallel educational synthesis with autonomous module orchestration.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-8">
                    <div className="space-y-4">
                        <label className="text-sm font-bold text-slate-400 uppercase tracking-widest">Course Subject / Goal</label>
                        <textarea
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder="E.g. Advanced deep learning with PyTorch for senior architects..."
                            className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-6 text-white min-h-[150px] focus:outline-none focus:border-violet-500/50 transition-all text-lg leading-relaxed"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <button
                            onClick={() => setHorizontal(false)}
                            className={`flex flex-col items-center gap-4 p-6 rounded-2xl border transition-all ${!horizontal ? 'bg-violet-500/10 border-violet-500 text-white shadow-[0_0_20px_rgba(139,92,246,0.2)]' : 'bg-slate-900 border-slate-800 text-slate-500'}`}
                        >
                            <Smartphone size={32} />
                            <div className="text-[10px] font-bold uppercase tracking-widest">Mobile Video</div>
                        </button>
                        <button
                            onClick={() => setHorizontal(true)}
                            className={`flex flex-col items-center gap-4 p-6 rounded-2xl border transition-all ${horizontal ? 'bg-violet-500/10 border-violet-500 text-white shadow-[0_0_20px_rgba(139,92,246,0.2)]' : 'bg-slate-900 border-slate-800 text-slate-500'}`}
                        >
                            <Monitor size={32} />
                            <div className="text-[10px] font-bold uppercase tracking-widest">Widescreen</div>
                        </button>
                    </div>
                </div>

                <div className="space-y-8">
                    <div className="rounded-3xl bg-slate-900/50 border border-slate-800 p-8 space-y-8">
                        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                            <Sparkles className="text-violet-500" size={14} /> Educational DNA
                        </h3>

                        <div className="space-y-4">
                            <div
                                onClick={() => setIncludeAvatar(!includeAvatar)}
                                className={`flex items-center justify-between p-5 rounded-2xl border cursor-pointer transition-all ${includeAvatar ? 'bg-violet-500 text-white border-violet-400 shadow-[0_0_20px_rgba(139,92,246,0.3)]' : 'bg-slate-800/50 border-slate-700 text-slate-400'}`}
                            >
                                <div className="flex items-center gap-3">
                                    <User size={20} />
                                    <span className="font-bold text-sm uppercase tracking-widest">Tutor Avatar</span>
                                </div>
                                <div className={`h-4 w-4 rounded-full border-2 ${includeAvatar ? 'bg-white border-white' : 'border-slate-600'}`} />
                            </div>

                            <div className="p-5 bg-violet-500/5 border border-violet-500/20 rounded-2xl space-y-3">
                                <div className="flex items-center gap-2 text-[10px] font-bold text-violet-400 uppercase tracking-widest">
                                    <Layers size={14} /> Hierarchy logic
                                </div>
                                <p className="text-xs text-slate-500 leading-relaxed italic">
                                    The factory will recursively synthesize modules and produce individual lessons in high-performance parallel streams.
                                </p>
                            </div>
                        </div>

                        <button
                            onClick={handleLaunch}
                            disabled={isProcessing}
                            className="w-full bg-white text-black hover:bg-violet-500 hover:text-white py-6 rounded-2xl font-black text-xl uppercase tracking-widest shadow-xl flex items-center justify-center gap-4 transition-all group"
                        >
                            {isProcessing ? <Loader2 className="animate-spin" /> : <Wand2 className="group-hover:translate-y-[-2px] transition-transform" />}
                            {isProcessing ? 'Synthesizing...' : 'Orchestrate Series'}
                        </button>

                        <div className="flex items-center gap-2 text-[10px] text-slate-500 font-medium">
                            <Info size={12} /> Sequential stream queuing enabled.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
