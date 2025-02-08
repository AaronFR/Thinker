import { refreshSessionEndpoint } from "../constants/endpoints";

/**
 * Retrieves the value of a specific cookie by name.
 *
 * @param {string} name - The name of the cookie to retrieve.
 * @returns {string|null} The value of the cookie if found; otherwise, null.
 */
const getCookie = (name) => {
    const cookieString = document.cookie;
    if (!cookieString) return null;
    const cookies = cookieString.split('; ');
    const cookie = cookies.find(row => row.startsWith(`${name}=`));
    return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
};

export const apiFetch = async (url, options = {}, requiresAuth = true) => {


    // Extract CSRF and tokens if needed
    const csrfToken = getCookie('csrf_access_token');

    // Define default headers // ToDo: Is this vunerable to XSS attacks?
    const defaultHeaders = {
        "X-CSRF-TOKEN": csrfToken,
        "Content-Type": "application/json",
    };

    options.headers = { ...defaultHeaders, ...(options.headers || {}) };
    options.credentials = "include"; // Ensure cookies are included

    let response;
    try {
        response = await fetch(url, options)
    } catch (error) {
        console.error(`Fetch request to ${url} failed:`, error)
        throw error
    }

    if (requiresAuth && response.status === 401) {
        console.log("Access token expired, attempting refresh...");

        try {
        
            // Attempt to refresh the token
            const refreshResponse = await fetch(refreshSessionEndpoint, {
                method: 'POST',
                credentials: 'include', // Include cookies for refresh
            });

            if (!refreshResponse.ok) {
                throw new Error('Failed to refresh token. Please log in again.');
            }

            // Retry the original request
            response = await fetch(url, options);
        } catch (error) {
            console.error('apiFetch error:', error);
            throw error;
        }
    }

    return response
};
