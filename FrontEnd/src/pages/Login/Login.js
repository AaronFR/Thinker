import React, { useState, useCallback } from 'react';

import { handleLogin, handleRegister, handleLogout } from '../../utils/loginUtils';

import './Login.css';


export function Login() {
    const [isLoginMode, setIsLoginMode] = useState(true); // Toggles between Login and Register
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    
    const handleSwitch = () => {
        setIsLoginMode(!isLoginMode)
    }

    const handleButtonClick = () => {
        if (isLoginMode) {
            handleLogin(email, password);
        } else {
            handleRegister(email, password);
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
                    onClick={handleButtonClick}>
                    {isLoginMode ? 'Login' : 'Register'}
                </button>
            </form>


            <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
    );
}

export default Login;
