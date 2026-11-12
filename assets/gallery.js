const filters = document.querySelectorAll('[data-filter]');
const cards = document.querySelectorAll('.photo-card');
const dialog = document.querySelector('#photo-dialog');

filters.forEach((button) => button.addEventListener('click', () => {
  const selected = button.dataset.filter;
  filters.forEach((item) => {
    const active = item === button;
    item.classList.toggle('is-active', active);
    item.setAttribute('aria-pressed', String(active));
  });
  cards.forEach((card) => { card.hidden = selected !== 'all' && card.dataset.category !== selected; });
}));

document.querySelectorAll('.photo-open').forEach((button) => button.addEventListener('click', () => {
  const image = dialog.querySelector('img');
  image.src = button.dataset.src;
  image.alt = button.dataset.alt;
  const caption = button.dataset.caption;
  const placeholder = document.documentElement.lang === 'zh-CN' ? '插画占位图' : 'illustration placeholder';
  const label = button.dataset.placeholder === 'true' ? [caption, placeholder].filter(Boolean).join(' · ') : caption;
  const note = dialog.querySelector('p');
  note.textContent = label;
  note.hidden = !label;
  dialog.showModal();
}));

dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });
