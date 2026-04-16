import React, { useCallback, useLayoutEffect, useRef, useState, forwardRef, useImperativeHandle } from 'react';
import { gsap } from 'gsap';
import './StaggeredMenu.css';

const StaggeredMenu = forwardRef(({ items = [], onItemClick, accentColor = '#667eea' }, ref) => {
  const [open, setOpen] = useState(false);
  const panelRef = useRef(null);
  const preLayersRef = useRef(null);
  const plusHRef = useRef(null);
  const plusVRef = useRef(null);
  const iconRef = useRef(null);
  const textInnerRef = useRef(null);
  const toggleBtnRef = useRef(null);
  const particleContainerRef = useRef(null);
  const [textLines, setTextLines] = useState(['Menu', 'Close']);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      const panel = panelRef.current;
      const preContainer = preLayersRef.current;
      const plusH = plusHRef.current;
      const plusV = plusVRef.current;
      const icon = iconRef.current;
      const textInner = textInnerRef.current;
      if (!panel || !plusH || !plusV || !icon || !textInner) return;

      let preLayers = [];
      if (preContainer) {
        preLayers = Array.from(preContainer.querySelectorAll('.sm-prelayer'));
      }

      gsap.set([panel, ...preLayers], { xPercent: 100 });
      gsap.set(plusH, { transformOrigin: '50% 50%', rotate: 0 });
      gsap.set(plusV, { transformOrigin: '50% 50%', rotate: 90 });
      gsap.set(icon, { rotate: 0, transformOrigin: '50% 50%' });
      gsap.set(textInner, { yPercent: 0 });
    });
    return () => ctx.revert();
  }, []);

  const createParticles = useCallback(() => {
    const container = particleContainerRef.current;
    if (!container) return;

    for (let i = 0; i < 10; i++) {
      const particle = document.createElement('div');
      particle.className = 'menu-particle';
      const angle = (Math.random() * 360) * (Math.PI / 180);
      const distance = 60 + Math.random() * 40;
      const endX = Math.cos(angle) * distance;
      const endY = Math.sin(angle) * distance;
      const duration = 0.6 + Math.random() * 0.4;
      
      particle.style.cssText = `
        --end-x: ${endX}px;
        --end-y: ${endY}px;
        --duration: ${duration}s;
      `;
      
      container.appendChild(particle);
      setTimeout(() => container.removeChild(particle), duration * 1000);
    }
  }, []);

  const toggleMenu = useCallback(() => {
    const target = !open;
    setOpen(target);
    createParticles();

    const panel = panelRef.current;
    const icon = iconRef.current;
    const textInner = textInnerRef.current;

    if (target) {
      gsap.to(panel, { xPercent: 0, duration: 0.5, ease: 'power4.out' });
      gsap.to(icon, { rotate: 225, duration: 0.8, ease: 'power4.out' });
      gsap.to(textInner, { yPercent: -50, duration: 0.5, ease: 'power4.out' });
    } else {
      gsap.to(panel, { xPercent: 100, duration: 0.32, ease: 'power3.in' });
      gsap.to(icon, { rotate: 0, duration: 0.35, ease: 'power3.inOut' });
      gsap.to(textInner, { yPercent: 0, duration: 0.35, ease: 'power3.inOut' });
    }
  }, [open, createParticles]);

  useImperativeHandle(ref, () => ({
    toggle: toggleMenu
  }));

  const handleItemClick = (item) => {
    toggleMenu();
    if (onItemClick) {
      onItemClick(item);
    }
  };

  return (
    <div className="staggered-menu-wrapper" style={{ '--sm-accent': accentColor, opacity: open ? 1 : 0, pointerEvents: open ? 'auto' : 'none' }}>
      <div ref={preLayersRef} className="sm-prelayers" aria-hidden="true">
        <div className="sm-prelayer" style={{ background: 'rgba(255, 255, 255, 0.1)' }} />
        <div className="sm-prelayer" style={{ background: 'rgba(255, 255, 255, 0.05)' }} />
      </div>

      <header className="staggered-menu-header">
        <div ref={particleContainerRef} className="menu-particle-container" />
        <button
          ref={toggleBtnRef}
          className="sm-toggle"
          aria-label={open ? 'Close menu' : 'Open menu'}
          onClick={toggleMenu}
          type="button"
        >
          <span className="sm-toggle-textWrap" aria-hidden="true">
            <span ref={textInnerRef} className="sm-toggle-textInner">
              {textLines.map((l, i) => (
                <span className="sm-toggle-line" key={i}>
                  {l}
                </span>
              ))}
            </span>
          </span>
          <span ref={iconRef} className="sm-icon" aria-hidden="true">
            <span ref={plusHRef} className="sm-icon-line" />
            <span ref={plusVRef} className="sm-icon-line sm-icon-line-v" />
          </span>
        </button>
      </header>

      <aside ref={panelRef} className="staggered-menu-panel" aria-hidden={!open}>
        <div className="sm-panel-inner">
          <ul className="sm-panel-list" role="list">
            {items.map((it, idx) => (
              <li className="sm-panel-itemWrap" key={idx}>
                <a className="sm-panel-item" href="#" onClick={(e) => { e.preventDefault(); handleItemClick(it); }}>
                  <span className="sm-panel-itemLabel">{it.label}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </div>
  );
});

export default StaggeredMenu;
