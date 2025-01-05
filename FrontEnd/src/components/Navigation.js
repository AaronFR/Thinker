import React from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';

import './styles/Navigation.css';

/**
 * Navigation Component
 * 
 * Renders a centralized navigation bar with multiple links.
 * Provides accessibility features and active link highlighting.
 * 
 * :param navLinks: An array of navigation link objects.
 * :type navLinks: Array<{ name: string, path: string }>
 */
const Navigation = ({ navLinks }) => {
    return (
        <nav className="navigation" aria-label="Main Navigation">
            <ul className="nav-list">
                {navLinks.map((link, index) => (
                    <li key={index} className="nav-item">
                        <NavLink 
                            to={link.path} 
                            className="nav-link" 
                            activeClassName="active" 
                            exact
                            aria-current="page"
                        >
                            {link.name}
                        </NavLink>
                    </li>
                ))}
            </ul>
        </nav>
    );
};

Navigation.propTypes = {
    navLinks: PropTypes.arrayOf(
        PropTypes.shape({
            name: PropTypes.string.isRequired,
            path: PropTypes.string.isRequired,
        })
    ).isRequired,
};

/**
 * Default navigation links.
 */
Navigation.defaultProps = {
    navLinks: [
        { name: 'Home', path: '/' },
        { name: 'Settings', path: '/settings' },
        { name: 'Pricing', path: '/pricing' },
        // Add more links as needed
    ],
};

export default React.memo(Navigation);
