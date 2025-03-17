import { useState, useCallback, useLayoutEffect, useRef } from 'react';

/**
 * Calculates the number of items that can fit in a row based on the container width and item width.
 * @param {React.RefObject<HTMLElement>} containerRef - A ref to the container element.
 * @param {string} itemSelector - CSS selector for the items within the container.
 * @param {function} setItemsPerRow - Setter function to update the itemsPerRow state.
 */
export const calculateItemsPerRow = (containerRef, itemSelector, setItemsPerRow) => {
  if (!containerRef.current) return;

  const containerWidth = containerRef.current.offsetWidth;
  const firstItem = containerRef.current.querySelector(itemSelector);

  if (!firstItem) return;

  const itemWidth = firstItem.offsetWidth;
  const computedItemsPerRow = Math.floor(containerWidth / itemWidth) || 1;
  setItemsPerRow(computedItemsPerRow);
};


/**
 * A custom hook that calculates and updates the number of items per row in a container.
 * @param {React.RefObject<HTMLElement>} containerRef - A ref to the container element.
 * @param {string} itemSelector - CSS selector for the items within the container.
 * @returns {[number]} - The number of items per row.
 */
export const useCalculateItemsPerRow = (containerRef, itemSelector) => {
  const [itemsPerRow, setItemsPerRow] = useState(0);

  const memoizedCalculateItemsPerRow = useCallback(() => {
    calculateItemsPerRow(containerRef, itemSelector, setItemsPerRow);
  }, [containerRef, itemSelector, setItemsPerRow]);

  useLayoutEffect(() => {
    memoizedCalculateItemsPerRow();

    let resizeObserver;
    if (containerRef.current) {
      resizeObserver = new ResizeObserver(() => {
        memoizedCalculateItemsPerRow();
      });
      resizeObserver.observe(containerRef.current);
    }

    return () => {
      if (resizeObserver && containerRef.current) {
        resizeObserver.unobserve(containerRef.current);
        resizeObserver.disconnect();
      }
    };
  }, [memoizedCalculateItemsPerRow, containerRef, itemSelector]);

  return [itemsPerRow];
};
