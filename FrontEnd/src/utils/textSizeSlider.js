import React, { useContext } from 'react';
import { SettingsContext } from '../pages/Settings/SettingsContext';

import './styles/TextSizeSlider.css';

/**
 * TextSizeSlider Component
 *
 * Allows users to adjust the text size of the application.
 *
 * Utilizes SettingsContext to access and modify font size settings.
 */
const TextSizeSlider = () => {
    const { fontSize, setFontSize } = useContext(SettingsContext);

    const MIN_FONT_SIZE = 12;
    const MAX_FONT_SIZE = 24;
    const FONT_SIZE_STORAGE_KEY = 'fontSize'

    /**
     * Handle slider change event
     *
     * @param {Object} event - The change event from the slider input.
     */
    const handleChange = (event) => {
        const newSize = Math.max(MIN_FONT_SIZE, Math.min(MAX_FONT_SIZE, event.target.value));
        setFontSize(newSize);
        document.documentElement.style.fontSize = `${newSize}px`;

        localStorage.setItem(FONT_SIZE_STORAGE_KEY, newSize);
    };

    /**
     * Handles keyboard interactions for the slider.
     *
     * :param {Object} event: The keyboard event.
     */
    const handleKeyDown = (event) => {
        let newSize = fontSize
        if (event.key === 'ArrowUp' && fontSize < MAX_FONT_SIZE) {
            newSize += 1
        } else if (event.key === 'ArrowDown' && fontSize > MIN_FONT_SIZE) {
            newSize -= 1
        }
        if (newSize !== fontSize) {
            setFontSize(newSize)
            document.documentElement.style.fontSize = `${newSize}px`
            localStorage.setItem(FONT_SIZE_STORAGE_KEY, newSize)
            event.preventDefault()
        }
    }
    
    return (
        <div className="text-size-slider-container">
            <label htmlFor="fontSizeSlider" className="text-size-slider-label">
                Text Size:
            </label>
            <input
                id="fontSizeSlider"
                className='slider'
                type="range"
                min={MIN_FONT_SIZE}
                max={MAX_FONT_SIZE}
                value={fontSize}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                aria-label="Text Size Slider"
            />
            <span className='size-display'>{`${fontSize}px`}</span>
        </div>
    );
};

export default TextSizeSlider;
