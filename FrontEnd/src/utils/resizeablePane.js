import React, { useState, useEffect, useCallback, useRef } from 'react';
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
    // Ensure exactly two children are provided
    if (React.Children.count(children) !== 2) {
        console.error('ResizablePane expects exactly two children: left and right panes.')
    }

    const [isDragging, setIsDragging] = useState(false)
    const [paneWidth, setPaneWidth] = useState(45) // Initial width in percentage

    const containerRef = useRef(null)

    /**
     * Starts the dragging process.
     *
     * @param {number} clientX - The x-coordinate where the drag starts.
     */
    const handleDragStart = useCallback((clientX) => {
        setIsDragging(true)
    }, [])

    /**
     * Handles the dragging action, updating the pane width based on mouse/touch movement.
     *
     * @param {number} clientX - The current x-coordinate during dragging.
     */
    const handleDrag = useCallback(
        (clientX) => {
            if (!isDragging || !containerRef.current) return

            const containerRect = containerRef.current.getBoundingClientRect()
            let newWidth = ((clientX - containerRect.left) / containerRect.width) * 100 // Convert to percentage
            newWidth = Math.max(0, Math.min(newWidth, 90)) // Restrict between 10% and 90%
            setPaneWidth(newWidth)
        },
        [isDragging]
    )

    /**
     * Ends the dragging process.
     */
    const handleDragEnd = useCallback(() => {
        setIsDragging(false)
    }, [])

    /**
     * Handles mouse down event on the resizer.
     *
     * @param {React.MouseEvent} e - The mouse event.
     */
    const handleMouseDown = useCallback(
        (e) => {
            e.preventDefault()
            handleDragStart(e.clientX)
        },
        [handleDragStart]
    )

    /**
     * Handles mouse move event during dragging.
     *
     * @param {React.MouseEvent} e - The mouse event.
     */
    const handleMouseMove = useCallback(
        (e) => {
            handleDrag(e.clientX)
        },
        [handleDrag]
    )

    /**
     * Handles mouse up event to terminate dragging.
     */
    const handleMouseUp = useCallback(() => {
        handleDragEnd()
    }, [handleDragEnd])

    /**
     * Handles touch start event on the resizer.
     *
     * @param {React.TouchEvent} e - The touch event.
     */
    const handleTouchStart = useCallback(
        (e) => {
            e.preventDefault()
            const touch = e.touches[0]
            handleDragStart(touch.clientX)
        },
        [handleDragStart]
    )

    /**
     * Handles touch move event during dragging.
     *
     * @param {React.TouchEvent} e - The touch event.
     */
    const handleTouchMove = useCallback(
        (e) => {
            const touch = e.touches[0]
            handleDrag(touch.clientX)
        },
        [handleDrag]
    )

    /**
     * Handles touch end event to terminate dragging.
     */
    const handleTouchEnd = useCallback(() => {
        handleDragEnd()
    }, [handleDragEnd])

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
            window.removeEventListener('mousemove', handleMouseMove)
            window.removeEventListener('mouseup', handleMouseUp)
            window.removeEventListener('touchmove', handleTouchMove)
            window.removeEventListener('touchend', handleTouchEnd)
        }
    }, [isDragging, handleMouseMove, handleMouseUp, handleTouchMove, handleTouchEnd])

    /**
     * Handles keyboard interactions for the resizer.
     * 
     * ToDo: this doesn't and hasn't worked
     *
     * @param {React.KeyboardEvent} e - The keyboard event.
     */
    const handleKeyDown = useCallback(
        (e) => {
            const increment = 2 // Percentage increment/decrement on each key press
            if (e.key === 'ArrowLeft') {
                e.preventDefault()
                setPaneWidth((prevWidth) => Math.max(10, prevWidth - increment))
            } else if (e.key === 'ArrowRight') {
                e.preventDefault()
                setPaneWidth((prevWidth) => Math.min(90, prevWidth + increment))
            }
        },
        []
    )

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
                onKeyDown={handleKeyDown}
            />
            <div className="right-pane" style={{ flex: 1, overflow: 'auto' }}>
                {children[1]} {/* Right pane content */}
            </div>
        </div>
    )
}

ResizablePane.propTypes = {
    children: PropTypes.node.isRequired, // Expecting exactly two children
    className: PropTypes.string,
}

ResizablePane.defaultProps = {
    className: '',
}

export default ResizablePane
