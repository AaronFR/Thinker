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

                <h2>
                    🧰 AI Toolkit 🧰
                </h2>

                <div className="card-container">
                    <div className="card left-card">
                        <div className='header'>
                            <h3><b className='red-text'>NOT</b> another Subscription</h3>
                            <span className="emoji">¢</span>
                        </div>
                        <p>Pay per prompt, with no recurring fees</p>
                        <p>Fairly priced with a 1% margin to cover hosting costs (ZERO % in β, i.e. at a loss)</p>
                        <p 
                            id="😉"
                            data-tooltip-id="tooltip"
                            data-tooltip-html={TooltipConstants.limitDetails}
                            data-tooltip-place="bottom"
                        >
                            No qoutas
                        </p>
                    </div>
                    <div className="card left-card">
                        <div className='header'>
                            <h3>Powerful</h3>
                            <span className="emoji">💪</span>
                        </div>
                        <p>Generate many response at once, the best selected automatically</p>
                        <p>Generate files, hundreds of responses long</p>
                        <p>Rewrite many files simultaneously from a single request</p>

                    </div>
                    <div className="card right-card">
                        <div className='header'>
                            <h3>User Friendly</h3>
                            <span className="emoji">😘</span>
                        </div>
                        <p>Use AI to rewrite or question your messages in advance.</p>
                        <p>Messages categorised automatically, with custom instructions of your choosing for each.</p>
                        <p>Activate/Deactivate/Customise any feature</p>
                    </div>
                    <div className="card right-card">
                        <div className='header'>
                            <h3>Open Source</h3>
                            <span className="emoji-large">👐</span>
                        </div>
                        <p>Open and transparent</p>
                        <p>Developing a tool for the community, not for profiteering. Review our development process and contribute</p>
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
            
            <div className="video">
                <iframe
                    src="https://www.youtube.com/embed/N3GOj288DOc"
                    style={{ width: "100%", aspectRatio: "16 / 9" }}
                    allowFullScreen
                    title="YouTube video"
                ></iframe>
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
