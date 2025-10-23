document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tab');
  const tabContents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active class from all tabs
      tabs.forEach(t => t.classList.remove('active'));

      // Hide all tab contents
      tabContents.forEach(content => content.classList.add('hidden'));

      // Add active class to clicked tab
      tab.classList.add('active');

      // Show the corresponding tab content
      const target = tab.getAttribute('data-tab');
      document.getElementById(target).classList.remove('hidden');
    });
  });
});