import React, { useState, useEffect } from 'react';
import { Tooltip } from 'react-tooltip';

//Hook to detect touch/no-hover devices
function useIsTouchDevice() {
  const [isTouch, setIsTouch] = useState(false);

  useEffect(() => {
    const mql = window.matchMedia('(hover: none), (pointer: coarse)');
    setIsTouch(mql.matches);
    const onChange = e => setIsTouch(e.matches);
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, []);

  return isTouch;
}

// Mobile‐friendly Tooltip wrapper
export default function MobileFriendlyTooltip({
  id,
  place = 'top',
  effect = 'solid',
  hideAfter = 5000,   // auto-hide timeout on touch
  ...restProps
}) {
  const isTouch = useIsTouchDevice();

  // Base props always applied
  const props = {
    id,
    place,
    effect,
    clickable: true,   // allow tapping inside if you render a close button
    scrollHide: true,  // hide on scroll
    ...restProps,
  };

  if (isTouch) {
    // Touch-specific behavior
    Object.assign(props, {
      event: 'click',
      eventOff: 'click',
      globalEventOff: 'click',
      hideAfter,
      delayShow: 0,
      delayHide: 0,
    });
  } else {
    // Desktop hover/focus behavior
    Object.assign(props, {
      event: 'mouseenter focus',
      eventOff: 'mouseleave blur',
      delayShow: 100,
      delayHide: 10,
    });
  }

  return <Tooltip {...props} />;
}
