import { useRef, useCallback } from 'react';

export const useGooeyAnimation = (particleCount = 10, color = '#667eea') => {
  const containerRef = useRef(null);

  const triggerAnimation = useCallback((e) => {
    const container = containerRef.current;
    if (!container) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.className = 'gooey-particle';
      const angle = (Math.random() * 360) * (Math.PI / 180);
      const distance = 60 + Math.random() * 40;
      const endX = Math.cos(angle) * distance;
      const endY = Math.sin(angle) * distance;
      const duration = 0.6 + Math.random() * 0.4;
      
      particle.style.cssText = `
        position: absolute;
        left: ${centerX}px;
        top: ${centerY}px;
        width: 8px;
        height: 8px;
        background: ${color};
        border-radius: 50%;
        pointer-events: none;
        opacity: 0.8;
        filter: blur(1px);
        animation: particle-burst ${duration}s ease-out forwards;
        --end-x: ${endX}px;
        --end-y: ${endY}px;
      `;
      
      container.appendChild(particle);
      setTimeout(() => {
        if (container.contains(particle)) {
          container.removeChild(particle);
        }
      }, duration * 1000);
    }
  }, [particleCount, color]);

  return { containerRef, triggerAnimation };
};
