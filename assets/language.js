/* Language-specific URLs are authoritative. Only the English home checks a
   saved choice before paint, so direct article links remain shareable. */
const languageKey = 'byxiaoyu-language';
const current = document.documentElement.lang === 'zh-CN' ? 'zh' : 'en';
try {
  if (current === 'en' && location.pathname.startsWith('/zh/')) {
    // GitHub Pages serves the root 404.html for unknown /zh/ URLs.
    location.replace('/zh/404.html');
  } else if (location.pathname === '/' && localStorage.getItem(languageKey) === 'zh') {
    location.replace('/zh/' + location.search + location.hash);
  } else {
    localStorage.setItem(languageKey, current);
  }
} catch (_) { /* Language URLs still work without storage. */ }
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-language]').forEach((link) => {
    link.addEventListener('click', () => {
      try { localStorage.setItem(languageKey, link.dataset.language); } catch (_) { /* Optional. */ }
    });
  });
});
