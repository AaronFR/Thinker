// ResizablePane.js
import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './styles/ResizablePane.css';

/**
 * ResizablePane component which allows resizing of child elements.
 *
 * :param {Object} props - Component props.
 * :param {React.ReactNode} props.children - Two child components: left and right panes.
 * :param {string} props.className - Additional class names for styling.
 * :returns {JSX.Element} The rendered ResizablePane component.
 */
const ResizablePane = ({ children, className }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [paneWidth, setPaneWidth] = useState(45); // Percentage without %

    const handleMouseDown = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleMouseMove = (e) => {
        if (!isDragging) return;
        const container = e.target.closest('.resizable-container');
        if (!container) return;
        
        const containerRect = container.getBoundingClientRect();
        let newWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100; // Convert to percentage
        newWidth = Math.max(20, Math.min(newWidth, 80)); // Restrict between 20% and 80%
        setPaneWidth(newWidth);
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    useEffect(() => {
        if (isDragging) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        } else {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        }

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging]);

    return (
        <div className={`resizable-container ${className}`} style={{ display: 'flex', width: '100%', height: '100%' }}>
            <div className="left-pane" style={{ width: `${paneWidth}%`, flexShrink: 0, overflow: 'hidden' }}>
                {children[0]} {/* Left pane content */}
            </div>
            <div
                className={`resizer ${isDragging ? 'resizing' : ''}`}
                onMouseDown={handleMouseDown}
                role="separator"
                aria-orientation="vertical"
                aria-label="Resize panes"
                tabIndex={0}
                onKeyDown={(e) => {
                    // Optional: Implement keyboard resizing if desired
                }}
            />
            <div className="right-pane" style={{ flex: 1, overflow: 'auto' }}>
                {children[1]} {/* Right pane content */}
            </div>
        </div>
    );
};

ResizablePane.propTypes = {
    children: PropTypes.node.isRequired, // Expecting exactly two children
    className: PropTypes.string,
};

export default ResizablePane;
