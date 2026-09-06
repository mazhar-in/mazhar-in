/**
 * MAZHAR.IN - Core Interactive Scripts
 * Handles Dark/Light theme switching, navigation, and UX polish
 */

(function () {
  'use strict';

  // --- Theme Management ---
  const STORAGE_KEY = 'mazhar_theme';
  const html = document.documentElement;

  function getPreferredTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    updateThemeToggleIcons(theme);
  }

  function updateThemeToggleIcons(theme) {
    const toggleBtns = document.querySelectorAll('.theme-toggle-btn');
    toggleBtns.forEach(btn => {
      btn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
      btn.innerHTML = theme === 'dark'
        ? `<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>`
        : `<svg viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>`;
    });
  }

  // Initialize Theme immediately to prevent flash
  const initialTheme = getPreferredTheme();
  setTheme(initialTheme);

  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      setTheme(e.matches ? 'dark' : 'light');
    }
  });

  // DOM Loaded Listeners
  document.addEventListener('DOMContentLoaded', () => {
    // Re-verify icons once DOM elements exist
    updateThemeToggleIcons(html.getAttribute('data-theme') || 'dark');

    // Theme toggle click handler
    document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme') || 'dark';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
      });
    });

    // Mobile Navigation Toggle
    const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const hamburgerIcon = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>';
    const closeIcon = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';

    if (mobileNavToggle && navMenu) {
      function closeNav() {
        navMenu.classList.remove('open');
        mobileNavToggle.setAttribute('aria-expanded', 'false');
        mobileNavToggle.innerHTML = hamburgerIcon;
      }

      mobileNavToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = navMenu.classList.toggle('open');
        mobileNavToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        mobileNavToggle.innerHTML = isOpen ? closeIcon : hamburgerIcon;
      });

      // Close mobile menu when clicking outside
      document.addEventListener('click', (e) => {
        if (!navMenu.contains(e.target) && !mobileNavToggle.contains(e.target)) {
          closeNav();
        }
      });

      // Close mobile menu when clicking any nav link
      navMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
          closeNav();
        });
      });
    }

    // Copy Code Block Handler
    document.querySelectorAll('pre code').forEach(codeBlock => {
      const pre = codeBlock.parentNode;
      if (!pre) return;
      
      const copyBtn = document.createElement('button');
      copyBtn.className = 'copy-code-btn';
      copyBtn.innerText = 'Copy';
      copyBtn.setAttribute('aria-label', 'Copy code snippet');
      copyBtn.style.cssText = `
        position: absolute;
        top: 0.6rem;
        right: 0.6rem;
        font-family: var(--font-mono);
        font-size: 0.7rem;
        background: var(--bg-primary);
        color: var(--text-muted);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        padding: 0.2rem 0.5rem;
        cursor: pointer;
        opacity: 0.8;
        transition: all var(--transition-fast);
      `;
      
      pre.style.position = 'relative';
      pre.appendChild(copyBtn);

      copyBtn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(codeBlock.innerText);
          copyBtn.innerText = 'Copied!';
          copyBtn.style.color = 'var(--accent-emerald)';
          setTimeout(() => {
            copyBtn.innerText = 'Copy';
            copyBtn.style.color = 'var(--text-muted)';
          }, 2000);
        } catch (err) {
          console.error('Failed to copy', err);
        }
      });
    });
  });
})();
