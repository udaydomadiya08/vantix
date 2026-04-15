export const IS_BROWSER = typeof window !== 'undefined';
export let API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

if (IS_BROWSER) {
    const isVercel = window.location.hostname.includes('vercel.app');
    if (isVercel && (!process.env.NEXT_PUBLIC_API_BASE || API_BASE.includes('127.0.0.1'))) {
        API_BASE = window.location.origin; // 🛰️ [Sovereign Proxy] Hit same-origin Vercel node
        console.log("🛠️ [VANTIX PROXY]: Infrastructure synchronized to production origin -> " + API_BASE);
    }
}

console.log(`📡 [INFRASTRUCTURE]: Active synthesis node -> ${API_BASE}`);

function getHeaders() {
    const headers: Record<string, string> = {
        "Content-Type": "application/json"
    };

    // 🔒 [SECURITY] Inject JWT Token
    if (typeof window !== "undefined") {
        const token = localStorage.getItem("vantix_token");
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        // Optional: Real-time header overrides from Vault
        const stored = localStorage.getItem("vantix_api_keys");
        if (stored) {
            try {
                const keys = JSON.parse(stored);
                if (keys.groq) headers["X-Groq-Key"] = keys.groq;
                if (keys.openrouter) headers["X-Openrouter-Key"] = keys.openrouter;
                if (keys.pexels) headers["X-Pexels-Key"] = keys.pexels;
                if (keys.pixabay) headers["X-Pixabay-Key"] = keys.pixabay;
            } catch (e) { }
        }
    }
    return headers;
}

export async function generateVideo(topic: string, options: any = {}) {
    const response = await fetch(`${API_BASE}/generate/video`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ topic, ...options }),
    });
    
    if (!response.ok) {
        const error: any = new Error("Vantix Production Node Failure");
        error.status = response.status;
        error.detail = await response.json().catch(() => ({}));
        throw error;
    }
    return response.json();
}

export async function generateEbook(topic: string, options: any = {}) {
    const response = await fetch(`${API_BASE}/generate/ebook`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ topic, ...options }),
    });

    if (!response.ok) {
        const error: any = new Error("Vantix E-book Node Failure");
        error.status = response.status;
        error.detail = await response.json().catch(() => ({}));
        throw error;
    }
    return response.json();
}

export async function checkStatus() {
    const response = await fetch(`${API_BASE}/`);
    return response.json();
}

export async function getJobStatus(jobId: string) {
    const response = await fetch(`${API_BASE}/status/${jobId}`, {
        headers: getHeaders()
    });
    if (!response.ok) return null;
    return response.json();
}

export async function syncUserKeys(keys: any) {
    const response = await fetch(`${API_BASE}/user/keys`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(keys),
    });
    
    const result = await response.json();
    if (response.ok) {
        // 🔒 [SYNC] Harmonize backend vault with local cluster session
        // We now store exactly what the server confirmed
        localStorage.setItem("vantix_api_keys", JSON.stringify(result));
    }
    return result;
}

export async function logout() {
    localStorage.removeItem("vantix_token");
    localStorage.removeItem("vantix_user");
    localStorage.removeItem("vantix_api_keys");
}

export async function loginUser(credentials: any) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials),
    });
    return response.json();
}

export async function signupUser(user: any) {
    const response = await fetch(`${API_BASE}/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
    });
    return response.json();
}

export async function getUserKeys() {
    const response = await fetch(`${API_BASE}/user/keys`, {
        headers: getHeaders(),
    });
    return response.json();
}

export async function generateCourse(topic: string, options: any = {}) {
    const response = await fetch(`${API_BASE}/generate/course`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ topic, ...options }),
    });

    if (!response.ok) {
        const error: any = new Error("Vantix Course Node Failure");
        error.status = response.status;
        error.detail = await response.json().catch(() => ({}));
        throw error;
    }
    return response.json();
}

export async function getUserDefaults() {
    const response = await fetch(`${API_BASE}/user/defaults`, {
        headers: getHeaders(),
    });
    return response.json();
}

export async function updateUserDefaults(factoryType: string, settings: any) {
    const response = await fetch(`${API_BASE}/user/defaults`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ factory_type: factoryType, settings }),
    });
    return response.json();
}

export async function generateThumbnail(topic: string) {
    const response = await fetch(`${API_BASE}/generate-thumbnail`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ topic }),
    });
    
    if (!response.ok) {
        const error: any = new Error("Vantix Thumbnail Node Failure");
        error.status = response.status;
        error.detail = await response.json().catch(() => ({}));
        throw error;
    }
    return response.json();
}

export async function cancelJob(jobId: string) {
    const response = await fetch(`${API_BASE}/status/${jobId}`, {
        method: "DELETE",
        headers: getHeaders(),
    });
    return response.json();
}

export async function getHistory() {
    const response = await fetch(`${API_BASE}/history`, {
        headers: getHeaders(),
    });
    return response.json();
}

export async function getUserBalance() {
    const response = await fetch(`${API_BASE}/user/balance`, {
        headers: getHeaders(),
    });
    return response.json();
}

export async function reloadCredits(amount: number) {
    const response = await fetch(`${API_BASE}/payments/reload?amount=${amount}`, {
        method: "POST",
        headers: getHeaders(),
    });
    return response.json();
}

export async function createCheckoutSession(planId: string) {
    const response = await fetch(`${API_BASE}/payments/create-checkout-session`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({ plan_id: planId }),
    });
    return response.json();
}

export async function getAdminStats() {
    const response = await fetch(`${API_BASE}/admin/stats`, {
        headers: getHeaders(),
    });
    return response.json();
}

export async function getAdminUsers() {
    const response = await fetch(`${API_BASE}/admin/users`, {
        headers: getHeaders(),
    });
    return response.json();
}
