import React, { useState } from 'react';

import { csrfFetch } from '../../utils/authUtils'
import './Login.css'

const flask_port = "http://localhost:5000";

export function Login() {
    const [isLoginMode, setIsLoginMode] = useState(true); // Toggles between Login and Register
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    
    const handleSwitch = () => {
        setIsLoginMode(!isLoginMode)
    }

    const handleLogin = async () => {
        try {
            const response = await csrfFetch(`${flask_port}/login`, {
                method: 'POST',
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                alert('Login successful!');
                window.location.href = "/";
            } else {
                alert('Failed to login.');
                console.error('Login request failed with status:', response.status);
            }
        } catch (error) {
            alert('An error occurred during login.');
            console.error('Error logging in:', error);
        }
    };

    const handleRegister = async () => {
        try {
            const response = await fetch(`${flask_port}/register`, {
                method: 'POST',
                credentials: "include", // Ensure cookies are sent/received
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                alert('User registered successfully!');
            } else {
                alert('Failed to register user.');
                console.error('Register request failed with status:', response.status);
            }
        } catch (error) {
            alert('An error occurred during registration.');
            console.error('Error registering user:', error);
        }
    };
    
    const handleLogout = async () => {
        try {
            const response = await csrfFetch(`${flask_port}/logout`, {
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
                    <label>Email:</label>
                    <input 
                        type="email" 
                        value={email} 
                        onChange={(e) => setEmail(e.target.value)} 
                        required 
                    />
                </div>

                <div className="form-group">
                    <label>Password:</label>
                    <input 
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
