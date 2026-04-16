import React from 'react';
import './AnimatedText.css';

const AnimatedText = ({ text, className = '', style = {} }) => {
  return (
    <h1 
      className={`animated-text ${className}`} 
      style={{
        ...style,
        display: 'inline-block'
      }}
    >
      {text.split('').map((char, index) => (
        <span
          key={index}
          className="animated-char"
          style={{
            animationDelay: `${index * 0.05}s`,
            display: 'inline-block'
          }}
        >
          {char === ' ' ? '\u00A0' : char}
        </span>
      ))}
    </h1>
  );
};

export default AnimatedText;
