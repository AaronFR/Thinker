import React, { useEffect, useState, useCallback } from 'react';
import PropTypes from 'prop-types';

import { handleLogin, handleRegister, handleLogout } from '../../utils/loginUtils';
import { About, BetaBanner, Pitch } from '../Guide/Guide';

import { Tooltip } from 'react-tooltip';
import TooltipConstants from '../../constants/tooltips';

import './Login.css';


export function Login({ isAuthenticated }) {
    const [isLoginMode, setIsLoginMode] = useState(true); // Toggles between Login and Register
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    // Effect to set initial mode based on localStorage
    useEffect(() => {
        const hasAccount = localStorage.getItem('hasAccount');
        if (hasAccount === 'true') {
            setIsLoginMode(true);
        } else {
            setIsLoginMode(false);
        }
    }, []);

    const handleSwitch = () => {
        // If user already has an account, restrict switching to Register mode
        setIsLoginMode(!isLoginMode);
        setError('');
    }

    // Handles login or registration based on the current mode
    const handleButtonClick = useCallback(async () => {
        try {
            if (isLoginMode) {
                await handleLogin(email, password);
                localStorage.setItem('hasAccount', 'true');
            } else {
                await handleRegister(email, password);
                localStorage.setItem('hasAccount', 'true');
                setIsLoginMode(true);
            }
            setError('');  // Clear error on successful login or registration
        } catch (err) {
            setError(err.message || 'An error occurred. Please try again.');
        }
    }, [isLoginMode, email, password]);

    return (
        <div className='scrollable container background'>
            <div className="auth-container">
                <div className='logo'>
                    <div className='beta-symbol'>β</div>
                    <div className='thinker'>The Thinker AI</div>
                </div>

                <h1>
                    🧰 AI toolkit 🧰
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
                        <p>Developing a robust tool for the community, not for profiteering off 'hype'. Review our development process and contribute</p>
                        <p  style={{opacity: 0.1}}
                            data-tooltip-id="tooltip"
                            data-tooltip-html={TooltipConstants.bountyDetails}
                            data-tooltip-place="bottom"
                        >
                            Bounties in future at $30/hr (<b><i>subject to review</i></b>), I dunno message me
                        </p>
                    </div>
                </div>

                {/** Error message display */}
                {error && <p className="error-message">{error}</p>}


                {!isAuthenticated ? (
                    <div>
                        <div className="centered auth-toggle">
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
                                className='login-button'
                                type="button" 
                                onClick={handleButtonClick}>
                                {isLoginMode ? 'Login' : 'Register'}
                            </button>
                        </form>
                    </div>) : (
                        <button onClick={handleLogout} className="logout-button">Logout</button>
                )}



                
                <p className='version-number'>v0.9.4</p>
            </div>
            <BetaBanner />
            <Pitch />
            <About />

            <Tooltip id="tooltip" />          
        </div>
    );
}

Login.propTypes = {
    isAuthenticated: PropTypes.bool.isRequired,
};

export default Login;
