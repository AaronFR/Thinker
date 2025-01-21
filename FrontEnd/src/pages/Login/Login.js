import React, { useState, useCallback } from 'react';

import { handleLogin, handleRegister, handleLogout } from '../../utils/loginUtils';
import { About, Tutorial } from '../Guide/Guide';

import './Login.css';


export function Login() {
    const [isLoginMode, setIsLoginMode] = useState(true); // Toggles between Login and Register
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    
    const handleSwitch = () => {
        setIsLoginMode(!isLoginMode)
        setError('');  // Clear any previous errors when switching
    }

    // Handles login or registration based on the current mode
    const handleButtonClick = useCallback(async () => {
        try {
            if (isLoginMode) {
                await handleLogin(email, password);
            } else {
                await handleRegister(email, password);
            }
            setError('');  // Clear error on successful login or registration
        } catch (err) {
            setError(err.message || 'An error occurred. Please try again.');
        }
    }, [isLoginMode, email, password]);

    return (
        <div className='scrollable container'>
            <div className="auth-container">
                <div className='logo'>
                    <div className='beta-symbol'>β</div>
                    <div className='thinker'>The Thinker AI</div>
                </div>

                <h1>
                    🧰 A toolbox for AI 🧰
                </h1>

                <div className="card-container">
                    <div className="card left-card">
                        <div className='header'>
                            <h3><b className='red-text'>NOT</b> another subscription</h3>
                            <span className="emoji">¢</span>
                        </div>
                        <p>Pay as you go: Pay for what you <i>actually</i> use. Try it out with no recurring fees</p>
                        <p>We want you to use AI as much as possible 😉. No qouta's, no limits</p>
                    </div>
                    <div className="card left-card">
                        <div className='header'>
                            <h3>User Friendly</h3>
                            <span className="emoji">😘</span>
                        </div>
                        <p>Automatically sorted by category, automatic prompt engineering, questions against prompts..</p>
                        <p style={{opacity: 0.3}}>All fully configurable</p>
                        <p>🚧 WIP</p>
                    </div>
                    <div className="card right-card">
                        <div className='header'>
                            <h3>Powerful</h3>
                            <span className="emoji">💪</span>
                        </div>
                        <p>Utilise agentic workflows to make requests of <b><i>any</i></b> size.</p>
                        <p style={{opacity: 0.3}}>From a typical one answer prompt to generating an entire book, code base, *anything*</p>
                        <p>🚧 WIP</p>
                    </div>
                    <div className="card right-card">
                        <div className='header'>
                            <h3>Open Source</h3>
                            <span className="emoji-large">👐</span>
                        </div>
                        <p>Developing a robust tool for the community, not for hype profiteering. Review our development process and contribute.</p>
                        <p style={{opacity: 0.1}}>Bounties in future at $30/hr (<b><i>subject to review</i></b>), I dunno message me</p>
                    </div>
                </div>

                {/** Error message display */}
                {error && <p className="error-message">{error}</p>}

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
                <p className='version-number'>v0.9.3</p>
            </div>
            <About />
            <Tutorial />            
        </div>
    );
}

export default Login;
