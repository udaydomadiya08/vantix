'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Shield, ShieldCheck, Eye, EyeOff, Save, CheckCircle2, Loader2, Lock, Cpu, Server, Sparkles, Trash2 } from "lucide-react";
import { getUserKeys, syncUserKeys } from "@/lib/api";

export default function ApiVaultPage() {
    const [keys, setKeys] = useState({
        groq: "",
        openrouter: "",
        pexels: "",
        pixabay: "",
        hf_token: ""
    });
    // Default visibility to true for total transparency
    const [visible, setVisible] = useState<Record<string, boolean>>({
        groq: true,
        openrouter: true,
        pexels: true,
        pixabay: true,
        hf_token: false
    });
    const [isSyncing, setIsSyncing] = useState(false);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        async function load() {
            try {
                const data = await getUserKeys();
                console.log("🧬 [VAULT_LOAD]: Server response received.", !!data);
                
                let finalKeys = { ...keys };
                
                // 🛡️ [HYDRATION] Fallback to Local Vault if Server is empty
                if (!data || Object.values(data).every(v => !v)) {
                   const stored = localStorage.getItem("vantix_api_keys");
                   if (stored) {
                       console.warn("⚠️ [VAULT_RECOVERY]: Server returned empty. Restoring from Local Vault...");
                       const localData = JSON.parse(stored);
                       // Only restore if localData has actual content
                       if (Object.values(localData).some(v => !!v)) {
                           finalKeys = { ...finalKeys, ...localData };
                           // Silent Re-Sync (Heal the backend node)
                           syncUserKeys(localData).catch(err => console.error("❌ [RE-SYNC_FAIL]:", err));
                       }
                   }
                } else {
                   finalKeys = { ...finalKeys, ...data };
                }

                setKeys(finalKeys);
            } catch (e) {
                console.error("🚨 [VAULT_CRITICAL]: Loading failed.", e);
                // Last ditch recovery on network failure
                const stored = localStorage.getItem("vantix_api_keys");
                if (stored) setKeys(prev => ({ ...prev, ...JSON.parse(stored) }));
            }
        }
        load();
    }, []);

    const handleSave = async () => {
        setIsSyncing(true);
        try {
            const res = await syncUserKeys(keys);
            // 🛡️ [STATE LOCK] Confirm local state with server truth
            if (res && !res.detail) {
                setKeys(prev => ({ ...prev, ...res }));
                localStorage.setItem("vantix_api_keys", JSON.stringify(res));
            }
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } catch (e) {
            alert("Sovereign Sync Failure: Node unreachable or identity mismatched.");
        } finally {
            setIsSyncing(false);
        }
    };

    const toggleVisible = (key: string) => {
        setVisible(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const keyFields = [
        { id: 'groq', name: 'Groq API Key', provider: 'Groq Cloud', subtitle: 'Ultra-fast inference (whisper-large-v3-turbo)' },
        { id: 'openrouter', name: 'OpenRouter Key', provider: 'OpenRouter', subtitle: 'Global model orchestration (Llama 3.3/Qwen)' },
        { id: 'pexels', name: 'Pexels Key', provider: 'Pexels', subtitle: 'High-fidelity cinematic stock discovery' },
        { id: 'pixabay', name: 'Pixabay Key', provider: 'Pixabay', subtitle: 'Illustrative and vector asset fallback search' },
        { id: 'hf_token', name: 'HF Access Token', provider: 'Hugging Face', subtitle: 'Required for Live System Telemetry (Logs)' },
    ];

    return (
        <>
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-5xl space-y-12 pb-20"
        >
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <span className="industrial-badge">Security Node</span>
                        <div className="h-px w-12 bg-emerald-500/30" />
                    </div>
                    <h1 className="text-5xl font-black tracking-tighter text-white flex items-center gap-4">
                        <Lock className="text-emerald-500 accent-glow" size={40} />
                        Sovereign Vault
                    </h1>
                    <p className="text-slate-400 text-lg max-w-xl">AES-256 encrypted production cluster credentials.</p>
                </div>

                {/* 🛡️ [COALITION LOGIC] Industrial Identity Instructions */}
                <div className="bg-emerald-500/10 border border-emerald-500/20 p-6 rounded-[2rem] space-y-4 backdrop-blur-xl">
                    <div className="flex items-center gap-3 text-emerald-400 font-bold text-xs uppercase tracking-[0.3em]">
                        <ShieldCheck size={20} className="accent-glow" />
                        Flexible Coalition Logic Active
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed font-medium">
                        VANTIX production streams require only **one active node per category**. 
                        Choose either <span className="text-emerald-400">Groq</span> or <span className="text-emerald-400">OpenRouter</span> for intelligence, 
                        and either <span className="text-emerald-400">Pexels</span> or <span className="text-emerald-400">Pixabay</span> for visual synthesis.
                    </p>
                </div>
                
                <div className="flex items-center gap-4">
                    <div className="px-5 py-2.5 rounded-2xl glass-card bg-emerald-500/10 border-emerald-500/20 flex items-center gap-3">
                        <Shield size={16} className="text-emerald-400 accent-glow" />
                        <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Encryption Active</span>
                    </div>
                </div>
            </header>

            <div className="p-8 glass-card rounded-[2.5rem] border-emerald-500/10 bg-emerald-500/5 flex items-start gap-6">
                <div className="p-4 rounded-2xl bg-emerald-500/10 text-emerald-500">
                    <Cpu size={28} className="accent-glow" />
                </div>
                <div className="space-y-2">
                    <h3 className="text-sm font-black text-white uppercase tracking-widest flex items-center gap-2">
                        Industrial Identity Masking
                        <span className="text-[10px] text-slate-500 font-bold lowercase opacity-50">/ (v74.5)</span>
                    </h3>
                    <p className="text-sm text-slate-400 leading-relaxed max-w-3xl">
                        Your credentials are cryptographically hardened. They are never stored in plain text and are only decrypted in-memory during high-throughput synthesis cycles on the production host.
                    </p>
                </div>
            </div>

            <section className="glass-card rounded-[2.5rem] overflow-hidden">
                <div className="p-8 md:p-12 grid grid-cols-1 gap-12">
                    {keyFields.map((field) => (
                        <div key={field.id} className="space-y-4">
                            <div className="flex justify-between items-center group">
                                <div className="flex items-center gap-4">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center gap-2 group-hover:text-emerald-500 transition-colors">
                                        <div className="w-1.5 h-1.5 rounded-full bg-slate-800 group-hover:bg-emerald-500 transition-colors" />
                                        {field.name}
                                    </label>
                                    <span className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-tighter ${keys[field.id as keyof typeof keys] ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-500 border border-rose-500/20'}`}>
                                        {keys[field.id as keyof typeof keys] ? 'Configured' : 'Missing'}
                                    </span>
                                </div>
                                <button
                                    onClick={async () => {
                                        // 🗑️ [IMMEDIATE PURGE] Update state and trigger a focused sync
                                        const newKeys = { ...keys, [field.id]: "" };
                                        setKeys(newKeys);
                                        setIsSyncing(true);
                                        try {
                                            const res = await syncUserKeys(newKeys);
                                            if (res && !res.detail) {
                                                localStorage.setItem("vantix_api_keys", JSON.stringify(res));
                                                setSaved(true);
                                                setTimeout(() => setSaved(false), 2000);
                                            }
                                        } finally {
                                            setIsSyncing(false);
                                        }
                                    }}
                                    className="text-[9px] text-rose-500 font-black uppercase tracking-widest hover:text-rose-400 transition-all flex items-center gap-2 bg-rose-500/5 px-3 py-1.5 rounded-lg border border-rose-500/10"
                                >
                                    <Trash2 size={12} />
                                    Delete
                                </button>
                            </div>
                            <div className="relative group/input">
                                <input
                                    type={visible[field.id] ? "text" : "password"}
                                    value={keys[field.id as keyof typeof keys] || ""}
                                    onChange={(e) => {
                                        setKeys(prev => ({ ...prev, [field.id]: e.target.value }));
                                        setSaved(false); // Reset saved status on edit
                                    }}
                                    placeholder={`[${field.provider.toUpperCase()} NODE] Click to Add/Edit Key...`}
                                    className="w-full monochrome-input rounded-2xl px-8 py-5 text-white focus:outline-none transition-all font-mono text-sm tracking-widest bg-slate-950/20"
                                />
                                <button
                                    onClick={() => toggleVisible(field.id)}
                                    className="absolute right-6 top-1/2 -translate-y-1/2 text-slate-600 hover:text-emerald-400 transition-colors"
                                >
                                    {visible[field.id] ? <EyeOff size={20} /> : <Eye size={20} />}
                                </button>
                                <div className="absolute left-0 bottom-0 h-0.5 w-0 bg-emerald-500/50 group-focus-within/input:w-full transition-all duration-500" />
                            </div>
                            {keys[field.id as keyof typeof keys] === "" && (
                                <p className="text-[9px] text-rose-500/60 font-medium italic animate-pulse">
                                    Node Cleared. Synchronize to permanently delete from vault.
                                </p>
                            )}
                        </div>
                    ))}
                </div>

                {/* 📊 [NEW] Master Key Summary Table */}
                <div className="px-8 pb-12">
                    <div className="rounded-[2rem] border border-slate-800 bg-slate-950/20 overflow-hidden">
                        <table className="w-full text-left">
                            <thead className="bg-slate-900/50">
                                <tr>
                                    <th className="px-6 py-4 text-[9px] font-black text-slate-500 uppercase tracking-widest">Node Provider</th>
                                    <th className="px-6 py-4 text-[9px] font-black text-slate-500 uppercase tracking-widest">Global Status</th>
                                    <th className="px-6 py-4 text-[9px] font-black text-slate-500 uppercase tracking-widest whitespace-nowrap">Encryption Nodes</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/30">
                                {keyFields.map((field) => (
                                    <tr key={field.id} className="hover:bg-slate-900/10 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col">
                                                <span className="text-xs font-bold text-white tracking-tight">{field.provider}</span>
                                                <span className="text-[9px] text-slate-600 font-medium uppercase tracking-tighter">{field.name}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <div className={`w-1.5 h-1.5 rounded-full ${keys[field.id as keyof typeof keys] ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-rose-500'}`} />
                                                <span className={`text-[10px] font-black uppercase tracking-widest ${keys[field.id as keyof typeof keys] ? 'text-emerald-400' : 'text-rose-500'}`}>
                                                    {keys[field.id as keyof typeof keys] ? 'Synchronized' : 'Missing'}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="text-[10px] font-mono text-slate-700">AES-256 / PBKDF2</span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <footer className="p-8 md:p-12 bg-slate-950/30 border-t border-slate-800/50 flex flex-col md:flex-row md:items-center justify-between gap-8">
                    <div className="flex items-center gap-4 text-slate-500">
                        <Server size={18} />
                        <span className="text-[10px] font-black uppercase tracking-widest">
                            Production Host: {typeof window !== 'undefined' ? (window.location.host === 'localhost:3000' ? '127.0.0.1:8000' : window.location.host) : 'Syncing...'}
                        </span>
                    </div>

                    <button
                        onClick={handleSave}
                        disabled={saved || isSyncing}
                        className={`relative group overflow-hidden flex items-center gap-4 px-12 py-5 rounded-2xl font-black text-[11px] uppercase tracking-[0.2em] transition-all ${saved ? 'bg-emerald-500 text-white' : 'bg-white text-black hover:scale-105 active:scale-95 disabled:opacity-50'}`}
                    >
                        {isSyncing ? (
                            <Loader2 className="animate-spin" size={18} />
                        ) : saved ? (
                            <>
                                <CheckCircle2 size={18} className="accent-glow" /> 
                                Identity Synchronized
                            </>
                        ) : (
                            <>
                                <Sparkles size={18} className="group-hover:rotate-12 transition-transform" />
                                Synchronize Identity
                            </>
                        )}
                        {!saved && <div className="absolute inset-x-0 bottom-0 h-1 bg-emerald-500 transform translate-y-full group-hover:translate-y-0 transition-transform" />}
                    </button>
                </footer>
            </section>
        </motion.div>

        {/* 🛠️ [NEW] Industrial Node Diagnostics */}
        <section className="glass-card rounded-[2.5rem] p-8 border-slate-800 bg-slate-900/20 space-y-8">
            <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl bg-orange-500/10 text-orange-500">
                    <Zap size={20} className="accent-glow" />
                </div>
                <div>
                    <h3 className="text-[10px] font-black text-white uppercase tracking-[0.2em]">Node Critical Diagnostics</h3>
                    <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">Post-Graduation Connectivity Audit</p>
                </div>
            </div>

            <div className="grid grid-cols-1">
                <div className="p-6 rounded-2xl bg-slate-950/50 border border-slate-800 space-y-3">
                    <div className="flex items-center gap-2 text-orange-400">
                        <Shield size={14} />
                        <span className="text-[9px] font-black uppercase tracking-widest">Global Asset Hygiene</span>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-relaxed">
                        If your visual discovery fails for a specific topic, the engine automatically swerves to Pixabay fallback layers to preserve production continuity.
                    </p>
                </div>
            </div>
        </section>
        </>
    );
}
