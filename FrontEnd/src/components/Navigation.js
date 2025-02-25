import React, { useMemo } from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';

import './styles/Navigation.css';

// Default navigation links moved outside the component to avoid recreating on every render
const defaultNavLinks = [
  { name: 'Guide', path: '/guide' },
  { name: 'Messages', path: '/messages' },
  { name: 'Home', path: '/' },
  { name: 'Settings', path: '/settings' },
  { name: 'Pricing', path: '/pricing' },
];

const Navigation = ({ navLinks }) => {
  // Memoize the rendered nav items to reduce unnecessary recalculations
  const navItems = useMemo(() => {
    return navLinks.map(link => (
      <li key={link.path} className="nav-item">
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
    ));
  }, [navLinks]);

  return (
    <nav className="navigation" aria-label="Main Navigation">
      <ul className="nav-list">
        {navItems}
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
  ),
};

Navigation.defaultProps = {
  navLinks: defaultNavLinks,
};

export default React.memo(Navigation);
