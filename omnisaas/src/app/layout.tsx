import { LayoutDashboard, Video, GraduationCap, BookOpen, Settings, Zap, User, LogOut, History, Coins, Plus, Loader2, X, ChevronRight, ShieldCheck } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { getUserBalance, reloadCredits } from "@/lib/api";

const inter = Inter({ subsets: ["latin"] });

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated && !pathname.startsWith('/auth')) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, pathname, router]);

  if (!isAuthenticated && !pathname.startsWith('/auth')) {
    return null; // or a loading spinner
  }

  return <>{children}</>;
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth" suppressHydrationWarning={true}>
      <body className={`${inter.className} min-h-screen bg-[#020617] text-slate-100 antialiased`}>
        <AuthProvider>
          <AuthGuard>
            <LayoutContent>{children}</LayoutContent>
          </AuthGuard>
        </AuthProvider>
      </body>
    </html>
  );
}

function LayoutContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { logout, user } = useAuth();
  const isAuthPage = pathname.startsWith('/auth');
  const [balance, setBalance] = useState<number | null>(null);
  const [showRecharge, setShowRecharge] = useState(false);
  const [isRecharging, setIsRecharging] = useState(false);

  useEffect(() => {
    if (!isAuthPage) {
      getUserBalance().then(data => setBalance(data.balance)).catch(() => {});
      const interval = setInterval(() => {
        getUserBalance().then(data => setBalance(data.balance)).catch(() => {});
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [isAuthPage]);

  const handleReload = async (amount: number) => {
    setIsRecharging(true);
    try {
      const data = await reloadCredits(amount);
      setBalance(data.balance);
      setShowRecharge(false);
    } catch (e) {
      alert("Recharge Failed: Commercial Link Interrupted.");
    } finally {
      setIsRecharging(false);
    }
  };

  if (isAuthPage) return <main className="p-8">{children}</main>;

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
    { name: 'Shorts', icon: Video, path: '/shorts' },
    { name: 'Courses', icon: GraduationCap, path: '/courses' },
    { name: 'E-Books', icon: BookOpen, path: '/ebooks' },
    { name: 'API Vault', icon: Zap, path: '/settings/api' },
    { name: 'Library', icon: History, path: '/library' },
  ];

  return (
    <div className="relative flex min-h-screen">
      {/* Dashboard Sidebar */}
      <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-slate-800/50 bg-[#020617]/80 backdrop-blur-xl">
        <div className="flex h-full flex-col px-4 py-6">
          <div className="mb-10 flex items-center gap-3 px-2">
            <div className="h-8 w-8 rounded-lg bg-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.6)]" />
            <span className="text-xl font-black tracking-[0.15em] text-white">VANTIX</span>
          </div>

          <nav className="flex-1 space-y-1">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.path}
                className={`group flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all hover:bg-slate-800/50 hover:text-white ${pathname === item.path ? 'bg-slate-800/50 text-white' : 'text-slate-400'}`}
              >
                <item.icon size={18} className={pathname === item.path ? 'text-emerald-500' : 'text-slate-500 group-hover:text-emerald-500 transition-colors'} />
                {item.name}
              </Link>
            ))}
          </nav>

          <div className="mt-auto space-y-4">
            <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-slate-900/30 border border-slate-800/50">
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-500 text-xs font-bold">
                  {user?.charAt(0).toUpperCase()}
                </div>
                <span className="text-sm font-medium text-slate-300 truncate max-w-[80px]">{user}</span>
              </div>
              <button onClick={logout} className="text-slate-500 hover:text-red-400 transition-colors">
                <LogOut size={16} />
              </button>
            </div>

            <div className="rounded-2xl bg-emerald-500/5 p-5 border border-emerald-500/20 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-emerald-400">
                  <Coins size={14} className="animate-pulse" />
                  <span className="text-[10px] font-black uppercase tracking-[0.2em]">Industrial Power</span>
                </div>
                <span className="text-[10px] font-black text-slate-500 tabular-nums">
                  {balance !== null ? balance : <Loader2 size={10} className="animate-spin" />} C
                </span>
              </div>
              
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 transition-all duration-1000" 
                  style={{ width: `${Math.min((balance || 0) / 2, 100)}%` }}
                />
              </div>

              <button 
                onClick={() => setShowRecharge(true)}
                className="w-full py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-black uppercase tracking-widest hover:bg-emerald-500 hover:text-white transition-all flex items-center justify-center gap-2 group"
              >
                <Plus size={12} className="group-hover:rotate-90 transition-transform" />
                Upgrade Node
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 flex-1 p-8">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>

      {/* 💳 GLOBAL RECHARGE MODAL */}
      <AnimatePresence>
        {showRecharge && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-6 sm:p-0">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => !isRecharging && setShowRecharge(false)}
              className="absolute inset-0 bg-slate-950/80 backdrop-blur-md" 
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-[2.5rem] shadow-2xl overflow-hidden"
            >
              <div className="p-8 space-y-8">
                <div className="flex items-center justify-between">
                   <div className="flex items-center gap-3">
                      <div className="p-3 rounded-2xl bg-emerald-500/10 text-emerald-400">
                         <Zap size={24} />
                      </div>
                      <h2 className="text-xl font-black text-white italic tracking-tight underline decoration-emerald-500/30 decoration-4 underline-offset-4 uppercase">RECHARGE NODE</h2>
                   </div>
                   <button 
                     onClick={() => !isRecharging && setShowRecharge(false)}
                     className="p-2 rounded-xl hover:bg-slate-800 text-slate-500 transition-all font-bold"
                   >
                     <X size={20} />
                   </button>
                </div>

                <div className="space-y-4">
                  <p className="text-slate-400 text-sm font-medium">Inject industrial power to restore synthesis capabilities. Select a recharge vector:</p>
                  
                  <div className="grid grid-cols-1 gap-4">
                    {[
                      { amount: 100, price: '10', label: 'Starter Cell', bonus: 'Basic Power' },
                      { amount: 500, price: '45', label: 'Engine Core', bonus: '10% Extraction Bonus' },
                      { amount: 2000, price: '150', label: 'Industrial Grid', bonus: '25% Optimization' }
                    ].map((plan) => (
                      <button
                        key={plan.amount}
                        disabled={isRecharging}
                        onClick={() => handleReload(plan.amount)}
                        className="p-6 rounded-3xl border border-slate-800 hover:border-emerald-500/50 hover:bg-emerald-500/5 transition-all text-left flex items-center justify-between group disabled:opacity-50"
                      >
                         <div className="space-y-1">
                            <h4 className="text-white font-black text-xs uppercase tracking-widest">{plan.label}</h4>
                            <p className="text-[10px] text-slate-500 font-bold">{plan.amount} Credits // {plan.bonus}</p>
                         </div>
                         <div className="text-right">
                            <span className="text-xs font-black text-emerald-400 uppercase tracking-tighter italic">US ${plan.price}</span>
                            <div className="flex items-center justify-end text-[8px] text-slate-600 font-bold uppercase mt-1 group-hover:text-white transition-colors">
                               Init Transfer <ChevronRight size={10} />
                            </div>
                         </div>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="p-6 rounded-3xl bg-slate-950/50 border border-slate-800/50 flex items-center gap-4">
                   <ShieldCheck size={20} className="text-slate-600" />
                   <div className="text-[10px] text-slate-600 font-medium leading-relaxed uppercase tracking-widest">Transactions secured by Vantix Cryptographic Ledger. Local simulation active.</div>
                </div>
              </div>
              
              {isRecharging && (
                <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm flex flex-col items-center justify-center space-y-4">
                   <Loader2 className="animate-spin text-emerald-500" size={40} />
                   <span className="text-[10px] font-black text-white uppercase tracking-[0.3em] animate-pulse">Synchronizing Ledger...</span>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
