// Dark mode toggle functionality
document.addEventListener('DOMContentLoaded', function() {
  // Create the toggle button element
  const themeToggle = document.createElement('div');
  themeToggle.className = 'theme-toggle';
  themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
  themeToggle.setAttribute('role', 'button');
  themeToggle.setAttribute('aria-label', 'Toggle dark mode');
  themeToggle.setAttribute('tabindex', '0');
  document.body.appendChild(themeToggle);

  // Add tooltip for better UX
  themeToggle.title = 'Switch to dark mode';

  // Check for saved theme preference or use preferred color scheme
  const savedTheme = localStorage.getItem('theme');
  const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');

  // Apply theme based on saved preference or system preference
  if (savedTheme === 'dark' || (savedTheme === null && prefersDarkScheme.matches)) {
    document.body.classList.add('dark-mode');
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    themeToggle.title = 'Switch to light mode';
  }

  // Toggle between light and dark mode
  themeToggle.addEventListener('click', function() {
    // Add transition class for smoother theme switching
    document.body.classList.add('theme-transition');
    document.body.classList.toggle('dark-mode');

    const isDarkMode = document.body.classList.contains('dark-mode');

    // Update the icon and title
    if (isDarkMode) {
      themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
      themeToggle.title = 'Switch to light mode';
      localStorage.setItem('theme', 'dark');
    } else {
      themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
      themeToggle.title = 'Switch to dark mode';
      localStorage.setItem('theme', 'light');
    }

    // Announce theme change for screen readers
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.className = 'sr-only';
    announcement.textContent = `Theme changed to ${isDarkMode ? 'dark' : 'light'} mode`;
    document.body.appendChild(announcement);

    // Remove the announcement and transition class after they've served their purpose
    setTimeout(() => {
      document.body.removeChild(announcement);
      document.body.classList.remove('theme-transition');
    }, 1000);

    // Add a subtle animation effect to the toggle button
    themeToggle.classList.add('theme-toggle-active');
    setTimeout(() => {
      themeToggle.classList.remove('theme-toggle-active');
    }, 500);
  });

  // Add keyboard shortcuts for toggle (Shift + D)
  document.addEventListener('keydown', function(e) {
    if (e.shiftKey && (e.key === 'D' || e.key === 'd')) {
      themeToggle.click();

      // Visual feedback for keyboard shortcut
      themeToggle.classList.add('keyboard-activated');
      setTimeout(() => {
        themeToggle.classList.remove('keyboard-activated');
      }, 300);
    }
  });

  // Listen for system preference changes
  prefersDarkScheme.addEventListener('change', function(e) {
    if (localStorage.getItem('theme') === null) {
      if (e.matches) {
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        themeToggle.title = 'Switch to light mode';
      } else {
        document.body.classList.remove('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        themeToggle.title = 'Switch to dark mode';
      }
    }
  });

  // Create back to top button
  const backToTopButton = document.createElement('a');
  backToTopButton.href = '#';
  backToTopButton.id = 'backToTop';
  backToTopButton.className = 'back-to-top';
  backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
  backToTopButton.setAttribute('aria-label', 'Back to top');
  document.body.appendChild(backToTopButton);

  // Show/hide back to top button based on scroll position
  window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
      backToTopButton.classList.add('visible');
    } else {
      backToTopButton.classList.remove('visible');
    }
  });

  // Smooth scroll to top when button is clicked
  backToTopButton.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // Add interactive behavior to FAQ questions
  const faqQuestions = document.querySelectorAll('#faq h4');

  faqQuestions.forEach(question => {
    question.addEventListener('click', function() {
      // Toggle visual emphasis on the active question
      const isActive = this.classList.contains('active-question');

      // Reset all questions
      faqQuestions.forEach(q => q.classList.remove('active-question'));

      // Toggle this question if it wasn't active before
      if (!isActive) {
        this.classList.add('active-question');
      }
    });
  });

  // Add styles for interactive elements
  const style = document.createElement('style');
  style.textContent = `
    .theme-transition {
      transition: background-color 0.5s ease, color 0.5s ease;
    }
    
    .theme-toggle-active {
      animation: pulse 0.5s ease;
    }
    
    .keyboard-activated {
      animation: flash 0.3s ease;
    }
    
    .active-question {
      border-left: 3px solid var(--secondary-color);
      padding-left: 1em;
      font-weight: 700;
    }
    
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.2); }
      100% { transform: scale(1); }
    }
    
    @keyframes flash {
      0% { background-color: var(--secondary-color); }
      100% { background-color: var(--card-bg); }
    }
  `;
  document.head.appendChild(style);
});