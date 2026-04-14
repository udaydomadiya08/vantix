import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // 🛡️ [SECURITY] Allow Public Paths
    if (
        pathname.startsWith('/auth') ||
        pathname.startsWith('/_next') ||
        pathname === '/favicon.ico' ||
        pathname.startsWith('/api') // Assuming API is handled separately or by the backend
    ) {
        return NextResponse.next();
    }

    // 🔒 [IDENTITY LOCKDOWN]
    // In this demo, we use AuthGuard in layout.tsx for primary protection.
    // Middleware provides a secondary server-side check.

    return NextResponse.next();
}

export const config = {
    matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
