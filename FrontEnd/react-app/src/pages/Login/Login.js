import React, { useState, useCallback } from 'react';

import { csrfFetch } from '../../utils/authUtils';

import './Login.css';


const FLASK_PORT = "http://localhost:5000";

export function Login() {
    const [isLoginMode, setIsLoginMode] = useState(true); // Toggles between Login and Register
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    
    const handleSwitch = () => {
        setIsLoginMode(!isLoginMode)
    }

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

    const handleLogin = async () => {
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

    const handleRegister = async () => {
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
    const handleLogout = useCallback(async () => {
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
    });

    return (
        <div className="auth-container">
            <nav className="auth-nav">
                <a href="/" className="link">Home</a>
                <a href="/pricing" className="link">Pricing</a>
            </nav>

            <div className="auth-toggle">
                <button 
                    className={`toggle-button ${isLoginMode ? 'active' : ''}`} 
                    onClick={handleSwitch}>
                    Login
                </button>
                <button 
                    className={`toggle-button ${!isLoginMode ? 'active' : ''}`} 
                    onClick={handleSwitch}>
                    Register
                </button>
            </div>

            <h2>{isLoginMode ? 'Login' : 'Register'}</h2>

            <form className="auth-form" onSubmit={(e) => e.preventDefault()}>
                <div className="form-group">
                    <label htmlFor="email">Email:</label>
                    <input 
                        id="email"
                        type="email" 
                        value={email} 
                        onChange={(e) => setEmail(e.target.value)} 
                        required 
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="password">Password:</label>
                    <input 
                        id="password"
                        type="password" 
                        value={password} 
                        onChange={(e) => setPassword(e.target.value)} 
                        required 
                    />
                </div>

                <button 
                    type="button" 
                    onClick={isLoginMode ? handleLogin : handleRegister}>
                    {isLoginMode ? 'Login' : 'Register'}
                </button>
            </form>


            <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
    );
}

export default Login;
