import React from 'react';

import { csrfFetch } from '../../utils/authUtils'

const flask_port = "http://localhost:5000";

export function Login() {
    const handleRegister = async () => {
        try {
            const response = await fetch(`${flask_port}/register`, {
                method: 'POST',
                credentials: "include", // Ensure cookies are sent/received
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({}) // Currently, no data is required in the request body
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
        <div className="register-container">
            <nav className="register-nav">
                <a href="/" className="link">Home</a>
                <a href="/pricing" className="link">Pricing</a>
            </nav>
            
            <h2>Register</h2>
            <button onClick={handleRegister}>Register</button>
            <button onClick={handleLogout}>Logout</button>
        </div>
    );
}

export default Login;
