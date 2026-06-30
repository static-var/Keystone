document.addEventListener('DOMContentLoaded', () => {
  // ── Theme toggle ──
  const themeToggle = document.querySelector('.theme-toggle');
  const themeQuery = window.matchMedia('(prefers-color-scheme: dark)');
  const storageKey = 'keystone-theme';

  const getSavedTheme = () => {
    try {
      return localStorage.getItem(storageKey);
    } catch {
      return null;
    }
  };

  const saveTheme = (theme) => {
    try {
      localStorage.setItem(storageKey, theme);
    } catch {
      // Theme still applies for the current page when storage is unavailable.
    }
  };

  const setTheme = (theme, persist = true) => {
    document.documentElement.dataset.theme = theme;
    if (persist) {
      saveTheme(theme);
    }
    if (themeToggle) {
      const isDark = theme === 'dark';
      themeToggle.setAttribute('aria-pressed', String(isDark));
      themeToggle.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} mode`);
    }
  };

  if (themeToggle) {
    setTheme(document.documentElement.dataset.theme || (themeQuery.matches ? 'dark' : 'light'), false);
    themeToggle.addEventListener('click', () => {
      setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
    });
  }

  themeQuery.addEventListener('change', (event) => {
    if (!getSavedTheme()) {
      setTheme(event.matches ? 'dark' : 'light', false);
    }
  });

  // ── Nav shadow on scroll ──
  const nav = document.getElementById('nav');
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle('scrolled', window.scrollY > 10);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ── Fade-in sections on scroll ──
  const sections = document.querySelectorAll('.section, .closing');
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  sections.forEach(s => s.classList.add('fade-in'));

  if (prefersReducedMotion || !('IntersectionObserver' in window)) {
    sections.forEach(s => s.classList.add('visible'));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
  );

  sections.forEach(s => observer.observe(s));
});
