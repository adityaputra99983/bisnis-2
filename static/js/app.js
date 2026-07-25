(function () {
  'use strict';

  /* ─── SPLASH SCREEN IS NOW PURE CSS ─── */

  /* ─── HEADER SCROLL EFFECT ─── */
  const header = document.getElementById('main-header') || document.querySelector('.header');
  let lastScroll = 0;
  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    if (scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    lastScroll = scrollY;
  }, { passive: true });

  /* ─── MOBILE NAV ─── */
  const mobileNavItems = document.querySelectorAll('.mobile-nav-item');
  mobileNavItems.forEach(item => {
    item.addEventListener('click', () => {
      mobileNavItems.forEach(i => i.classList.remove('active'));
      item.classList.add('active');
    });
  });

  /* ─── SCROLL REVEAL with stagger ─── */
  const reveals = document.querySelectorAll('[data-reveal]');
  const revealObs = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        const delay = e.target.dataset.delay || 0;
        setTimeout(() => {
          e.target.classList.add('revealed');
        }, parseInt(delay));
        revealObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.05, rootMargin: '0px 0px -30px 00px' });
  reveals.forEach((el, i) => {
    el.style.transitionDelay = (i % 4) * 0.08 + 's';
    revealObs.observe(el);
  });

  /* ─── STAGGER CHILDREN on reveal ─── */
  document.querySelectorAll('[data-stagger]').forEach(parent => {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const children = entry.target.children;
          Array.from(children).forEach((child, i) => {
            child.style.opacity = '0';
            child.style.transform = 'translateY(16px)';
            child.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            child.style.transitionDelay = (i * 0.08) + 's';
            requestAnimationFrame(() => {
              child.style.opacity = '1';
              child.style.transform = 'translateY(0)';
            });
          });
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    obs.observe(parent);
  });

  /* ─── SEARCH FUNCTIONALITY ─── */
  const searchInput = document.querySelector('.search-input');
  if (searchInput) {
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const form = searchInput.closest('form');
        if (form) {
          form.submit();
        } else {
          const q = searchInput.value.trim();
          if (q) window.location.href = '/healers/?q=' + encodeURIComponent(q);
        }
      }
    });
  }

  /* ─── HEART/FAVORITE TOGGLE with bounce ─── */
  document.querySelectorAll('.healer-fav-btn, .center-fav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const icon = btn.querySelector('i');
      if (icon.classList.contains('far')) {
        icon.classList.replace('far', 'fas');
        icon.style.color = '#ef4444';
        btn.style.transform = 'scale(1.2)';
        setTimeout(() => { btn.style.transform = 'scale(1)'; }, 200);
      } else {
        icon.classList.replace('fas', 'far');
        icon.style.color = '';
      }
    });
  });

  /* ─── SMOOTH PAGE TRANSITION ─── */
  /* Removed: was causing full body opacity fade on every click = constant repaints */

  /* ─── COUNTER ANIMATION ─── */
  const counters = document.querySelectorAll('.stat-number[data-count]');
  const countObs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const text = el.textContent.trim();
        const num = parseInt(text.replace(/[^0-9]/g, ''));
        if (isNaN(num) || num === 0) return;
        const prefix = text.match(/^[^\d]*/)[0];
        const suffix = text.match(/[^\d]*$/)[0];
        const duration = 1200;
        const start = performance.now();
        function update(now) {
          const p = Math.min((now - start) / duration, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          el.textContent = prefix + Math.floor(num * eased).toLocaleString() + suffix;
          if (p < 1) requestAnimationFrame(update);
          else el.textContent = prefix + num.toLocaleString() + suffix;
        }
        requestAnimationFrame(update);
        countObs.unobserve(el);
      }
    });
  }, { threshold: 0.5 });
  counters.forEach(c => countObs.observe(c));

  /* ─── PARALLAX on hero (throttled with rAF) ─── */
  const heroContent = document.querySelector('.hero-content');
  const heroImg = document.querySelector('.hero-video-wrap img');
  if (heroContent && heroImg) {
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        const scrollY = window.scrollY;
        if (scrollY < window.innerHeight) {
          heroContent.style.transform = `translateY(${scrollY * 0.15}px)`;
          heroContent.style.opacity = 1 - (scrollY / (window.innerHeight * 0.8));
          heroImg.style.transform = `translateY(${scrollY * 0.08}px) scale(${1 + scrollY * 0.0002})`;
        }
        ticking = false;
      });
    }, { passive: true });
  }

  /* ─── MAGNETIC BUTTONS (throttled with rAF) ─── */
  document.querySelectorAll('.btn-gold, .btn-cta-primary, .btn-book').forEach(btn => {
    let ticking = false;
    let mx = 0, my = 0;
    btn.addEventListener('mousemove', (e) => {
      if (ticking) return;
      const rect = btn.getBoundingClientRect();
      mx = e.clientX - rect.left - rect.width / 2;
      my = e.clientY - rect.top - rect.height / 2;
      ticking = true;
      requestAnimationFrame(() => {
        btn.style.transform = `translate(${mx * 0.15}px, ${my * 0.15}px)`;
        ticking = false;
      });
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0, 0)';
      btn.style.transition = 'transform 0.3s ease';
    });
    btn.addEventListener('mouseenter', () => {
      btn.style.transition = 'transform 0.1s ease';
    });
  });

  /* ─── CARD TILT EFFECT (throttled with rAF) ─── */
  document.querySelectorAll('.healer-card, .center-card, .review-card').forEach(card => {
    let ticking = false;
    let pendingX = 0, pendingY = 0;
    card.addEventListener('mousemove', (e) => {
      if (ticking) return;
      const rect = card.getBoundingClientRect();
      pendingX = (e.clientX - rect.left) / rect.width;
      pendingY = (e.clientY - rect.top) / rect.height;
      ticking = true;
      requestAnimationFrame(() => {
        const rotateX = (pendingY - 0.5) * -4;
        const rotateY = (pendingX - 0.5) * 4;
        card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        ticking = false;
      });
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(800px) rotateX(0) rotateY(0) translateY(0)';
      card.style.transition = 'transform 0.4s ease';
    });
    card.addEventListener('mouseenter', () => {
      card.style.transition = 'transform 0.1s ease';
    });
  });

  /* ─── RIPPLE EFFECT on buttons ─── */
  document.querySelectorAll('.btn-gold, .btn-cta-primary').forEach(btn => {
    btn.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      ripple.style.cssText = `
        position:absolute;width:${size}px;height:${size}px;
        left:${e.clientX - rect.left - size/2}px;top:${e.clientY - rect.top - size/2}px;
        background:rgba(255,255,255,0.2);border-radius:50%;
        transform:scale(0);animation:ripple 0.6s ease-out;
        pointer-events:none;
      `;
      this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });

  /* ─── TYPING EFFECT on hero subtitle ─── */
  const heroSubtitle = document.querySelector('.hero-subtitle');
  if (heroSubtitle) {
    const originalText = heroSubtitle.textContent;
    heroSubtitle.textContent = '';
    heroSubtitle.style.opacity = '1';
    let i = 0;
    function typeChar() {
      if (i < originalText.length) {
        heroSubtitle.textContent += originalText.charAt(i);
        i++;
        setTimeout(typeChar, 18 + Math.random() * 12);
      }
    }
    setTimeout(typeChar, 1200);
  }

  /* ─── SECTION LABELS animate in ─── */
  document.querySelectorAll('.section-label').forEach(label => {
    label.style.opacity = '0';
    label.style.transform = 'translateX(-10px)';
    const obs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            label.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            label.style.opacity = '1';
            label.style.transform = 'translateX(0)';
          }, 200);
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    obs.observe(label);
  });

  /* ─── SCROLL PROGRESS BAR ─── */
  const progressBar = document.createElement('div');
  progressBar.style.cssText = `
    position:fixed;top:0;left:0;height:1px;z-index:100;
    background:linear-gradient(90deg,var(--gold-dark),var(--gold),var(--gold-light));
    width:0;transition:width 0.1s;pointer-events:none;
  `;
  document.body.appendChild(progressBar);
  window.addEventListener('scroll', () => {
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (window.scrollY / scrollHeight) * 100;
    progressBar.style.width = progress + '%';
  }, { passive: true });

  /* ─── SMOOTH ANCHOR SCROLL ─── */
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ─── RIPPLE KEYFRAME ─── */
  const style = document.createElement('style');
  style.textContent = `@keyframes ripple { to { transform: scale(4); opacity: 0; } }`;
  document.head.appendChild(style);

})();
