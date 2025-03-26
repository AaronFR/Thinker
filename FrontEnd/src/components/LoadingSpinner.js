import React from 'react';
import './styles/LoadingSpinner.css';

const Circle = ({ size, color, offset = 0, children }) => {
  const style = {
    width: size,
    height: size,
    border: `10px solid ${color}`,
    borderRadius: '50%',
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: offset 
      ? `translate(-50%, -50%) translateX(-${offset}px)`
      : 'translate(-50%, -50%)',
    boxSizing: 'border-box',
  };

  return <div className="circle" style={style}>{children}</div>;
};

const Rotator = ({ speed, children }) => {
  const style = {
    animation: `rotate ${speed}s linear infinite`,
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
  };
  return <div className="rotator" style={style}>{children}</div>;
};

const LoadingSpinner = () => {
  const outer = { size: 200, speed: 15, color: 'grey' };
  const middle = { size: 100, speed: 10, color: 'grey' };
  const inner = { size: 50, speed: 5, color: 'grey' };

  // Compute the offset to position the child circle relative to its parent
  const computeOffset = (parentSize, childSize) => parentSize / 2 - childSize / 2;
  const offsetMiddle = computeOffset(outer.size, middle.size);
  const offsetInner = computeOffset(middle.size, inner.size);

  return (
    <div className="loading-spinner">
      <Circle size={outer.size} color={outer.color}>
        <Rotator speed={outer.speed}>
          <Circle size={middle.size} color={middle.color} offset={offsetMiddle}>
            <Rotator speed={middle.speed}>
              <Circle size={inner.size} color={inner.color} offset={offsetInner} />
            </Rotator>
          </Circle>
        </Rotator>
      </Circle>
    </div>
  );
};

export default LoadingSpinner;
