/* A visual gate for the personal sections of this static site.
   The page HTML remains public; this is not access control for sensitive data. */
const gate = document.querySelector('#gate-screen');
const content = document.querySelector('#protected-content');
const input = document.querySelector('#private-password');
const button = document.querySelector('#unlock-button');
const error = document.querySelector('#gate-error');
const storageKey = 'byxiaoyu-personal-gate';
const expectedHash = gate.dataset.hash;
const zh = document.documentElement.lang === 'zh-CN';

function reveal(manual = false) {
  gate.hidden = true;
  content.hidden = false;
  document.querySelector('.skip-link').href = '#main';
  if (manual) {
    const heading = content.querySelector('h1');
    if (heading) {
      heading.tabIndex = -1;
      heading.focus();
    }
  }
}

try {
  if (sessionStorage.getItem(storageKey) === expectedHash) reveal();
} catch (_) {
  // The gate still works for the current page if session storage is unavailable.
}

async function unlock() {
  if (!input.value) {
    error.textContent = zh ? '请输入密码。' : 'Please enter the password.';
    input.focus();
    return;
  }
  if (!window.crypto || !crypto.subtle) {
    error.textContent = zh ? '当前浏览器无法验证密码。请使用支持 HTTPS 或本地预览的现代浏览器。' : 'This browser cannot check the password. Try a current browser over HTTPS or localhost.';
    return;
  }
  button.disabled = true;
  const bytes = new TextEncoder().encode(input.value);
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  const actualHash = Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, '0')).join('');
  button.disabled = false;
  if (actualHash !== expectedHash) {
    error.textContent = zh ? '密码不正确，请重试。' : 'That password did not match. Try again.';
    input.value = '';
    input.focus();
    return;
  }
  try { sessionStorage.setItem(storageKey, expectedHash); } catch (_) { /* Optional session memory. */ }
  input.value = '';
  error.textContent = '';
  reveal(true);
}

button.addEventListener('click', unlock);
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault();
    unlock();
  }
});
