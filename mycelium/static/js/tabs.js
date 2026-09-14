document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tab');
  const tabContents = document.querySelectorAll('.tab-content');

  function activateTab(tab, updateUrl = true) {
    if (!tab) return;
    const target = tab.getAttribute('data-tab');
    if (!target) return;
    const contentEl = document.getElementById(target);

    const container = tab.closest('.tabs-container') || tab.closest('ul')?.parentElement || document;
    container.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

    tabContents.forEach(content => content.classList.add('hidden'));

    tab.classList.add('active');
    if (contentEl) {
      contentEl.classList.remove('hidden');
    }

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
      let activeTabInput = form.querySelector('input[name="active_tab"]');
      if (!activeTabInput) {
        activeTabInput = document.createElement('input');
        activeTabInput.type = 'hidden';
        activeTabInput.name = 'active_tab';
        form.appendChild(activeTabInput);
      }
      activeTabInput.value = target;
    });

    const editLinks = document.querySelectorAll('a[href*="/edit/"]');
    editLinks.forEach(link => {
      try {
        const linkUrl = new URL(link.href, window.location.origin);
        linkUrl.searchParams.set('tab', target);
        link.href = linkUrl.pathname + linkUrl.search + linkUrl.hash;
      } catch (e) {}
    });

    if (updateUrl && window.history && window.history.replaceState) {
      const url = new URL(window.location);
      url.searchParams.set('tab', target);
      window.history.replaceState({}, '', url);
    }
  }

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      activateTab(tab, true);
    });
  });

  const urlParams = new URLSearchParams(window.location.search);
  const tabParam = urlParams.get('tab');
  const activeTabInput = document.querySelector('input[name="active_tab"]');
  const initialTabTarget = tabParam || (activeTabInput ? activeTabInput.value : '');

  if (initialTabTarget) {
    const targetTab = Array.from(tabs).find(t => t.getAttribute('data-tab') === initialTabTarget);
    if (targetTab) {
      activateTab(targetTab, false);
    }
  }
});