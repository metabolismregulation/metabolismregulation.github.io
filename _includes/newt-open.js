  // Newt buttons, shared by /converter/ and /ysbgn-js/: an SBGN-ML file opened in our copy of Newt
  // (/newt/, iVis-at-Bilkent/newt built as is with one script of ours, open.js), as if dropped on it.
  // Newt opens a map only from a web address, which these files lack (user, 2026-10-20). Each button is a
  // link to /newt/?f=<key>#<file name>, so a click, a middle click and "Open link in new tab" all work
  // (user, 2026-10-21): Newt's open.js asks this page for the file <key> over a BroadcastChannel, inside
  // the browser, and this page answers while it is open. The file's name is in the address (after #,
  // which Newt does not read) and the tab title, so a map can be named in feedback (user, 2026-10-20).
  const NEWT = '{{ "/newt/" | relative_url }}';
  const RUN = Math.random().toString(36).slice(2, 8);  // this page load's files, apart from another tab's
  const NEWT_FILES = new Map();
  new BroadcastChannel('newt-open').onmessage = function (e) {
    const text = e.data && NEWT_FILES.get(e.data.ask);
    if (text !== undefined) this.postMessage({ key: e.data.ask, text });
  };

  const NEWT_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" ' +
                    'stroke-linejoin="round" aria-hidden="true"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>' +
                    '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>';

  // a button in the Converter's two lines: "Open in Newt" (user, 2026-10-21; it was "Newt"), and under
  // it the variant, small; white with the blue edge (user, 2026-10-21; it was grey; Newt's orange tried and dropped), the external-link
  // icon after it (the buttons made wider for it)
  function newtButton(text, name, variant) {
    const a = document.createElement('a');
    const key = RUN + '-' + (NEWT_FILES.size + 1);
    NEWT_FILES.set(key, text);
    a.className = 'cv-btn cv-alt'; a.href = NEWT + '?f=' + key + '#' + encodeURIComponent(name); a.target = '_blank';
    a.title = hover('Open in Newt', variant, '', name);
    const lines = document.createElement('span'); lines.className = 'cv-lines';
    lines.append('Open in Newt');
    for (const t of variant ? variant.split(', ') : []) {  // "plain, straight line": a line each
      const v = document.createElement('span'); v.className = 'cv-variant'; v.textContent = t; lines.append(v);
    }
    a.append(lines);
    a.insertAdjacentHTML('beforeend', NEWT_ICON);
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
