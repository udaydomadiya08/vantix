'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Book, Video, GraduationCap, Image as ImageIcon, Search, Filter, Download, ExternalLink, Clock, Server, CheckCircle2, History, Trash2, Zap, AlertCircle, ShieldAlert } from "lucide-react";
import { getHistory } from "@/lib/api";

export default function LibraryPage() {
    const [history, setHistory] = useState<any[]>([]);
    const [filter, setFilter] = useState<string>("all");
    const [search, setSearch] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const data = await getHistory();
                // 🛡️ [DEFENSIVE] Only accept arrays — auth errors return objects
                if (Array.isArray(data)) {
                    setHistory(data);
                } else {
                    console.warn("[Library] History returned non-array — likely an auth error:", data);
                    setHistory([]);
                }
            } catch (e) {
                console.error("Ledger retrieval failed");
                setHistory([]);
            } finally {
                setIsLoading(false);
            }
        }
        load();
    }, []);

    const filteredHistory = history.filter(job => {
        const matchesFilter = filter === "all" || job.stream === filter;
        const matchesSearch = !search || (job.topic ?? "").toLowerCase().includes(search.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    const categories = [
        { id: 'all', label: 'All Assets', icon: History },
        { id: 'video', label: 'Videos', icon: Video },
        { id: 'ebook', label: 'Ebooks', icon: Book },
        { id: 'course', label: 'Courses', icon: GraduationCap },
        { id: 'thumbnail', label: 'Thumbnails', icon: ImageIcon },
    ];

    return (
        <motion.div 
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="max-w-7xl space-y-12 pb-20"
        >
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-8 py-4">
                <div className="space-y-3">
                    <div className="flex items-center gap-2">
                        <span className="industrial-badge text-emerald-500 bg-emerald-500/10 border-emerald-500/20">Identity: {localStorage.getItem('sovereign_username') || 'Anonymous'}</span>
                        <div className="h-px w-12 bg-emerald-500/20" />
                    </div>
                    <h1 className="text-5xl font-black tracking-tighter text-white flex items-center gap-4">
                        <History className="text-emerald-500 accent-glow" size={44} />
                        Vantix Ledger
                    </h1>
                    <div className="flex items-center gap-3">
                        <p className="text-slate-400 text-lg">Historical record of all factory nodes.</p>
                        <div className="w-1.5 h-1.5 rounded-full bg-slate-800" />
                        <span className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Vault Status: {localStorage.getItem('sovereign_api_keys') ? 'Synchronized' : 'Offline'}</span>
                    </div>
                </div>

                <div className="flex flex-col md:flex-row gap-4">
                    <div className="relative group">
                        <Search size={18} className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-emerald-500 transition-colors" />
                        <input 
                            type="text"
                            placeholder="Filter by topic..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="bg-slate-950/50 border border-slate-800 rounded-2xl pl-14 pr-6 py-4 text-sm text-white focus:outline-none focus:border-emerald-500/50 w-full md:w-64 transition-all"
                        />
            </div>
        </div>
    </header>

    {/* ⚠️ EPHEMERAL SHIELD WARNING */}
    <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card border-rose-500/20 bg-rose-500/5 p-8 rounded-[2.5rem] flex flex-col md:flex-row items-center gap-8 relative overflow-hidden"
    >
        <div className="p-5 rounded-3xl bg-rose-500/10 text-rose-500 shadow-inner">
            <ShieldAlert size={32} />
        </div>
        <div className="space-y-2 text-center md:text-left relative z-10">
            <h3 className="text-rose-500 font-black text-lg uppercase tracking-tighter italic">Data Volatility Warning</h3>
            <p className="text-slate-400 text-sm font-medium max-w-4xl leading-relaxed">
                The Ledger tracks all production nodes, but physical assets are **PURGED** every 24 hours. 
                Completion items older than one day will remain in history for tracking but their download links will return <span className="text-rose-500 font-bold">404: Destroyed</span>.
                The Sovereignty of your data depends on your immediate local download.
            </p>
        </div>
        <div className="absolute -right-4 -bottom-4 opacity-5 pointer-events-none">
            <Trash2 size={160} />
        </div>
    </motion.div>

            {/* Filter Tabs */}
            <div className="flex flex-wrap gap-3">
                {categories.map((cat) => (
                    <button
                        key={cat.id}
                        onClick={() => setFilter(cat.id)}
                        className={`px-6 py-3 rounded-xl border flex items-center gap-3 text-[10px] font-black uppercase tracking-widest transition-all ${filter === cat.id ? 'bg-emerald-500 text-white border-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.3)]' : 'bg-slate-900 border-slate-800 text-slate-500 hover:border-slate-700'}`}
                    >
                        <cat.icon size={14} />
                        {cat.label}
                    </button>
                ))}
            </div>

            {/* Main Ledger Grid */}
            {isLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {[1, 2, 3, 4, 5, 6].map(i => (
                        <div key={i} className="glass-card h-64 rounded-[2rem] animate-pulse bg-emerald-500/5" />
                    ))}
                </div>
            ) : filteredHistory.length === 0 ? (
                <div className="glass-card p-24 md:p-32 rounded-[3rem] border-dashed border-slate-800 flex flex-col items-center justify-center text-center space-y-6">
                    <div className="p-8 rounded-full bg-slate-900 text-slate-700 border border-slate-800">
                        <History size={48} />
                    </div>
                    <div className="space-y-3">
                        <h3 className="text-xl font-bold text-slate-500 uppercase tracking-widest">Archive Empty</h3>
                        <p className="text-sm text-slate-600 max-w-sm">No historical nodes match your current account (**{localStorage.getItem('sovereign_username') || 'Anonymous'}**).</p>
                        <div className="pt-4 flex flex-col items-center gap-2">
                            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-black">Troubleshooting</p>
                            <p className="text-[10px] text-slate-700 max-w-xs leading-relaxed">Each factory node maintains its own ledger. Ensure you are logged into the same account used during synthesis.</p>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <AnimatePresence mode="popLayout">
                        {filteredHistory.map((job) => (
                            <motion.div
                                key={job.id}
                                layout
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="glass-card rounded-[2.5rem] p-8 flex flex-col justify-between hover:border-emerald-500/30 transition-all group overflow-hidden relative"
                            >
                                <div className="space-y-6 relative z-10">
                                    <div className="flex items-center justify-between">
                                        <div className={`p-4 rounded-2xl bg-slate-900 text-slate-500 group-hover:bg-emerald-500/10 group-hover:text-emerald-500 transition-all`}>
                                            {job.stream === 'video' ? <Video size={24} /> : job.stream === 'ebook' ? <Book size={24} /> : job.stream === 'thumbnail' ? <ImageIcon size={24} /> : <GraduationCap size={24} />}
                                        </div>
                                        <div className="flex flex-col items-end">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-[8px] font-black text-amber-500/60 uppercase tracking-widest border border-amber-500/20 px-2 py-0.5 rounded-full bg-amber-500/5">Vantix Ephemeral Node</span>
                                                <span className="text-[9px] font-black text-slate-600 uppercase tracking-tighter">Status</span>
                                            </div>
                                            <div className="flex items-center gap-1.5">
                                                <div className={`w-1.5 h-1.5 rounded-full ${job.status === 'completed' ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : job.status === 'cancelled' ? 'bg-rose-500' : 'bg-orange-500'}`} />
                                                <span className={`text-[10px] font-black uppercase tracking-widest ${job.status === 'completed' ? 'text-emerald-400' : 'text-slate-500'}`}>{job.status}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-2">
                                        <h3 className="text-white font-black text-xl leading-tight line-clamp-2 min-h-[3.5rem] tracking-tight">{job.topic || job.stream?.toUpperCase() || 'Asset'}</h3>
                                        <div className="flex items-center gap-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                                            <div className="flex items-center gap-1.5">
                                                <Clock size={12} />
                                                {new Date(job.submitted).toLocaleDateString()}
                                            </div>
                                            <div className="flex items-center gap-1.5">
                                                <Server size={12} />
                                                {job.id.slice(0, 8)}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-8 pt-6 border-t border-slate-800/50 flex items-center justify-between relative z-10">
                                    {job.result_url ? (
                                        <a 
                                            href={job.result_url} 
                                            download
                                            className="flex-1 mr-4 bg-emerald-500 text-white rounded-2xl py-4 flex items-center justify-center gap-3 text-[11px] font-black uppercase tracking-[0.2em] shadow-xl shadow-emerald-500/10 hover:bg-emerald-400 transition-all"
                                        >
                                            <Download size={16} /> Get Asset
                                        </a>
                                    ) : (
                                        <div className="flex-1 mr-4 bg-slate-900 border border-slate-800 text-slate-700 rounded-2xl py-4 flex items-center justify-center gap-3 text-[11px] font-black uppercase tracking-[0.2em]">
                                            {job.status === 'cancelled' ? <Zap size={16} /> : <AlertCircle size={16} />}
                                            {job.status === 'cancelled' ? 'Killed' : 'No Asset'}
                                        </div>
                                    )}
                                    <button className="p-4 rounded-2xl bg-slate-900 text-slate-500 hover:text-white hover:bg-slate-800 transition-all">
                                        <ExternalLink size={18} />
                                    </button>
                                </div>

                                {/* Industrial Background Glow */}
                                <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 blur-[80px] -mr-16 -mt-16 group-hover:bg-emerald-500/10 transition-all" />
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>
            )}
        </motion.div>
    );
}
