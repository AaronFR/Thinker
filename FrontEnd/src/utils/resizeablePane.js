import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import './styles/ResizablePane.css';

/**
 * ResizablePane component which allows resizing of child elements.
 *
 * @param {Object} props - Component props.
 * @param {React.ReactNode} props.children - Two child components: left and right panes.
 * @param {string} props.className - Additional class names for styling.
 * @returns {JSX.Element} The rendered ResizablePane component.
 */
const ResizablePane = ({ children, className }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [paneWidth, setPaneWidth] = useState(45); // Percentage without %

    const handleDragStart = (clientX) => {
        setIsDragging(true);
    };

    const handleDrag = (clientX) => {
        if (!isDragging) return;
        const container = document.querySelector('.resizable-container');
        if (!container) return;

        const containerRect = container.getBoundingClientRect();
        let newWidth = ((clientX - containerRect.left) / containerRect.width) * 100; // Convert to percentage
        newWidth = Math.max(10, Math.min(newWidth, 90)); // Restrict between 20% and 80%
        setPaneWidth(newWidth);
    };

    const handleDragEnd = () => {
        setIsDragging(false);
    };

    // Mouse Events
    const handleMouseDown = (e) => {
        e.preventDefault();
        handleDragStart(e.clientX);
    };

    const handleMouseMove = (e) => {
        handleDrag(e.clientX);
    };

    const handleMouseUp = () => {
        handleDragEnd();
    };

    // Touch Events
    const handleTouchStart = (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        handleDragStart(touch.clientX);
    };

    const handleTouchMove = (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        handleDrag(touch.clientX);
    };

    const handleTouchEnd = () => {
        handleDragEnd();
    };

    useEffect(() => {
        if (isDragging) {
            // Mouse Events
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
            // Touch Events
            window.addEventListener('touchmove', handleTouchMove, { passive: false });
            window.addEventListener('touchend', handleTouchEnd);
        } else {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
            window.removeEventListener('touchmove', handleTouchMove);
            window.removeEventListener('touchend', handleTouchEnd);
        }

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
            window.removeEventListener('touchmove', handleTouchMove);
            window.removeEventListener('touchend', handleTouchEnd);
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
                onTouchStart={handleTouchStart}
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
