'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

interface AuthContextType {
    user: string | null;
    token: string | null;
    login: (username: string, token: string) => void;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<string | null>(null);
    const [token, setToken] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        const storedUser = localStorage.getItem('vantix_user');
        const storedToken = localStorage.getItem('vantix_token');

        if (storedUser && storedToken) {
            setUser(storedUser);
            setToken(storedToken);
        }
        setIsLoading(false);
    }, []);

    const login = (username: string, authToken: string) => {
        setUser(username);
        setToken(authToken);
        localStorage.setItem('vantix_user', username);
        localStorage.setItem('vantix_token', authToken);
        router.push('/');
    };

    const logout = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('vantix_user');
        localStorage.removeItem('vantix_token');
        router.push('/auth/login');
    };

    if (isLoading) return null;

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!token }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
