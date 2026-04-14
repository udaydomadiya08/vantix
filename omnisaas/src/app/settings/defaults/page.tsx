'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Settings, Save, Video, Book, GraduationCap, CheckCircle2, Loader2, Monitor, Info, Sparkles, ChevronRight } from "lucide-react";
import { getUserDefaults, updateUserDefaults } from "@/lib/api";

export default function SettingsDefaultsPage() {
    const [defaults, setDefaults] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");

    useEffect(() => {
        let isMounted = true;
        getUserDefaults().then(data => {
            if (isMounted) {
                setDefaults(data);
                setLoading(false);
            }
        }).catch(() => {
            if (isMounted) setLoading(false);
        });
        return () => { isMounted = false; };
    }, []);

    const handleSave = async (factory: string) => {
        if (!defaults || !defaults[factory]) return;
        setSaving(true);
        try {
            await updateUserDefaults(factory, defaults[factory]);
            setSuccessMessage(`${factory.toUpperCase()} parameters synchronized.`);
            setTimeout(() => setSuccessMessage(""), 3000);
        } catch (e) {
            alert("Sovereign Sync Failure: Check backend connection.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6">
            <div className="relative">
                <Loader2 className="animate-spin text-emerald-500" size={48} />
                <div className="absolute inset-0 blur-xl bg-emerald-500/20 animate-pulse" />
            </div>
            <p className="text-emerald-500/50 font-black uppercase tracking-[0.2em] text-[10px]">Accessing Production DNA...</p>
        </div>
    );

    if (!defaults || !defaults.video || !defaults.ebook) return (
        <div className="glass-card p-12 text-center space-y-4 max-w-2xl mx-auto rounded-3xl border-rose-500/20">
            <div className="mx-auto w-16 h-16 rounded-full bg-rose-500/10 flex items-center justify-center text-rose-500">
                <Info size={32} />
            </div>
            <h2 className="text-xl font-bold text-white">Sovereign Vault Offline</h2>
            <p className="text-slate-400">Could not synchronize with the industrial production cluster. Please verify backend status.</p>
        </div>
    );

    return (
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-5xl space-y-12 pb-20"
        >
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-2">
                    <div className="flex items-center gap-2 mb-2">
                        <span className="industrial-badge">Configuration Node</span>
                        <div className="h-px w-12 bg-emerald-500/30" />
                    </div>
                    <h1 className="text-5xl font-black tracking-tighter text-white">Production DNA</h1>
                    <p className="text-slate-400 text-lg max-w-xl">Fine-tune the global orchestration parameters for your industrial synthesis factories.</p>
                </div>
                
                <AnimatePresence>
                    {successMessage && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, x: 20 }}
                            animate={{ opacity: 1, scale: 1, x: 0 }}
                            exit={{ opacity: 0, scale: 0.9, x: 20 }}
                            className="flex items-center gap-3 text-emerald-400 text-xs font-black uppercase tracking-widest bg-emerald-500/10 px-6 py-3 rounded-2xl border border-emerald-500/30 glass-card"
                        >
                            <Sparkles size={16} className="text-emerald-400 accent-glow" /> 
                            {successMessage}
                        </motion.div>
                    )}
                </AnimatePresence>
            </header>

            <div className="grid grid-cols-1 gap-12">
                {/* Video Factory Card */}
                <section className="glass-card rounded-[2.5rem] overflow-hidden group">
                    <div className="p-8 md:p-10 border-b border-slate-800/50 flex flex-col md:flex-row md:items-center justify-between gap-6 bg-gradient-to-r from-emerald-500/5 to-transparent">
                        <div className="flex items-center gap-6">
                            <div className="p-4 rounded-3xl bg-emerald-500/10 text-emerald-500 shadow-inner">
                                <Video size={32} className="accent-glow" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">Video Factory</h2>
                                <p className="text-slate-500 text-sm font-bold">Cinematic Shorts & Viral Synthesis</p>
                            </div>
                        </div>
                        <button
                            onClick={() => handleSave('video')}
                            disabled={saving}
                            className="relative group/btn overflow-hidden flex items-center gap-3 bg-white text-black px-8 py-4 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] hover:scale-105 active:scale-95 transition-all shadow-xl"
                        >
                            {saving ? <Loader2 className="animate-spin" size={16} /> : <Save size={16} />}
                            Synchronize Factory
                            <div className="absolute inset-x-0 bottom-0 h-1 bg-emerald-500 transform translate-y-full group-hover/btn:translate-y-0 transition-transform" />
                        </button>
                    </div>

                    <div className="p-8 md:p-10 grid grid-cols-1 gap-12">
                        <div className="space-y-8">
                            <div className="space-y-4">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center gap-2">
                                    <Monitor size={12} className="text-emerald-500" /> Resolution Aspect
                                </label>
                                <div className="grid grid-cols-2 gap-3 p-1.5 bg-slate-950/50 rounded-2xl border border-slate-800/50">
                                    <button
                                        onClick={() => setDefaults({...defaults, video: {...defaults.video, horizontal: true}})}
                                        className={`flex items-center justify-center gap-3 py-4 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${defaults.video.horizontal ? 'bg-emerald-500 text-white shadow-lg accent-glow' : 'text-slate-500 hover:text-white hover:bg-slate-800'}`}
                                    >
                                        Landscape (16:9)
                                    </button>
                                    <button
                                        onClick={() => setDefaults({...defaults, video: {...defaults.video, horizontal: false}})}
                                        className={`flex items-center justify-center gap-3 py-4 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${!defaults.video.horizontal ? 'bg-emerald-500 text-white shadow-lg accent-glow' : 'text-slate-500 hover:text-white hover:bg-slate-800'}`}
                                    >
                                        Portrait (9:16)
                                    </button>
                                </div>
                                <p className="text-[11px] text-slate-500 font-medium px-2">Defines the industrial render dimensions for all content streams.</p>
                            </div>

                            <div className="space-y-4">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center gap-2">
                                    <Smartphone size={12} className="text-emerald-500" /> AI Avatar Synergy
                                </label>
                                <button
                                    onClick={() => setDefaults({...defaults, video: {...defaults.video, include_avatar: !defaults.video.include_avatar}})}
                                    className={`w-full flex items-center justify-between p-5 rounded-2xl border transition-all ${defaults.video.include_avatar ? 'bg-emerald-500/10 border-emerald-500/50 text-white' : 'bg-slate-950/30 border-slate-800/50 text-slate-400 hover:border-slate-700'}`}
                                >
                                    <span className="text-[11px] font-black uppercase tracking-widest">Enable Avatar Overlays</span>
                                    <div className={`w-12 h-6 rounded-full relative transition-all ${defaults.video.include_avatar ? 'bg-emerald-500' : 'bg-slate-800'}`}>
                                        <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-all ${defaults.video.include_avatar ? 'left-7' : 'left-1'}`} />
                                    </div>
                                </button>
                            </div>
                        </div>

                    </div>
                </section>

                {/* E-Book Factory Card */}
                <section className="glass-card rounded-[2.5rem] overflow-hidden group">
                    <div className="p-8 md:p-10 border-b border-slate-800/50 flex flex-col md:flex-row md:items-center justify-between gap-6 bg-gradient-to-r from-cyan-500/5 to-transparent">
                        <div className="flex items-center gap-6">
                            <div className="p-4 rounded-3xl bg-cyan-500/10 text-cyan-500">
                                <Book size={32} />
                            </div>
                            <div>
                                <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic">E-Book Factory</h2>
                                <p className="text-slate-500 text-sm font-bold">Deep Narrative & Layout Synthesis</p>
                            </div>
                        </div>
                        <button
                            onClick={() => handleSave('ebook')}
                            className="flex items-center gap-2 bg-slate-800 text-white px-8 py-4 rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] hover:bg-cyan-500 transition-all shadow-xl"
                        >
                            <Save size={16} /> Synchronize Factory
                        </button>
                    </div>

                    <div className="p-8 md:p-10 grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
                        <div className="p-6 rounded-3xl bg-slate-950/30 border border-slate-800/50">
                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest block mb-4">Chapter Depth</span>
                            <div className="flex items-center justify-center gap-4">
                                <button onClick={() => setDefaults({...defaults, ebook: {...defaults.ebook, num_chapters: Math.max(1, defaults.ebook.num_chapters - 1)}})} className="w-8 h-8 rounded-full bg-slate-800 hover:bg-cyan-500 text-white transition-all">-</button>
                                <span className="text-3xl font-black text-white">{defaults.ebook.num_chapters}</span>
                                <button onClick={() => setDefaults({...defaults, ebook: {...defaults.ebook, num_chapters: defaults.ebook.num_chapters + 1}})} className="w-8 h-8 rounded-full bg-slate-800 hover:bg-cyan-500 text-white transition-all">+</button>
                            </div>
                        </div>
                        
                        <div className="p-6 rounded-3xl bg-slate-950/30 border border-slate-800/50">
                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest block mb-4">Min. Word Count</span>
                            <div className="flex items-center justify-center gap-4">
                                <button onClick={() => setDefaults({...defaults, ebook: {...defaults.ebook, min_words: Math.max(50, defaults.ebook.min_words - 50)}})} className="w-8 h-8 rounded-full bg-slate-800 hover:bg-cyan-500 text-white transition-all">-</button>
                                <span className="text-3xl font-black text-white">{defaults.ebook.min_words}</span>
                                <button onClick={() => setDefaults({...defaults, ebook: {...defaults.ebook, min_words: defaults.ebook.min_words + 50}})} className="w-8 h-8 rounded-full bg-slate-800 hover:bg-cyan-500 text-white transition-all">+</button>
                            </div>
                        </div>

                        <div className="p-6 rounded-3xl bg-slate-950/30 border border-slate-800/50">
                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest block mb-4">Visual Art Synergy</span>
                            <button
                                onClick={() => setDefaults({...defaults, ebook: {...defaults.ebook, include_images: !defaults.ebook.include_images}})}
                                className={`px-6 py-3 rounded-full text-[10px] font-black uppercase tracking-widest transition-all ${defaults.ebook.include_images ? 'bg-cyan-500 text-white' : 'bg-slate-800 text-slate-400'}`}
                            >
                                {defaults.ebook.include_images ? 'Active' : 'Muted'}
                            </button>
                        </div>
                    </div>
                </section>
            </div>
            
            <footer className="p-12 glass-card rounded-[2.5rem] flex items-center gap-6 border-emerald-500/10 bg-emerald-500/5">
                <div className="p-5 rounded-3xl bg-emerald-500/20 text-emerald-400">
                    <GraduationCap size={40} />
                </div>
                <div className="space-y-1">
                    <h3 className="text-xl font-bold text-white">Industrial Graduation v99.1</h3>
                    <p className="text-slate-500 text-sm">Your production DNA is cryptographically persistent and synchronized across the entire Sovereign factory cluster.</p>
                </div>
            </footer>
        </motion.div>
    );
}

const Smartphone = (props: any) => (
    <svg {...props} width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-smartphone"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg>
);
