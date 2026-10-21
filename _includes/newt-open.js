  // Newt buttons, shared by /converter/ and /ysbgn-js/: an SBGN-ML file opened in our copy of Newt
  // (/newt/, iVis-at-Bilkent/newt built as is), as if dropped on it. Newt opens a map only from a web
  // address, which these files lack; on our own site the page can hand it the file (user, 2026-10-20).
  // The cookie skips Newt's welcome tour. The file's name goes into the address (after #, which Newt
  // does not read) and the tab title, so a map can be named in feedback (user, 2026-10-20).
  const NEWT = '{{ "/newt/" | relative_url }}';

  function openInNewt(text, name) {
    document.cookie = 'showIntro=false; path=' + NEWT + '; max-age=15552000; SameSite=Lax';
    const w = window.open(NEWT + '#' + encodeURIComponent(name), '_blank');
    if (!w) return;
    const started = Date.now();
    const wait = setInterval(() => {
      if (w.closed || Date.now() - started > 60000) { clearInterval(wait); return; }
      try {
        if (w.document.readyState !== 'complete' || !w.cy || !w.$ || !w.$('#file-input').length) return;
        clearInterval(wait);
        w.document.title = name + ' · Newt';
        setTimeout(() => w.$('#file-input').trigger('change', [new w.File([text], name, { type: 'text/plain' })]), 300);
      } catch (e) { /* the new tab is still on about:blank */ }
    }, 200);
  }

  // a button in the Converter's two lines: "Open in Newt" (user, 2026-10-21; it was "Newt"), and under
  // it the variant, small; white with the blue edge (user, 2026-10-21; it was grey), no external-link
  // icon (our own copy, and "Open in Newt" fills the button)
  function newtButton(text, name, variant) {
    const a = document.createElement('a');
    a.className = 'cv-btn cv-alt'; a.href = NEWT; a.title = 'Open ' + name + ' in Newt';
    const lines = document.createElement('span'); lines.className = 'cv-lines';
    lines.append('Open in Newt');
    if (variant) { const v = document.createElement('span'); v.className = 'cv-variant'; v.textContent = variant; lines.append(v); }
    a.append(lines);
    a.addEventListener('click', e => { e.preventDefault(); openInNewt(text, name); });
    return a;
  }

  // a map's Newt buttons ({text, name, variant}), after its SBGN-ML buttons, else after its others
  function addNewtButtons(box, files) {
    let at = [...box.querySelectorAll('a.cv-btn')].filter(b => b.download.endsWith('.sbgn')).pop();
    for (const f of files) {
      const b = newtButton(f.text, f.name, f.variant);
      if (at) at.after(b); else box.append(b);
      at = b;
    }
  }
