// Authentication Service - Google OAuth only
class AuthService {
    constructor() {
        this.baseUrl = '';
    }

    getToken() {
        // Get token from localStorage first
        const localStorageToken = localStorage.getItem('token');
        if (localStorageToken) {
            return localStorageToken;
        }

        // Fallback to getting token from cookie (set by Google OAuth callback)
        const name = 'access_token=';
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i].trim();
            if (c.indexOf(name) === 0) {
                const token = c.substring(name.length, c.length);
                // Save to localStorage for future use
                localStorage.setItem('token', token);
                return token;
            }
        }
        return null;
    }

    setToken(token) {
        localStorage.setItem('token', token);
        document.cookie = `access_token=${token}; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=lax`;
    }

    removeToken() {
        localStorage.removeItem('token');
        document.cookie = 'access_token=; path=/; max-age=0; SameSite=lax';
    }

    isAuthenticated() {
        return !!this.getToken();
    }

    loginWithGoogle(redirect = null) {
        const redirectParam = redirect ? `?redirect=${encodeURIComponent(redirect)}` : '';
        window.location.href = `${this.baseUrl}/auth/google/login${redirectParam}`;
    }

    async logout() {
        try {
            await fetch(`${this.baseUrl}/auth/logout`, {
                method: 'POST',
                credentials: 'include'
            });
        } catch (e) {
            // Continue with client-side cleanup even if server call fails
        }
        this.removeToken();
        window.location.href = '/login.html';
    }

    async getCurrentUser() {
        if (!this.isAuthenticated()) {
            throw new Error('Not authenticated');
        }

        try {
            const response = await fetch(`${this.baseUrl}/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });

            if (!response.ok) {
                this.removeToken();
                throw new Error('Session expired');
            }

            return await response.json();
        } catch (error) {
            console.error('Get user error:', error);
            this.removeToken();
            throw error;
        }
    }

    async checkAuthStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/auth/check`, {
                credentials: 'include'
            });
            return await response.json();
        } catch (error) {
            console.error('Auth check error:', error);
            return { authenticated: false };
        }
    }

    async getUserProfile() {
        return this.getCurrentUser();
    }

    async updateProfile(data) {
        if (!this.isAuthenticated()) {
            throw new Error('Not authenticated');
        }

        try {
            const response = await fetch(`${this.baseUrl}/auth/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getToken()}`
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Profile update failed');
            }

            return await response.json();
        } catch (error) {
            console.error('Profile update error:', error);
            throw error;
        }
    }
}

// Initialize authentication service
window.AuthService = AuthService;
const authService = new AuthService();
