// Reading and installation stay usable without JavaScript.
for (const button of document.querySelectorAll('[data-copy]')) {
  button.addEventListener('click', async () => {
    const code = button.parentElement.querySelector('code');
    const english = document.documentElement.lang === 'en';
    try {
      await navigator.clipboard.writeText(code.textContent.trim());
      button.textContent = english ? 'Copied' : '已复制';
      setTimeout(() => { button.textContent = english ? 'Copy' : '复制'; }, 1800);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = english ? 'Select & copy' : '请复制选中文本';
    }
  });
}
