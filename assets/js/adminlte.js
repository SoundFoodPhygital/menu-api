/* AdminLTE-style JavaScript for Flask-Admin */

/**
 * Toggle sidebar visibility
 * On desktop: collapses to mini sidebar
 * On mobile: slides sidebar in/out
 */
function toggleSidebar() {
  const body = document.body;
  const sidebar = document.getElementById('main-sidebar');

  if (window.innerWidth > 991) {
    body.classList.toggle('sidebar-collapse');
  } else {
    sidebar.classList.toggle('sidebar-open');
  }
}

/**
 * Toggle treeview menu (submenu expansion)
 * @param {HTMLElement} element - The clicked nav-link element
 * @param {Event} event - The click event
 */
function toggleTreeview(element, event) {
  event.preventDefault();
  const parent = element.parentElement;
  parent.classList.toggle('menu-open');
}

/**
 * Handle window resize events
 * Removes mobile sidebar state when resizing to desktop
 */
function handleResize() {
  const sidebar = document.getElementById('main-sidebar');
  if (window.innerWidth > 991) {
    sidebar.classList.remove('sidebar-open');
  }
}

// Initialize event listeners when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Handle window resize
  window.addEventListener('resize', handleResize);

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('main-sidebar');
    const sidebarToggle = document.querySelector('.sidebar-toggle');

    if (window.innerWidth <= 991 &&
        sidebar.classList.contains('sidebar-open') &&
        !sidebar.contains(event.target) &&
        !sidebarToggle.contains(event.target)) {
      sidebar.classList.remove('sidebar-open');
    }
  });
});
