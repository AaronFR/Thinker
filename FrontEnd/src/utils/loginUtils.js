import { csrfFetch } from "./authUtils";

const FLASK_PORT = "http://localhost:5000"

    
    /**
     * Sends a POST request to the specified endpoint with the provided data.
     *
     * :param {string} endpoint: The API endpoint to send the request to.
     * :param {Object} data: The payload to include in the request body.
     * :returns {Promise<Response>} The fetch response.
     */
    const postRequest = async (endpoint, data) => {
        try {
            const response = await csrfFetch(`${FLASK_PORT}/${endpoint}`, {
                method: 'POST',
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });
            return response;
        } catch (error) {
            console.error(`Error in postRequest to ${endpoint}:`, error);
            throw error;
        }
    };

    export const handleLogin = async ( email, password ) => {
        try {
            const response = await postRequest('login', { email, password });

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

    export const handleRegister = async ( email, password ) => {
        try {
            const response = await postRequest('register', { email, password });

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
            const response = await csrfFetch(`${FLASK_PORT}/logout`, {
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