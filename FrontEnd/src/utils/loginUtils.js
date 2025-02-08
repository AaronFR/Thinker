import { loginEndpoint, logoutSessionEndpoint, registerEndpoint } from "../constants/endpoints";
import { apiFetch } from "./authUtils";

    
    /**
     * Sends a POST request to the specified endpoint with the provided data.
     *
     * @param {string} route: The API route to send the request to.
     * @param {Object} data: The payload to include in the request body.
     * @returns {Promise<Response>} The fetch response.
     * @raises {Error} If the fetch request fails.
     */
    const postRequest = async (endpoint, data) => {
        try {
            const response = await apiFetch(endpoint, {
                method: 'POST',
                body: JSON.stringify(data),
            },
            false);
            return response;
        } catch (error) {
            console.error(`Error in postRequest to ${endpoint}:`, error);
            throw error;
        }
    };

   /**
    * Handles user login by sending credentials to the login endpoint.
    *
    * @param {string} email - The user's email address.
    * @param {string} password - The user's password.
    */
    export const handleLogin = async ( email, password ) => {
        try {
            const response = await postRequest(loginEndpoint, { email, password });

            if (response.ok) {
                alert('Login successful!');
                window.location.href = "/";
            } else {
                alert('Failed to login.');
                console.error('Login request failed with status:', response.status);
            }
        } catch (error) {
            alert('An error occurred during login.');
        }
    };

    /**
     * Handles user registration by sending credentials to the register endpoint.
     *
     * @param {string} email - The user's email address.
     * @param {string} password - The user's password.
     */
    export const handleRegister = async ( email, password ) => {
        try {
            const response = await postRequest(registerEndpoint, { email, password });

            if (response.ok) {
                alert('User registered successfully!');
                window.location.href = "/";
            } else {
                alert('Failed to register user.');
                console.error('Register request failed with status:', response.status);
            }
        } catch (error) {
            alert('An error occurred during registration.');
        }
    };

    /**
     * Handles user logout by sending a POST request to the logout endpoint.
     */
    export const handleLogout = async () => {
        try {
            const response = await apiFetch(logoutSessionEndpoint, {
                method: "POST",
            });
    
            if (response.ok) {
                alert('Logout successful!');
                window.location.href = "/login";
            } else {
                console.error("Logout failed");
            }
        } catch (error) {
            console.error("Error logging out:", error);
        }
    };