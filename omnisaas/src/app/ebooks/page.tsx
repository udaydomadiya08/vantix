'use client';

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Book, Feather, Palette, Sparkles, Wand2, Loader2, List, Type, Image as ImageIcon, Layout, Settings2 } from "lucide-react";
import { generateEbook } from "@/lib/api";

export default function EbooksPage() {
    const [topic, setTopic] = useState("");
    const [desc, setDesc] = useState("");
    const [chapters, setChapters] = useState(3);
    const [minWords, setMinWords] = useState(150);
    const [themeColor, setThemeColor] = useState("#1e293b");
    const [includeImages, setIncludeImages] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);
    const [showAdvanced, setShowAdvanced] = useState(false);

    const handleLaunch = async () => {
        if (!topic) return alert("Vantix Input Error: Topic node required.");
        setIsProcessing(true);
        try {
            console.log("🚀 [FACTORY]: Initiating E-Book Production Cluster...", topic);
            const res = await generateEbook(topic, {
                description: desc,
                chapters,
                min_words: minWords,
                theme_color: themeColor,
                images_toggle: includeImages
            });
            if (res && res.job_id) {
                console.log("✅ [FACTORY]: E-Book Narrative Stream Active. Job ID:", res.job_id);
                // 🛰️ [SYNC] Hydrate Global Dashboard Ledger
                const saved = localStorage.getItem('vantix_queue');
                const jobs = saved ? JSON.parse(saved) : [];
                localStorage.setItem('vantix_queue', JSON.stringify([{ 
                    id: res.job_id, 
                    status: 'queued', 
                    type: 'ebook', 
                    topic: topic, 
                    timestamp: new Date() 
                }, ...jobs]));
                alert("INDUSTRIAL SUCCESS: E-book synthesis enqueued. Return to Dashboard to track progress.");
            }
        } catch (error: any) {
            const status = error instanceof Response ? error.status : (error.response?.status || 0);
            if (status === 402) {
                alert("INSUFFICIENT POWER: Node balance depleted. Recharge your industrial balance to continue.");
            } else if (status === 428) {
                alert("VAULT LOCKED: Core AI keys missing. Please synchronize your Sovereign Vault.");
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
                    <Book className="text-blue-500" size={32} />
                    E-Book Factory
                </h1>
                <p className="text-slate-400 text-lg">High-throughput recursive research with multi-chapter sequential synthesis.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-8">
                    <div className="space-y-4">
                        <label className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                            <Type size={14} /> Main Topic
                        </label>
                        <input
                            type="text"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            placeholder="E.g. The Psychology of High-Performance Teams..."
                            className="w-full bg-slate-900 border border-slate-800 rounded-2xl px-6 py-4 text-white focus:outline-none focus:border-blue-500/50 transition-all text-lg"
                        />
                    </div>

                    <div className="space-y-4">
                        <label className="text-sm font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                            <ImageIcon size={14} /> Visual Aesthetic (Vision)
                        </label>
                        <textarea
                            value={desc}
                            onChange={(e) => setDesc(e.target.value)}
                            placeholder="Describe the desired aesthetic... (Cyber-noir, Minimalist, Royal)"
                            className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-6 text-white min-h-[120px] focus:outline-none focus:border-blue-500/50 transition-all font-serif"
                        />
                    </div>

                    <div className="space-y-4">
                        <button
                            onClick={() => setShowAdvanced(!showAdvanced)}
                            className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-widest hover:text-white transition-colors"
                        >
                            <Settings2 size={14} className={`transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
                            Advanced Parameters
                        </button>

                        {showAdvanced && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                className="space-y-6 pt-4 border-t border-slate-800 grid grid-cols-2 gap-4"
                            >
                                <div className="space-y-2">
                                    <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Chapters</label>
                                    <input
                                        type="number"
                                        value={chapters}
                                        onChange={(e) => setChapters(Number(e.target.value))}
                                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-white"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Min Words/Sec</label>
                                    <input
                                        type="number"
                                        value={minWords}
                                        onChange={(e) => setMinWords(Number(e.target.value))}
                                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-white"
                                    />
                                </div>
                            </motion.div>
                        )}
                    </div>
                </div>

                <div className="space-y-8">
                    <div className="rounded-3xl bg-slate-900/50 border border-slate-800 p-8 space-y-8">
                        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
                            <Layout size={14} /> Masterpiece Design
                        </h3>

                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-slate-300 font-medium">Primary Theme</span>
                                <input
                                    type="color"
                                    value={themeColor}
                                    onChange={(e) => setThemeColor(e.target.value)}
                                    className="h-8 w-8 rounded-lg bg-transparent cursor-pointer"
                                />
                            </div>

                            <div
                                onClick={() => setIncludeImages(!includeImages)}
                                className={`flex items-center justify-between p-5 rounded-2xl border cursor-pointer transition-all ${includeImages ? 'bg-blue-500 text-white border-blue-400 shadow-[0_0_20px_rgba(59,130,246,0.3)]' : 'bg-slate-800/50 border-slate-700 text-slate-400'}`}
                            >
                                <div className="flex items-center gap-3">
                                    <ImageIcon size={20} />
                                    <span className="font-bold text-sm uppercase tracking-widest">AI Illustrations</span>
                                </div>
                                <div className={`h-4 w-4 rounded-full border-2 ${includeImages ? 'bg-white border-white' : 'border-slate-600'}`} />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-800">
                            <div className="bg-slate-800/40 p-4 rounded-xl flex items-center gap-3">
                                <Feather className="text-blue-400" size={18} />
                                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-300">Literary</span>
                            </div>
                            <div className="bg-slate-800/40 p-4 rounded-xl flex items-center gap-3">
                                <Palette className="text-blue-400" size={18} />
                                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-300">Cinematic</span>
                            </div>
                        </div>

                        <p className="text-[10px] text-slate-500 leading-relaxed italic">
                            * The engine will synthesize a unique color palette and typography set based on your theme.
                        </p>
                    </div>

                    <button
                        onClick={handleLaunch}
                        disabled={isProcessing}
                        className="w-full bg-white text-black hover:bg-blue-500 hover:text-white py-6 rounded-2xl font-black text-xl uppercase tracking-widest shadow-xl flex items-center justify-center gap-4 transition-all group"
                    >
                        {isProcessing ? <Loader2 className="animate-spin" /> : <Wand2 className="group-hover:translate-x-1 transition-transform" />}
                        {isProcessing ? 'Synthesizing...' : 'Synthesize Book'}
                    </button>
                </div>
            </div>
        </div>
    );
}
