import React, { useEffect, useState, useCallback } from 'react';
import PropTypes from 'prop-types';

import { handleLogin, handleRegister, handleLogout } from '../../utils/loginUtils';
import { About, BetaBanner, Pitch } from '../Guide/Guide';
import Navigation from "../../components/Navigation";

import { Tooltip } from 'react-tooltip';
import TooltipConstants from '../../constants/tooltips';

import './Login.css';
import GitHubButton from '../../components/GitHubButton';


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
            {isAuthenticated && <Navigation />}
            <GitHubButton />

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
                        <p 
                            id="😉"
                            data-tooltip-id="tooltip"
                            data-tooltip-html={TooltipConstants.limitDetails}
                            data-tooltip-place="bottom"
                        >
                            We want you to use AI as much as possible. No qouta's, no limits but the ones you set
                        </p>
                    </div>
                    <div className="card left-card">
                        <div className='header'>
                            <h3>User Friendly</h3>
                            <span className="emoji">😘</span>
                        </div>
                        <p>Use AI to help use AI with automated helper functionality</p>
                        <p>Activate/De-activate or customise any feature you want enabled</p>
                        <p id="fully, later">All configurable, with more options and settings to come</p>
                    </div>
                    <div className="card right-card">
                        <div className='header'>
                            <h3>Powerful</h3>
                            <span className="emoji">💪</span>
                        </div>
                        <p>Utilise AI workflows to make requests of <b><i>any</i></b> size</p>
                        <p>Rewrite many files at once, write arbitrarily long documents with a single prompt</p>
                        <p style={{opacity: 0.1}}>Maybe one day a whole code base? ¯\_(ツ)_/¯</p>
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

                <p className='version-number'>v0.10.0</p>
            </div>
            <BetaBanner />
            
            <div className="centered">
                <iframe width="860" height="480"
                src="https://www.youtube.com/embed/syfUbWpO7Cg">
                </iframe>
            </div>

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
