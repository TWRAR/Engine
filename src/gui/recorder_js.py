"""JS injected into every page/frame to capture clicks, form input, and
navigation-triggering key presses, and forward them to Python via the
`__record_event` binding. Best-effort CSS selector generation - selectors
are meant to be reviewed/edited in the step editor, not trusted blindly.
"""

RECORDER_JS = r"""
(function () {
  if (window.__stuxRecorderInstalled) return;
  window.__stuxRecorderInstalled = true;

  function cssPath(el) {
    if (!(el instanceof Element)) return null;
    if (el.id) return '#' + CSS.escape(el.id);

    const testAttrs = ['data-testid', 'data-test', 'data-qa', 'name', 'aria-label'];
    for (const attr of testAttrs) {
      const v = el.getAttribute(attr);
      if (v) return '[' + attr + '="' + CSS.escape(v) + '"]';
    }

    const path = [];
    let node = el;
    while (node && node.nodeType === Node.ELEMENT_NODE && node !== document.body) {
      let selector = node.tagName.toLowerCase();
      if (node.classList.length) {
        selector += '.' + Array.from(node.classList).slice(0, 2).map(function (c) {
          return CSS.escape(c);
        }).join('.');
      }
      const parent = node.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter(function (c) {
          return c.tagName === node.tagName;
        });
        if (siblings.length > 1) {
          selector += ':nth-of-type(' + (siblings.indexOf(node) + 1) + ')';
        }
      }
      path.unshift(selector);
      node = parent;
      if (path.length >= 4) break;
    }
    return path.join(' > ');
  }

  function send(type, detail) {
    if (window.__record_event) {
      window.__record_event(JSON.stringify(Object.assign({ type: type }, detail)));
    }
  }

  document.addEventListener('click', function (e) {
    const el = e.target;
    const modifiers = [];
    if (e.ctrlKey) modifiers.push('Control');
    if (e.shiftKey) modifiers.push('Shift');
    if (e.altKey) modifiers.push('Alt');
    if (e.metaKey) modifiers.push('Meta');
    send('click', { selector: cssPath(el), modifiers: modifiers });
  }, true);

  document.addEventListener('change', function (e) {
    const el = e.target;
    if (!el || !el.tagName) return;
    const tag = el.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') {
      const type = (el.getAttribute('type') || 'text').toLowerCase();
      if (type === 'checkbox' || type === 'radio') {
        send('check', { selector: cssPath(el), checked: el.checked });
      } else {
        send('fill', { selector: cssPath(el), value: el.value });
      }
    } else if (tag === 'SELECT') {
      send('select_option', { selector: cssPath(el), value: el.value });
    }
  }, true);

  document.addEventListener('keydown', function (e) {
    const controlKeys = ['Enter', 'Tab', 'Escape'];
    if (controlKeys.indexOf(e.key) !== -1) {
      send('press', { selector: cssPath(e.target), keys: e.key });
    }
  }, true);
})();
"""
