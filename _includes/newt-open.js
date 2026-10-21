  // Newt buttons, shared by /converter/ and /ysbgn-js/: an SBGN-ML file opened in our copy of Newt
  // (/newt/, iVis-at-Bilkent/newt built as is), as if dropped on it. Newt opens a map only from a web
  // address, which these files lack; on our own site the page can hand it the file (user, 2026-10-20).
  // The cookie skips Newt's welcome tour. The file's name goes into the address (after #, which Newt
  // does not read) and the tab title, so a map can be named in feedback (user, 2026-10-20).
  const NEWT = '{{ "/newt/" | relative_url }}';

  const NEWT_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" ' +
                    'stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>' +
                    '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>';

  function openInNewt(text, name) {
    document.cookie = 'showIntro=false; path=' + NEWT + '; max-age=15552000; SameSite=Lax';
    const w = window.open(NEWT + '#' + encodeURIComponent(name), '_blank');
    if (!w) return;
    // handed over once Newt's file input has its handler, and again if the map has not arrived two
    // seconds later (Chrome showed an empty map now and then, user 2026-10-21), up to three times
    const started = Date.now();
    let tries = 0, last = 0;
    const wait = setInterval(() => {
      if (w.closed || Date.now() - started > 60000) { clearInterval(wait); return; }
      try {
        const input = w.$ && w.$('#file-input')[0];
        if (w.document.readyState !== 'complete' || !w.cy || !input || !(w.$._data(input, 'events') || {}).change) return;
        if (w.cy.elements().length) { clearInterval(wait); return; }
        if (Date.now() - last < 2000) return;
        if (tries++ === 3) { clearInterval(wait); return; }
        last = Date.now();
        w.document.title = name + ' · Newt';
        w.$(input).trigger('change', [new w.File([text], name, { type: 'text/plain' })]);
      } catch (e) { /* the new tab is still on about:blank */ }
    }, 200);
  }

  // a button in the Converter's two lines: "Open in Newt" (user, 2026-10-21; it was "Newt"), and under
  // it the variant, small; white with the blue edge (user, 2026-10-21; it was grey), the external-link
  // icon after it (the buttons made wider for it)
  function newtButton(text, name, variant) {
    const a = document.createElement('a');
    a.className = 'cv-btn cv-alt'; a.href = NEWT; a.title = 'Open ' + name + ' in Newt';
    const lines = document.createElement('span'); lines.className = 'cv-lines';
    lines.append('Open in Newt');
    for (const t of variant ? variant.split(', ') : []) {  // "plain, straight line": a line each
      const v = document.createElement('span'); v.className = 'cv-variant'; v.textContent = t; lines.append(v);
    }
    a.append(lines);
    a.insertAdjacentHTML('beforeend', NEWT_ICON);
    for (const ev of ['click', 'auxclick'])  // a middle click too, which would open an empty Newt
      a.addEventListener(ev, e => { if (e.button > 1) return; e.preventDefault(); openInNewt(text, name); });
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
