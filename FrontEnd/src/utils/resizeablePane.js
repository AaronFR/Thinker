import React, { useState, useEffect, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';

import './styles/ResizablePane.css';

/**
 * ResizablePane component which allows resizing of child elements.
 *
 * @param {React.ReactNode} props.children - Two child components: left and right panes.
 * @param {string} props.className - Additional class names for styling.
 * @returns {JSX.Element} The rendered ResizablePane component.
 */
const ResizablePane = ({ children, className }) => {
    if (React.Children.count(children) !== 2) {
        console.error('ResizablePane expects exactly two children: left and right panes.');
    }

    const [paneWidth, setPaneWidth] = useState(45);
    const [isDragging, setIsDragging] = useState(false);
    const containerRef = useRef(null);
    const draggingRef = useRef(false);

    useEffect(() => {
        draggingRef.current = isDragging;
    }, [isDragging]);

    const onMouseMove = useCallback((e) => {
        if (!draggingRef.current || !containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        let newWidth = ((e.clientX - rect.left) / rect.width) * 100;
        newWidth = Math.max(10, Math.min(newWidth, 90));
        setPaneWidth(newWidth);
    }, []);

    const onMouseUp = useCallback(() => {
        if (draggingRef.current) setIsDragging(false);
    }, []);

    const onTouchMove = useCallback((e) => {
        if (!draggingRef.current || !containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const touch = e.touches[0];
        let newWidth = ((touch.clientX - rect.left) / rect.width) * 100;
        newWidth = Math.max(0, Math.min(newWidth, 90));
        setPaneWidth(newWidth);
        e.preventDefault();
    }, []);

    const onTouchEnd = useCallback(() => {
        if (draggingRef.current) setIsDragging(false);
    }, []);

    useEffect(() => {
        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
        window.addEventListener('touchmove', onTouchMove, { passive: false });
        window.addEventListener('touchend', onTouchEnd);
        return () => {
            window.removeEventListener('mousemove', onMouseMove);
            window.removeEventListener('mouseup', onMouseUp);
            window.removeEventListener('touchmove', onTouchMove);
            window.removeEventListener('touchend', onTouchEnd);
        };
    }, [onMouseMove, onMouseUp, onTouchMove, onTouchEnd]);

    const onMouseDown = useCallback((e) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const onTouchStart = useCallback((e) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const onKeyDown = useCallback((e) => {
        const increment = 2;
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            setPaneWidth((prev) => Math.max(10, prev - increment));
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            setPaneWidth((prev) => Math.min(90, prev + increment));
        }
    }, []);

    return (
        <div
            ref={containerRef}
            className={`resizable-container ${className}`}
            style={{ display: 'flex', width: '100%', height: '100%' }}
        >
            <div
                className="left-pane"
                style={{ width: `${paneWidth}%`, flexShrink: 0, overflow: 'hidden' }}
            >
                {children[0]}
            </div>
            <div
                className={`resizer ${isDragging ? 'resizing' : ''}`}
                onMouseDown={onMouseDown}
                onTouchStart={onTouchStart}
                role="separator"
                aria-orientation="vertical"
                aria-label="Resize panes"
                tabIndex={0}
                onKeyDown={onKeyDown}
            />
            <div className="right-pane" style={{ flex: 1, overflow: 'auto' }}>
                {children[1]}
            </div>
        </div>
    );
};

ResizablePane.propTypes = {
    children: PropTypes.node.isRequired,
    className: PropTypes.string,
};

ResizablePane.defaultProps = {
    className: '',
};

export default ResizablePane;
