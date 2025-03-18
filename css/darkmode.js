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

  // Check for saved theme preference or use preferred color scheme
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark' || (savedTheme === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.body.classList.add('dark-mode');
    themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
  }

  // Toggle between light and dark mode
  themeToggle.addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');

    // Update the icon
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

    // Remove the announcement after it's been read
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  });

  // Add keyboard shortcut for toggle (Shift + D)
  document.addEventListener('keydown', function(e) {
    if (e.shiftKey && e.key === 'D') {
      themeToggle.click();
    }
  });

  // Back to top button
  const backToTopButton = document.createElement('a');
  backToTopButton.href = '#';
  backToTopButton.id = 'backToTop';
  backToTopButton.className = 'back-to-top';
  backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
  backToTopButton.setAttribute('aria-label', 'Back to top');
  document.body.appendChild(backToTopButton);

  window.addEventListener('scroll', function() {
    if (window.pageYOffset > 300) {
      backToTopButton.classList.add('visible');
    } else {
      backToTopButton.classList.remove('visible');
    }
  });

  backToTopButton.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
});