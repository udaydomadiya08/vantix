'use client';

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Zap, Shield, CreditCard, Rocket, Flame, 
  CheckCircle2, Loader2, Sparkles, Coins,
  Plus, ArrowRight
} from "lucide-react";
import { createCheckoutSession } from "@/lib/api";

const PLANS = [
  {
    id: "starter",
    name: "Starter Cell",
    price: "$10",
    credits: "100 Credits",
    featured: false,
    color: "cyan",
    perks: [
      "20 High-Retention Shorts",
      "5 Industrial E-Books",
      "Standard Synthesis Speed",
      "24h Asset Persistence"
    ]
  },
  {
    id: "core",
    name: "Engine Core",
    price: "$45",
    credits: "500 Credits",
    featured: true,
    color: "emerald",
    perks: [
      "100 High-Retention Shorts",
      "25 Industrial E-Books",
      "Priority Queue Access",
      "Global Topic Enrichment",
      "Extended Research Mode"
    ]
  },
  {
    id: "grid",
    name: "Industrial Grid",
    price: "$150",
    credits: "2000 Credits",
    featured: false,
    color: "indigo",
    perks: [
      "400 High-Retention Shorts",
      "100 Industrial E-Books",
      "Ultra-Low Latency Hub",
      "Infinite Synthesis Scale",
      "Full API Cluster Access"
    ]
  }
];

export default function RechargePage() {
    const [loadingPlan, setLoadingPlan] = useState<string | null>(null);

    const handlePurchase = async (planId: string) => {
        setLoadingPlan(planId);
        try {
            console.log(`💳 [BILLING]: Initiating Stripe Session for: ${planId}`);
            const res = await createCheckoutSession(planId);
            if (res && res.url) {
                window.location.href = res.url;
            } else {
                alert("Billing Error: Industrial node failed to generate checkout URL.");
            }
        } catch (e) {
            console.error("Payment synthesis failure:", e);
            alert("Payment Interruption: Node unreachable or Stripe handshake failed.");
        } finally {
            setLoadingPlan(null);
        }
    };

    return (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-7xl mx-auto space-y-12 pb-20 font-sans">
            <header className="space-y-4">
                <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black text-emerald-500 uppercase tracking-widest px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">Industrial Billing Hub</span>
                </div>
                <h1 className="text-6xl font-black tracking-tight text-white italic">RECHARGE POWER</h1>
                <p className="text-slate-400 text-xl max-w-2xl font-medium">Inject credits into your Vantix node to fuel autonomous media synthesis.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {PLANS.map((plan) => (
                    <motion.div
                        key={plan.id}
                        whileHover={{ y: -5 }}
                        className={`glass-card p-10 rounded-[3rem] flex flex-col space-y-8 relative overflow-hidden group transition-all ${plan.featured ? 'border-emerald-500/50 bg-emerald-500/[0.03]' : 'border-slate-800'}`}
                    >
                        {plan.featured && (
                            <div className="absolute top-0 right-0 px-6 py-2 bg-emerald-500 text-white text-[10px] font-black uppercase tracking-widest rounded-bl-2xl">
                                Popular Node
                            </div>
                        )}

                        <div className="space-y-4 text-center">
                            <div className={`p-5 rounded-2xl bg-${plan.color}-500/10 text-${plan.color}-400 w-fit mx-auto`}>
                                {plan.id === 'starter' ? <Zap size={32} /> : plan.id === 'core' ? <Rocket size={32} /> : <Flame size={32} />}
                            </div>
                            <div>
                                <h3 className="text-2xl font-black italic tracking-tight">{plan.name}</h3>
                                <p className={`text-[10px] font-black text-${plan.color}-500 uppercase tracking-widest mt-1`}>{plan.credits}</p>
                            </div>
                        </div>

                        <div className="text-center">
                            <span className="text-5xl font-black text-white">{plan.price}</span>
                            <span className="text-slate-500 text-xs font-bold uppercase ml-2 tracking-widest">/ Node</span>
                        </div>

                        <ul className="space-y-4 flex-1">
                            {plan.perks.map((perk, i) => (
                                <li key={i} className="flex items-start gap-3 text-xs font-medium text-slate-400">
                                    <CheckCircle2 size={14} className={`text-${plan.color}-500 mt-0.5`} />
                                    {perk}
                                </li>
                            ))}
                        </ul>

                        <button
                            onClick={() => handlePurchase(plan.id)}
                            disabled={loadingPlan !== null}
                            className={`w-full py-5 rounded-[2rem] font-black uppercase tracking-widest transition-all flex items-center justify-center gap-3 group/btn ${
                                plan.featured 
                                ? 'bg-emerald-500 text-white shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:scale-105' 
                                : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
                            }`}
                        >
                            {loadingPlan === plan.id ? (
                                <Loader2 size={18} className="animate-spin" />
                            ) : (
                                <>
                                    Link Industrial Stripe
                                    <ArrowRight size={18} className="group-hover/btn:translate-x-1 transition-transform" />
                                </>
                            )}
                        </button>
                    </motion.div>
                ))}
            </div>

            <footer className="glass-card p-10 rounded-[3rem] border-slate-800/50 bg-slate-900/40 text-center space-y-6">
                <div className="flex items-center justify-center gap-4 text-slate-500 uppercase tracking-[0.3em] font-black text-[10px]">
                    <Shield size={16} />
                    Secured by Vantix Stripe Protocol
                </div>
                <p className="text-slate-500 text-xs font-medium max-w-2xl mx-auto italic">
                    All transactions are recorded in the Industrial Ledger. Credits are non-transferable and are consumed upon successful synthesis initiation.
                </p>
            </footer>
        </motion.div>
    );
}
