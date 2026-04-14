'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Coins, ChevronRight, ShieldCheck, Plus, ArrowRight, Loader2, Play, Book, GraduationCap, ArrowLeft } from "lucide-react";
import { getUserBalance, createCheckoutSession } from "@/lib/api";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function RechargeContent() {
  const [balance, setBalance] = useState<number | null>(null);
  const [isRecharging, setIsRecharging] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const searchParams = useSearchParams();

  useEffect(() => {
    getUserBalance().then(data => setBalance(data.balance)).catch(() => {});
    
    // 💡 [SENTINEL] Detect Stripe Feedback
    if (searchParams.get("success") === "true") {
      setSuccessMessage("Industrial Power Infusion Successful. Credits have been minted to your node.");
      setTimeout(() => setSuccessMessage(""), 10000);
    }
    if (searchParams.get("canceled") === "true") {
      setErrorMessage("Commercial Link Aborted. Payment was not processed.");
      setTimeout(() => setErrorMessage(""), 5000);
    }
  }, [searchParams]);

  const handleCheckout = async (planId: string) => {
    setIsRecharging(true);
    setErrorMessage("");
    try {
      const data = await createCheckoutSession(planId);
      if (data.url) {
        window.location.href = data.url; // 🛰️ REDIRECT TO STRIPE
      } else {
        throw new Error("No URL returned");
      }
    } catch (e) {
      setErrorMessage("Commercial Link Interrupted. Failed to initiate Stripe Session.");
    } finally {
      setIsRecharging(false);
    }
  };

  const plans = [
    { id: 'starter', amount: 100, price: '10', label: 'Starter Cell', bonus: 'Basic Power', icon: Zap, color: 'emerald' },
    { id: 'core', amount: 500, price: '45', label: 'Engine Core', bonus: '10% Extraction Bonus', icon: Coins, color: 'cyan' },
    { id: 'grid', amount: 2000, price: '150', label: 'Industrial Grid', bonus: '25% Optimization', icon: ShieldCheck, color: 'indigo' }
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-12 pb-20">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-8 py-6">
        <div className="space-y-4">
          <Link href="/" className="flex items-center gap-2 text-slate-500 hover:text-white transition-colors mb-4 group">
             <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
             <span className="text-[10px] font-black uppercase tracking-widest">Return to Dashboard</span>
          </Link>
          <div className="flex items-center gap-3">
             <div className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-400">
                <Coins size={32} />
             </div>
             <h1 className="text-5xl font-black italic tracking-tighter text-white underline decoration-emerald-500/30 decoration-8 underline-offset-8">RECHARGE NODE</h1>
          </div>
          <p className="text-slate-400 text-lg max-w-xl font-medium">Inject industrial power to restore synthesis capabilities and scale your media production.</p>
        </div>

        <div className="glass-card px-8 py-6 rounded-[2rem] bg-emerald-500/5 border-emerald-500/20 text-right">
           <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest block mb-1">Active Cluster Power</span>
           <div className="flex items-center justify-end gap-3">
              <span className="text-3xl font-black text-white tabular-nums">
                {balance !== null ? balance : <Loader2 size={24} className="animate-spin" />}
              </span>
              <span className="text-emerald-500 font-bold italic">Credits</span>
           </div>
        </div>
      </header>

      {/* Success Banner */}
      <AnimatePresence>
        {successMessage && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="p-6 rounded-3xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-black uppercase tracking-widest text-center"
          >
             {successMessage}
          </motion.div>
        )}
        {errorMessage && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="p-6 rounded-3xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-black uppercase tracking-widest text-center"
          >
             {errorMessage}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Pricing Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <motion.div
            key={plan.amount}
            whileHover={{ y: -10 }}
            className={`glass-card p-10 rounded-[3rem] border-slate-800 hover:border-${plan.color}-500/50 transition-all flex flex-col space-y-8 relative overflow-hidden group`}
          >
            <div className={`absolute top-0 right-0 w-32 h-32 bg-${plan.color}-500/5 blur-[80px] group-hover:bg-${plan.color}-500/10 transition-all`} />
            
            <div className="space-y-4 relative">
               <div className={`p-4 rounded-[1.5rem] w-fit bg-${plan.color}-500/10 text-${plan.color}-400`}>
                  <plan.icon size={28} />
               </div>
               <div>
                  <h3 className="text-white font-black text-xs uppercase tracking-widest">{plan.label}</h3>
                  <div className="flex items-baseline gap-1 mt-2">
                     <span className="text-4xl font-black text-white italic tracking-tighter">${plan.price}</span>
                     <span className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">/ Node</span>
                  </div>
               </div>
            </div>

            <div className="flex-1 space-y-4">
               <div className="flex items-center gap-3 text-slate-300">
                  <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]" />
                  <span className="text-xs font-bold">{plan.amount} Industrial Credits</span>
               </div>
               <div className="flex items-center gap-3 text-slate-300">
                  <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]" />
                  <span className="text-xs font-bold">{plan.bonus}</span>
               </div>
               <div className="flex items-center gap-3 text-slate-300">
                  <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]" />
                  <span className="text-xs font-bold">Standard Support</span>
               </div>
            </div>

            <button
              disabled={isRecharging}
              onClick={() => handleCheckout(plan.id)}
              className={`w-full py-5 rounded-[1.5rem] bg-${plan.color}-500 text-white text-xs font-black uppercase tracking-widest hover:brightness-110 active:scale-95 transition-all flex items-center justify-center gap-3 shadow-xl`}
            >
               {isRecharging ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
               Initiate Transfer
            </button>
          </motion.div>
        ))}
      </div>

      {/* Synthesis Costs / Legend */}
      <section className="glass-card p-12 rounded-[3.5rem] bg-slate-900/40 border-slate-800 space-y-10">
         <div className="flex flex-col items-center text-center space-y-2">
            <h2 className="text-xs font-black text-emerald-400 uppercase tracking-[0.3em]">Commercial Ledger</h2>
            <p className="text-2xl font-bold text-white italic">Synthesis Taxation Rates</p>
         </div>

         <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              { type: 'Short Video', cost: 5, icon: Play },
              { type: 'Narrative E-Book', cost: 10, icon: Book },
              { type: 'Industrial Course', cost: 25, icon: GraduationCap }
            ].map(item => (
              <div key={item.type} className="flex flex-col items-center space-y-4">
                 <div className="p-4 rounded-2xl bg-slate-800/50 text-slate-400">
                    <item.icon size={24} />
                 </div>
                 <div className="text-center">
                    <h4 className="text-xs font-black text-white uppercase tracking-widest mb-1">{item.type}</h4>
                    <p className="text-xl font-bold text-emerald-500 tabular-nums italic">-{item.cost} <span className="text-[10px] uppercase font-black text-slate-600">Credits</span></p>
                 </div>
              </div>
            ))}
         </div>

         <div className="pt-10 border-t border-slate-800 flex flex-col items-center gap-4 text-center">
            <div className="flex items-center gap-2 text-slate-500">
               <ShieldCheck size={16} />
               <span className="text-[10px] font-black uppercase tracking-widest">End-to-End Encryption Sequence</span>
            </div>
            <p className="text-[10px] text-slate-600 font-medium max-w-lg leading-relaxed uppercase tracking-widest">All industrial power transfers are permanently recorded on the Vantix Private Ledger. Once credits are injected into a node, they are non-refundable and dedicated to media synthesis.</p>
         </div>
      </section>
    </div>
  );
}

export default function RechargePage() {
  return (
    <Suspense fallback={
       <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
          <Loader2 size={32} className="text-emerald-500 animate-spin" />
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500 text-center">Calibrating Commercial Link...</p>
       </div>
    }>
       <RechargeContent />
    </Suspense>
  );
}
