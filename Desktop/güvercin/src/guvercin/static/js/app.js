/**
 * GüvercinIhale — Global Alpine.js app state
 */
function app() {
    return {
        user: null,
        token: null,

        async init() {
            this.token = localStorage.getItem('token');
            if (this.token) {
                try {
                    const res = await fetch('/auth/me', {
                        headers: { 'Authorization': 'Bearer ' + this.token }
                    });
                    if (res.ok) {
                        this.user = await res.json();
                    } else {
                        this.clearAuth();
                    }
                } catch(e) {
                    this.clearAuth();
                }
            }
        },

        logout() {
            this.clearAuth();
            window.location.href = '/';
        },

        clearAuth() {
            localStorage.removeItem('token');
            this.token = null;
            this.user = null;
        }
    }
}
