/**
 * Learning Platform Router
 * Handles client-side routing for chapters and lessons
 */

const Router = (function () {
    const routes = new Map();
    const history = [];
    let currentRoute = null;

    /**
     * Register a route with its handler
     */
    function register(path, handler) {
        // Convert path to regex pattern
        const pattern = path
            .replace(/\//g, '\\/')
            .replace(/:([^\/]+)/g, '([^\\/]+)')
            .replace(/\*$/g, '(.*)');

        routes.set(new RegExp(`^${pattern}$`), handler);
    }

    /**
     * Navigate to a specific path
     */
    function navigate(path, replace = false) {
        const url = new URL(path, window.location.origin);

        if (replace) {
            window.history.replaceState({ path }, '', url.pathname);
        } else {
            window.history.pushState({ path }, '', url.pathname);
        }

        handleRoute(url.pathname);
    }

    /**
     * Get URL parameters
     */
    function getParams(match, keys) {
        const params = {};
        keys.forEach((key, index) => {
            params[key] = match[index + 1];
        });
        return params;
    }

    /**
     * Handle current route
     */
    function handleRoute(path) {
        let matched = false;

        for (const [pattern, handler] of routes) {
            const match = path.match(pattern);

            if (match) {
                currentRoute = {
                    path,
                    params: getParams(match, (pattern.source.match(/:([^\/]+)/g) || []).map(k => k.slice(1)))
                };

                handler(currentRoute.params, currentRoute);
                matched = true;
                break;
            }
        }

        if (!matched) {
            // Default route - show home
            navigate('/', true);
        }

        // Update active nav
        Navigation.updateActive(path);

        return matched;
    }

    /**
     * Initialize router
     */
    function init() {
        window.addEventListener('popstate', (e) => {
            if (e.state?.path) {
                handleRoute(e.state.path);
            }
        });

        // Handle initial load
        handleRoute(window.location.pathname);
    }

    /**
     * Get current route
     */
    function getCurrentRoute() {
        return currentRoute;
    }

    /**
     * Go back in history
     */
    function back() {
        if (history.length > 0) {
            const prev = history.pop();
            navigate(prev, true);
        }
    }

    return {
        register,
        navigate,
        init,
        getCurrentRoute,
        back
    };
})();

// Export for use
window.Router = Router;