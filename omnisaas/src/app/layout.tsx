'use client';

import { AuthProvider, useAuth } from "@/context/AuthContext";
import { Inter } from "next/font/google";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getUserBalance } from "@/lib/api";
import "./globals.css";
import { LayoutDashboard, Video, GraduationCap, BookOpen, Zap, LogOut, History, Coins, Plus, Loader2, ShieldCheck } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    // 🛡️ [SECURITY] Allow public access to the landing page (/)
    if (!isAuthenticated && !pathname.startsWith('/auth') && pathname !== '/') {
      router.push('/auth/login');
    }
  }, [isAuthenticated, pathname, router]);

  if (!isAuthenticated && !pathname.startsWith('/auth') && pathname !== '/') {
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

  useEffect(() => {
    if (!isAuthPage) {
      getUserBalance().then(data => setBalance(data.balance)).catch(() => { });
      const interval = setInterval(() => {
        getUserBalance().then(data => setBalance(data.balance)).catch(() => { });
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [isAuthPage]);

  if (isAuthPage) return <main className="p-8">{children}</main>;

  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
    { name: 'Shorts', icon: Video, path: '/shorts' },
    { name: 'Courses', icon: GraduationCap, path: '/courses' },
    { name: 'E-Books', icon: BookOpen, path: '/ebooks' },
    { name: 'API Vault', icon: Zap, path: '/settings/api' },
    { name: 'Library', icon: History, path: '/library' },
    { name: 'Buy Credits', icon: Coins, path: '/recharge' },
  ];

  // 👑 [ADMIN] Direct Oracle Link
  if (user === "uday") {
    navItems.push({ name: 'Command Center', icon: ShieldCheck, path: '/admin' });
  }

  // 🏗️ [LAYOUT] Cinematic Mode: Hide sidebar on landing page for visitors
  const showSidebar = !(!isAuthenticated && pathname === '/');

  return (
    <div className="relative flex min-h-screen font-sans">
      {/* Dashboard Sidebar */}
      {showSidebar && (
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-slate-800/50 bg-[#020617]/80 backdrop-blur-xl">
          <div className="flex h-full flex-col px-4 py-6">
            <div className="mb-10 flex items-center gap-3 px-2">
              <div className="h-8 w-8 rounded-lg bg-emerald-500 shadow-[0_0_20px_rgba(16,185,129,0.6)]" />
              <span className="text-xl font-black tracking-[0.15em] text-white uppercase italic">VANTIX</span>
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
                <div className="text-slate-400 leading-relaxed">[QUEUE_MANAGER] Shorts Factory {"->"} Received 1500 tokens</div>
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

              <Link
                href="/recharge"
                className="w-full py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-black uppercase tracking-widest hover:bg-emerald-500 hover:text-white transition-all flex items-center justify-center gap-2 group"
              >
                <Plus size={12} className="group-hover:rotate-90 transition-transform" />
                Upgrade Node
              </Link>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className={`${showSidebar ? 'ml-64' : ''} flex-1 p-8`}>
        <div className={showSidebar ? "max-w-7xl mx-auto" : ""}>
          {children}
        </div>
      </main>
    </div>
  );
}
