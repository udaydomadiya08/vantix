'use client';

import { useState } from "react";
import { motion } from "framer-motion";
import { User, Lock, ArrowRight, ShieldCheck, Loader2 } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { loginUser } from "@/lib/api";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");
    const { login } = useAuth();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError("");

        try {
            const data = await loginUser({ username, password });
            if (data && data.token) {
                login(username, data.token);
            } else {
                // 🛡️ [STANDARD HANDSHAKE] Direct feedback loop
                const detail = data?.detail || "Invalid credentials.";
                setError(detail);
                
                // If user not found, gently suggest signup after a delay or secondary link
                if (detail.includes("node not found")) {
                    console.warn("⚠️ [AUTH]: Identity not matched in database cluster.");
                }
            }
        } catch (err) {
            setError("INDUSTRIAL ERROR: Database node unreachable or network interruption.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-[80vh] flex flex-col items-center justify-center">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md bg-slate-900/40 border border-slate-800 p-10 rounded-3xl backdrop-blur-xl shadow-2xl space-y-8"
            >
                <div className="text-center space-y-2">
                    <div className="mx-auto h-12 w-12 rounded-xl bg-emerald-500 flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(16,185,129,0.3)]">
                        <ShieldCheck className="text-white" size={24} />
                    </div>
                    <h1 className="text-3xl font-bold text-white">Vantix Gate</h1>
                    <p className="text-slate-400">Access your VANTIX Command Center</p>
                </div>

                <form onSubmit={handleLogin} className="space-y-4">
                    <div className="space-y-2">
                        <div className="relative">
                            <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                            <input
                                type="text"
                                placeholder="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all font-medium"
                            />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <div className="relative">
                            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                            <input
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="w-full bg-slate-800/50 border border-slate-700 rounded-xl pl-12 pr-4 py-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all font-medium"
                            />
                        </div>
                    </div>

                    {error && <div className="text-red-400 text-xs text-center font-bold px-4 py-2 bg-red-400/10 rounded-lg">{error}</div>}

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-white text-black hover:bg-emerald-500 hover:text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all group disabled:opacity-50"
                    >
                        {isLoading ? <Loader2 className="animate-spin" /> : <>Log In <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" /></>}
                    </button>
                </form>

                <div className="text-center">
                    <span className="text-sm text-slate-500">Don&apos;t have an account? </span>
                    <Link href="/auth/signup" className="text-sm text-emerald-400 font-bold hover:underline">Sign Up</Link>
                </div>
            </motion.div>
        </div>
    );
}
