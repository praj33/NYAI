import React from 'react';
import './SkeletonLoader.css';

const SkeletonLoader = ({ type = 'text', count = 1, gridColumns = 1 }) => {
  const skeletonStyle = {
    backgroundColor: '#e9ecef',
    borderRadius: '4px',
    marginBottom: '10px',
    position: 'relative',
    overflow: 'hidden'
  };

  const shimmerStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent)',
    animation: 'shimmer 1.5s infinite'
  };

  const getSkeletonContent = () => {
    switch (type) {
      case 'image':
        return (
          <div style={{ ...skeletonStyle, height: '200px' }}>
            <div style={shimmerStyle} />
          </div>
        );
      case 'card':
        return (
          <div style={{ ...skeletonStyle, padding: '15px' }}>
            <div style={{ ...skeletonStyle, height: '20px', marginBottom: '10px' }}>
              <div style={shimmerStyle} />
            </div>
            <div style={{ ...skeletonStyle, height: '15px', width: '80%', marginBottom: '5px' }}>
              <div style={shimmerStyle} />
            </div>
            <div style={{ ...skeletonStyle, height: '15px', width: '60%', marginBottom: 0 }}>
              <div style={shimmerStyle} />
            </div>
          </div>
        );
      case 'text':
      default:
        return (
          <div style={{ ...skeletonStyle, height: '20px' }}>
            <div style={shimmerStyle} />
          </div>
        );
    }
  };

  const renderSkeletons = () => {
    return Array.from({ length: count }, (_, i) => (
      <div key={i} style={{ marginBottom: '15px' }}>
        {getSkeletonContent()}
      </div>
    ));
  };

  return (
    <div 
      style={{ 
        display: 'grid', 
        gridTemplateColumns: `repeat(${gridColumns}, 1fr)`, 
        gap: '20px',
        width: '100%'
      }}
      role="status"
      aria-busy="true"
    >
      <span className="visually-hidden">Loading content...</span>
      {renderSkeletons()}
    </div>
  );
};

export default SkeletonLoader;