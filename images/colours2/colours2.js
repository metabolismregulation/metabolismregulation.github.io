// Colour theme playground for the maps of the page's map menu (#c2-maps).
// The map is the yEd SVG export tagged by maps-workbench tools/colours_svg.py:
// each fill has the class c-<role>, each text t-<role> of the fill under it
// (t-page on the background), and lines and arrowheads take the root's colour.
// A theme sets one CSS variable per role (the rules are in colours.md).
(function () {
  'use strict';

  var ROLES = [
    { id: 'compartment', name: 'Compartment', cls: 0 },
    { id: 'complex', name: 'Complex', cls: 3 },
    { id: 'protein', name: 'Protein', cls: 2 },
    { id: 'metabolite', name: 'Chemical', cls: 4 },
    { id: 'hlProtein', name: 'Highlighted protein', cls: 6, hl: true },
    { id: 'white', name: 'Process, labels', cls: 1 },
    { id: 'ink', name: 'Lines', cls: -1 },
    { id: 'text', name: 'Text', cls: -1 },
    { id: 'gene', name: 'Gene, mRNA', cls: 8, after: 'white' }
  ];
  // Roles as listed on the page: Gene, mRNA right after Process, labels.
  // ROLES itself keeps the order of the theme code, where gene comes last.
  var ROLE_VIEW = ROLES.filter(function (r) { return !r.after; });
  ROLES.forEach(function (r) {
    if (r.after) ROLE_VIEW.splice(ROLE_VIEW.findIndex(function (v) { return v.id === r.after; }) + 1, 0, r);
  });

  var PRESETS = window.C2_PRESETS;

  // Machado et al. 2009, severity 1.0, applied in linear RGB
  var CVD = {
    none: null,
    deuteranopia: [0.367322, 0.860646, -0.227968, 0.280085, 0.672501, 0.047413, -0.01182, 0.04294, 0.968881],
    protanopia: [0.152286, 1.052583, -0.204868, 0.114503, 0.786281, 0.099216, -0.003882, -0.048116, 1.051998],
    tritanopia: [1.255528, -0.076749, -0.178779, -0.078411, 0.930809, 0.147602, 0.004733, 0.691367, 0.3039]
  };

  var theme = {};
  var armed = null; // swatch picked from an image, waiting to be assigned
  var map = document.getElementById('c2-map');
  var svg = null; // the map, once loaded

  // ---------- colour maths ----------
  function hexToRgb(h) {
    h = h.replace('#', '');
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  }
  function rgbToHex(c) {
    return '#' + c.map(function (v) {
      v = Math.max(0, Math.min(255, Math.round(v)));
      return (v < 16 ? '0' : '') + v.toString(16);
    }).join('').toUpperCase();
  }
  function lin(v) { v /= 255; return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }
  function delin(v) { v = v <= 0.0031308 ? 12.92 * v : 1.055 * Math.pow(v, 1 / 2.4) - 0.055; return v * 255; }

  function rgbToOklab(c) {
    var r = lin(c[0]), g = lin(c[1]), b = lin(c[2]);
    var l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
    var m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
    var s = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
    return [
      0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s,
      1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s,
      0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s
    ];
  }
  function oklabToRgbLinear(o) {
    var l = Math.pow(o[0] + 0.3963377774 * o[1] + 0.2158037573 * o[2], 3);
    var m = Math.pow(o[0] - 0.1055613458 * o[1] - 0.0638541728 * o[2], 3);
    var s = Math.pow(o[0] - 0.0894841775 * o[1] - 1.291485548 * o[2], 3);
    return [
      4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
      -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
      -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s
    ];
  }
  function oklabToRgb(o) { return oklabToRgbLinear(o).map(delin); }
  function inGamut(o) {
    return oklabToRgbLinear(o).every(function (v) { return v >= -0.0005 && v <= 1.0005; });
  }

  function luminance(c) { return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]); }
  function contrast(a, b) {
    var la = luminance(hexToRgb(a)), lb = luminance(hexToRgb(b));
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }
  // Text on a fill: the Text colour, or white where white reads better
  // (dark fills). Equal WCAG contrast would switch at a fill luminance of
  // about 0.18, which keeps black text on fills that already look dark; the
  // weight WHITE_BIAS moves the switch to 0.26 (with black text), below
  // the 0.34-0.42 range APCA's author gives for text; chosen by eye for
  // this light page.
  var WHITE_BIAS = 1.83;
  function textOn(fill) {
    return WHITE_BIAS * contrast('#FFFFFF', fill) > contrast(theme.text, fill) ? '#FFFFFF' : theme.text;
  }

  function simulate(rgb, mode) {
    var M = CVD[mode];
    if (!M) return rgb;
    var r = lin(rgb[0]), g = lin(rgb[1]), b = lin(rgb[2]);
    return [
      delin(Math.max(0, Math.min(1, M[0] * r + M[1] * g + M[2] * b))),
      delin(Math.max(0, Math.min(1, M[3] * r + M[4] * g + M[5] * b))),
      delin(Math.max(0, Math.min(1, M[6] * r + M[7] * g + M[8] * b)))
    ];
  }

  // ---------- map rendering ----------
  function loadMap(src, done) {
    fetch(src).then(function (r) { return r.text(); }).then(function (t) {
      map.innerHTML = t;
      svg = map.querySelector('svg');
      svg.removeAttribute('width');
      svg.removeAttribute('height');
      mapW = svg.viewBox.baseVal.width;
      mapH = svg.viewBox.baseVal.height;
      done();
      fit();
    });
  }

  // ---------- viewer ----------
  // A window of one height for every map, as the Atlas's (a lean copy of its
  // viewer): the map fits it when loaded, the wheel or a pinch zooms at the
  // pointer, a drag moves it, Fit returns. The zoom is shown as on the Atlas:
  // 100% is the Atlas's reading size, 110% of the map pages' 0.675 px per
  // yEd unit (user, 2026-10-22).
  var view = document.getElementById('c2-view');
  var STANDARD = 0.7425, MIN = 0.08, MAX = 4, KEEP = 80, TOP = 36; // KEEP: pixels of map kept in view
  var z = STANDARD, tx = 0, ty = 0, moved = false, mapW = 0, mapH = 0;
  // pointer positions come in screen pixels, the site is zoomed (style.scss)
  function pz() { return view.currentCSSZoom || 1; }
  function draw() {
    if (!svg) return;
    var w = mapW * z, h = mapH * z, vw = view.clientWidth, vh = view.clientHeight;
    tx = Math.min(vw - Math.min(KEEP, w), Math.max(Math.min(KEEP, w) - w, tx));
    ty = Math.min(vh - Math.min(KEEP, h), Math.max(Math.min(KEEP, h) - h, ty));
    // sized by width and height, not a scale transform, so the map stays sharp
    svg.style.width = w + 'px';
    svg.style.height = h + 'px';
    svg.style.transform = 'translate(' + tx + 'px,' + ty + 'px)';
    document.getElementById('c2-zoom').textContent = Math.round(z / STANDARD * 100) + '%';
  }
  function zoomAt(nz, cx, cy) {
    nz = Math.max(MIN, Math.min(MAX, nz));
    tx = cx - (cx - tx) * nz / z;
    ty = cy - (cy - ty) * nz / z;
    z = nz;
    moved = true;
    draw();
  }
  // the whole map below the strip of the controls, never larger than the
  // reading size, at the top and centred left to right, as on the Atlas
  function fit() {
    if (!svg) return;
    z = Math.min(view.clientWidth * 0.96 / mapW, (view.clientHeight - TOP - 12) / mapH, STANDARD);
    tx = (view.clientWidth - mapW * z) / 2;
    ty = TOP;
    moved = false;
    draw();
  }
  function centre() { return [view.clientWidth / 2, view.clientHeight / 2]; }
  document.getElementById('c2-in').addEventListener('click', function () { var c = centre(); zoomAt(z * 1.25, c[0], c[1]); });
  document.getElementById('c2-out').addEventListener('click', function () { var c = centre(); zoomAt(z / 1.25, c[0], c[1]); });
  document.getElementById('c2-fit').addEventListener('click', fit);
  view.addEventListener('wheel', function (e) {
    e.preventDefault();
    var r = view.getBoundingClientRect();
    zoomAt(z * Math.exp(-e.deltaY * (e.deltaMode ? 0.05 : 0.0015)), (e.clientX - r.left) / pz(), (e.clientY - r.top) / pz());
  }, { passive: false });
  view.addEventListener('dblclick', function (e) {
    if (e.target.closest('.c2-ctrl')) return;
    var r = view.getBoundingClientRect();
    zoomAt(z * 1.5, (e.clientX - r.left) / pz(), (e.clientY - r.top) / pz());
  });
  // drag with one pointer, pinch with two
  var pts = {}, last = null;
  view.addEventListener('pointerdown', function (e) {
    if (e.target.closest('.c2-ctrl')) return;
    // leave the lower right corner to the browser's resize handle
    var r = view.getBoundingClientRect();
    if (e.clientX > r.right - 18 && e.clientY > r.bottom - 18) return;
    view.setPointerCapture(e.pointerId);
    pts[e.pointerId] = [e.clientX, e.clientY];
    last = null;
    view.classList.add('c2-drag');
  });
  view.addEventListener('pointermove', function (e) {
    if (!pts[e.pointerId]) return;
    var prev = pts[e.pointerId];
    pts[e.pointerId] = [e.clientX, e.clientY];
    var ids = Object.keys(pts);
    if (ids.length === 1) {
      tx += (e.clientX - prev[0]) / pz();
      ty += (e.clientY - prev[1]) / pz();
      moved = true;
      draw();
    } else if (ids.length === 2) {
      var a = pts[ids[0]], b = pts[ids[1]], r = view.getBoundingClientRect();
      var d = Math.hypot(a[0] - b[0], a[1] - b[1]);
      if (last) zoomAt(z * d / last, ((a[0] + b[0]) / 2 - r.left) / pz(), ((a[1] + b[1]) / 2 - r.top) / pz());
      last = d;
    }
  });
  function release(e) {
    delete pts[e.pointerId];
    last = null;
    if (!Object.keys(pts).length) view.classList.remove('c2-drag');
  }
  view.addEventListener('pointerup', release);
  view.addEventListener('pointercancel', release);
  view.addEventListener('keydown', function (e) {
    var c = centre();
    if (e.key === '+' || e.key === '=') zoomAt(z * 1.25, c[0], c[1]);
    else if (e.key === '-') zoomAt(z / 1.25, c[0], c[1]);
    else if (e.key === '0') fit();
    else return;
    e.preventDefault();
  });
  // the window's height: 77% of the browser window, as the Atlas's, until
  // the reader drags its lower edge (the browser then sets its own height)
  var autoH = null;
  function viewHeight() {
    if (autoH !== null && view.style.height !== autoH) return;
    autoH = Math.round(Math.max(300, window.innerHeight / pz() * 0.77)) + 'px';
    view.style.height = autoH;
  }
  viewHeight();
  window.addEventListener('resize', viewHeight);
  // a new window size: the fitted map fits again, a moved one stays
  if (window.ResizeObserver) new ResizeObserver(function () { if (moved) draw(); else fit(); }).observe(view);

  function render() {
    if (!svg) return;
    var mode = document.getElementById('c2-cvd').value;
    var hex = {};
    ROLES.forEach(function (r) { if (r.cls >= 0 && theme[r.id]) hex[r.id] = theme[r.id]; });
    // Highlight off: highlighted elements are drawn like ordinary ones
    if (!document.getElementById('c2-hl').checked) hex.hlProtein = hex.protein;
    // "Complex transparent": complexes take the compartment colour
    if (document.getElementById('c2-cxbg').checked) hex.complex = hex.compartment;
    function seen(h) { return rgbToHex(simulate(hexToRgb(h), mode)); }
    var st = svg.style;
    Object.keys(hex).forEach(function (id) {
      st.setProperty('--c-' + id, seen(hex[id]));
      st.setProperty('--t-' + id, seen(textOn(hex[id])));
      // white text is drawn semibold
      st.setProperty('--w-' + id, whiteOn(hex[id]) ? '600' : 'normal');
    });
    st.setProperty('--ink', seen(theme.ink));
    st.setProperty('--t-page', seen(theme.text));
  }

  // ---------- mixer ----------
  // Chemical column: a fixed list (false), or the backup that calculates
  // chemicals from the chosen protein by hue angle (true).
  var CHEM_FROM_ANGLE = false;
  // Named colours from the presets; pick one per column to build a theme.
  var MIX = [
    { role: 'compartment', title: 'Background', items: [
      // warm to cool (OKLab b, yellow to blue)
      ['Paper', 'F7F6F3'], ['Chalk', 'F8F8F8'], ['Slate', 'F3F4F6']] },
    { role: 'protein', title: 'Protein', items: [
      // a small starting set; colours found on the map are added with +
      ['Stone', 'D9D2C7'], ['Paper', 'D4D3CA'], ['Lichen', 'D3DBC7']] },
    CHEM_FROM_ANGLE ? { role: 'metabolite', title: 'Chemical', generated: true } :
    { role: 'metabolite', title: 'Chemical', items: [
      // a small starting set; colours found on the map are added with +
      ['Pearl', 'EFEDE7'], ['Silver', 'E8E6E2'], ['Willow', 'E8E8DE']] }
  ];

  // Backup (CHEM_FROM_ANGLE): chemicals are calculated from the chosen protein: eleven hues on the
  // OKLCH wheel from +80 through 180 to -80 degrees from the protein's hue in
  // 20-degree steps (hues within 60 degrees of the protein are left out), one
  // lightness step (+0.04) above the protein, then 10% closer to white, colour strength 90% of the protein's.
  var CHEM_OFFSETS = [80, 100, 120, 140, 160, 180, -160, -140, -120, -100, -80];
  var CHEM_NAMES = [[20, 'Rose'], [50, 'Peach'], [80, 'Sand'], [110, 'Straw'], [135, 'Leaf'], [155, 'Green'],
    [175, 'Mint'], [195, 'Teal'], [210, 'Aqua'], [228, 'Mist'], [245, 'Sky'], [265, 'Blue'], [290, 'Iris'],
    [320, 'Lilac'], [345, 'Pink'], [360, 'Rose']];

  function lchOf(hex) {
    var o = rgbToOklab(hexToRgb(hex));
    return { L: o[0], C: Math.hypot(o[1], o[2]), h: (Math.atan2(o[2], o[1]) * 180 / Math.PI + 360) % 360 };
  }
  function lchHex(L, C, hDeg) {
    var h = hDeg * Math.PI / 180, c = C, lab = [L, c * Math.cos(h), c * Math.sin(h)];
    while (!inGamut(lab) && c > 0) {
      c -= 0.002;
      lab = [L, c * Math.cos(h), c * Math.sin(h)];
    }
    return rgbToHex(oklabToRgb(lab));
  }
  function chemOptions(protein) {
    var p = lchOf(protein);
    var L0 = p.L + 0.04, L = Math.min(L0 + 0.1 * (1 - L0), 0.96), C = 0.9 * Math.min(Math.max(p.C, 0.025), 0.045);
    return CHEM_OFFSETS.map(function (off) {
      var h = Math.round((p.h + off + 360) % 360);
      var name = CHEM_NAMES.filter(function (n) { return h <= n[0]; })[0][1];
      var sign = off > 0 && off < 180 ? '+' : off < 0 ? '\u2212' : '';
      return { off: off, h: h, name: name + ' ' + sign + Math.abs(off) + '\u00B0', hex: lchHex(L, C, h) };
    });
  }
  var chemSlot = null; // offset of the chosen chemical; null when it is not from the list

  function oklabDist(a, b, mode) {
    var x = rgbToOklab(simulate(hexToRgb(a), mode)), y = rgbToOklab(simulate(hexToRgb(b), mode));
    return 100 * Math.sqrt(dist(x, y));
  }
  function pairDistance(a, b) {
    return Math.min(oklabDist(a, b, 'none'), oklabDist(a, b, 'deuteranopia'));
  }

  // Colours added to the Mixer with + are kept in this browser, per column,
  // after the built-in ones; they can be removed with their cross.
  var MIX_KEY = 'colours.mixerColours';
  // added colours are [name, hex, id]; the id tells apart repeats of a colour
  // earlier long names, shortened for colours already added in this browser
  var SHORT_NAMES = { Mushroom: 'Oat', Pistachio: 'Fern', Celadon: 'Jade', Seafoam: 'Foam',
    Periwinkle: 'Frost', Lavender: 'Iris' };
  function loadMixAdded() {
    var all;
    try { all = JSON.parse(localStorage.getItem(MIX_KEY)) || {}; } catch (e) { all = {}; }
    Object.keys(all).forEach(function (role) {
      all[role].forEach(function (it, i) {
        if (!it[2]) it[2] = 'a' + i + it[1];
        var m = /^(\S+)( \d+)?$/.exec(it[0]);
        if (m && SHORT_NAMES[m[1]]) it[0] = SHORT_NAMES[m[1]] + (m[2] || '');
      });
    });
    return all;
  }
  function mixKey(it) { return it[2] || '#' + it[1]; }
  function saveMixAdded(all) {
    try { localStorage.setItem(MIX_KEY, JSON.stringify(all)); } catch (e) { /* storage blocked */ }
  }
  function addMixColour(c, col) {
    var hex = theme[col.role].slice(1).toUpperCase();
    var all = loadMixAdded(), mine = all[col.role] || [];
    var list = col.items.concat(mine);
    var base = colourName('#' + hex), name = base, n = 2;
    while (list.some(function (it) { return it[0] === name; })) name = base + ' ' + n++;
    mine.push([name, hex, 'a' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)]);
    all[col.role] = mine;
    saveMixAdded(all);
    refillMixCols(col);
    syncMixer();
  }
  // Double-click an added colour to rename it: a text field takes the place
  // of its row (a field cannot sit inside the button). Enter or clicking
  // elsewhere keeps the new name, Escape cancels.
  function renameMixColour(b, col, it) {
    var row = document.createElement('div');
    row.className = 'c2-dot c2-renaming';
    row.innerHTML = '<i style="background:#' + it[1] + '"></i>';
    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'c2-rename';
    input.value = it[0];
    row.appendChild(input);
    b.replaceWith(row);
    input.focus();
    input.select();
    var done = false;
    var finish = function (keep) {
      if (done) return;
      done = true;
      var v = input.value.trim();
      if (keep && v && v !== it[0]) {
        var all = loadMixAdded();
        all[col.role] = (all[col.role] || []).map(function (a) { return a[2] === it[2] ? [v, a[1], a[2]] : a; });
        saveMixAdded(all);
      }
      refillMixCols(col);
      syncMixer();
    };
    input.addEventListener('keydown', function (e) {
      e.stopPropagation();
      if (e.key === 'Enter') finish(true);
      else if (e.key === 'Escape') finish(false);
    });
    input.addEventListener('blur', function () { finish(true); });
  }
  function removeMixColour(c, col, id) {
    var all = loadMixAdded();
    all[col.role] = (all[col.role] || []).filter(function (it) { return it[2] !== id; });
    saveMixAdded(all);
    refillMixCols(col);
    syncMixer();
  }
  // Mixer colours can be dragged by their swatch to reorder a column; the
  // order is kept in this browser.
  var MIX_ORDER_KEY = 'colours.mixerOrder';
  var mixDrag = null, mixDragged = false;
  function loadMixOrder() {
    try { return JSON.parse(localStorage.getItem(MIX_ORDER_KEY)) || {}; } catch (e) { return {}; }
  }
  function saveMixOrder(c, role) {
    var all = loadMixOrder();
    all[role] = Array.prototype.map.call(c.querySelectorAll('.c2-dot'), function (b) {
      return b.getAttribute('data-key');
    });
    try { localStorage.setItem(MIX_ORDER_KEY, JSON.stringify(all)); } catch (e) { /* storage blocked */ }
  }
  document.addEventListener('pointermove', function (e) {
    if (!mixDrag) return;
    var col = mixDrag.parentNode;
    var over = document.elementFromPoint(e.clientX, e.clientY);
    over = over && over.closest('.c2-dot');
    if (!over || over === mixDrag || over.parentNode !== col) return;
    var r = over.getBoundingClientRect();
    col.insertBefore(mixDrag, e.clientY < r.top + r.height / 2 ? over : over.nextSibling);
    mixDragged = true;
  });
  function stopMixDrag() {
    if (!mixDrag) return;
    mixDrag.classList.remove('c2-dragging');
    if (mixDragged) {
      var role = mixDrag.getAttribute('data-role');
      saveMixOrder(mixDrag.parentNode, role);
      refillMixCols(MIX.filter(function (col) { return col.role === role; })[0], mixDrag.parentNode);
      syncMixer();
      setTimeout(function () { mixDragged = false; }, 0);
    }
    mixDrag = null;
  }
  document.addEventListener('pointerup', stopMixDrag);
  document.addEventListener('pointercancel', stopMixDrag);

  function fillMixCol(c, col) {
    c.innerHTML = '<div class="c2-mixtitle">' + col.title + '</div>';
    var added = loadMixAdded()[col.role] || [];
    var order = loadMixOrder()[col.role] || [];
    var all = col.items.concat(added);
    var rank = function (it) {
      var i = order.indexOf(mixKey(it));
      return i < 0 ? order.length + all.indexOf(it) : i;
    };
    all.slice().sort(function (x, y) { return rank(x) - rank(y); }).forEach(function (it) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'c2-dot';
      b.setAttribute('data-role', col.role);
      b.setAttribute('data-hex', '#' + it[1]);
      b.setAttribute('data-key', mixKey(it));
      b.title = it[0] + ' #' + it[1];
      b.innerHTML = '<i style="background:#' + it[1] + '"></i><span class="c2-dname">' +
        it[0].replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</span>';
      b.querySelector('i').addEventListener('pointerdown', function (e) {
        e.preventDefault();
        mixDrag = b;
        mixDragged = false;
        b.classList.add('c2-dragging');
      });
      b.addEventListener('click', function (e) {
        if (mixDragged) { e.stopImmediatePropagation(); return; }
        // a new protein brings the chosen chemical along, recalculated for it
        // the chemical keeps its offset when the protein changes; 180 degrees
        // when no chemical from the list was chosen yet
        if (CHEM_FROM_ANGLE && col.role === 'protein') {
          var off = chemSlot !== null ? chemSlot : 180;
          theme.metabolite = chemOptions('#' + it[1]).filter(function (o) { return o.off === off; })[0].hex;
        }
        setRole(col.role, '#' + it[1]);
      });
      if (col.items.indexOf(it) < 0) {
        b.addEventListener('dblclick', function (e) {
          if (e.target.closest('.c2-del, i')) return;
          renameMixColour(b, col, it);
        });
        var x = document.createElement('span');
        x.className = 'c2-del';
        x.title = 'Remove this colour';
        x.addEventListener('click', function (e) { e.stopPropagation(); removeMixColour(c, col, it[2]); });
        b.appendChild(x);
      }
      c.appendChild(b);
    });
    var add = document.createElement('button');
    add.type = 'button';
    add.className = 'c2-mixadd';
    add.title = 'Add the ' + col.title.toLowerCase() + ' colour on the map';
    add.innerHTML = '<svg viewBox="0 0 15 15"><rect x="0.5" y="0.5" width="14" height="14"/>' +
      '<path d="M4 7.5h7M7.5 4v7" stroke="currentColor"/></svg>';
    add.addEventListener('click', function () { addMixColour(c, col); });
    c.appendChild(add);
  }
  // a change in a column is redrawn in every copy of it on the page
  function refillMixCols(col, skip) {
    Array.prototype.forEach.call(document.querySelectorAll('.c2-mixcol[data-role="' + col.role + '"]'), function (c) {
      if (c !== skip) fillMixCol(c, col);
    });
  }
  function buildMixer(id) {
    var box = document.getElementById(id);
    if (!box) return;
    MIX.forEach(function (col) {
      var c = document.createElement('div');
      c.className = 'c2-mixcol';
      c.innerHTML = '<div class="c2-mixtitle">' + col.title + '</div>';
      if (col.generated) {
        if (id === 'c2-mixer') c.id = 'c2-chemcol';
        box.appendChild(c);
        return;
      }
      c.setAttribute('data-role', col.role);
      box.appendChild(c);
      fillMixCol(c, col);
    });
  }


  // The Mixer marks its items only once it is being used: a preset click
  // clears the marks, a Mixer click brings them back.
  var mixerLinked = false;
  function syncMixer() {
    var names = {};
    Array.prototype.forEach.call(document.querySelectorAll('.c2-dot'), function (b) {
      var role = b.getAttribute('data-role'), hex = b.getAttribute('data-hex');
      var on = mixerLinked && theme[role] === hex;
      b.classList.toggle('c2-on', on);
      if (on) names[role] = b.textContent;
    });
    if (!CHEM_FROM_ANGLE) return;
    // rebuild the chemical column for the current protein
    var col = document.getElementById('c2-chemcol');
    col.innerHTML = '<div class="c2-mixtitle">Chemical</div>';
    var match = null;
    chemOptions(theme.protein).forEach(function (o) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'c2-dot';
      b.title = o.name + ' #' + o.hex.slice(1);
      b.innerHTML = '<i style="background:' + o.hex + '"></i>' + o.name;
      if (mixerLinked && theme.metabolite === o.hex) { b.classList.add('c2-on'); match = o; }
      b.addEventListener('click', function () {
        chemSlot = o.off;
        setRole('metabolite', o.hex);
      });
      col.appendChild(b);
    });
    chemSlot = match ? match.off : null;
    if (match) names.metabolite = match.name;
  }

  // ---------- controls ----------
  var roleBox = document.getElementById('c2-roles');

  // sfx tells apart the fields of more than one Roles list ('' for the first)
  var ROLE_SFX = [''];
  function buildRoles(box, sfx) {
    if (!box) return;
    ROLE_VIEW.forEach(function (r) {
      var row = document.createElement('div');
      row.className = 'c2-role' + (r.hl ? ' c2-hl' : '');
      row.innerHTML =
        '<input type="color" id="c2-in' + sfx + '-' + r.id + '">' +
        '<span class="c2-role-name">' + r.name + '</span>' +
        '<input type="text" class="c2-hexin" id="c2-hex' + sfx + '-' + r.id + '" maxlength="7" spellcheck="false">' +
        '<span class="c2-cr" id="c2-cr' + sfx + '-' + r.id + '"></span>';
      box.appendChild(row);
      var input = row.querySelector('input[type=color]');
      input.addEventListener('input', function () { setRole(r.id, input.value); });
      // hex field: click selects it for copying; typing or pasting a hex applies it
      var hexIn = row.querySelector('.c2-hexin');
      hexIn.addEventListener('focus', function () { hexIn.select(); });
      hexIn.addEventListener('input', function () {
        var v = hexIn.value.trim().replace(/^#?/, '#');
        if (/^#[0-9a-fA-F]{6}$/.test(v)) setRole(r.id, v);
      });
      hexIn.addEventListener('blur', function () { hexIn.value = theme[r.id]; });
      // drag a row onto another row to copy its colour there
      row.draggable = true;
      row.addEventListener('dragstart', function (e) {
        e.dataTransfer.setData('text/plain', theme[r.id]);
        e.dataTransfer.effectAllowed = 'copy';
      });
      row.addEventListener('dragover', function (e) { e.preventDefault(); row.classList.add('c2-dropping'); });
      row.addEventListener('dragleave', function () { row.classList.remove('c2-dropping'); });
      row.addEventListener('drop', function (e) {
        e.preventDefault();
        row.classList.remove('c2-dropping');
        var v = e.dataTransfer.getData('text/plain').trim().replace(/^#?/, '#');
        if (/^#[0-9a-fA-F]{6}$/.test(v)) setRole(r.id, v);
      });
      row.addEventListener('click', function (e) {
        if (!armed || e.target.tagName === 'INPUT') return;
        e.preventDefault();
        setRole(r.id, armed);
      });
    });
  }

  var queued = false;
  function setRole(id, hex) {
    theme[id] = hex.toUpperCase();
    syncControls();
    if (!queued) {
      queued = true;
      requestAnimationFrame(function () { queued = false; render(); });
    }
  }

  // ---------- swap and lighter ----------
  // Lighter works like a volume slider on the fills, running right to left
  // (dir=rtl): right (0) is the theme as it was when the slider was first
  // moved, left (100) the lightest and softest version
  // (each fill moved 80% of the way to white in OKLab lightness, chroma eased
  // to a half). Any other change to the theme starts from scratch again.
  var LIGHT_ROLES = ['compartment', 'complex', 'protein', 'metabolite'];
  var lightBase = null, adjusting = false;
  function lighten(hex, k) {
    var o = rgbToOklab(hexToRgb(hex)), f = 1 - 0.6 * k;
    return rgbToHex(oklabToRgb([o[0] + k * (1 - o[0]), o[1] * f, o[2] * f])).toUpperCase();
  }
  function applyLight() {
    var k = 0.8 * document.getElementById('c2-light').value / 100;
    if (!lightBase) {
      lightBase = {};
      LIGHT_ROLES.forEach(function (id) { lightBase[id] = theme[id]; });
    }
    adjusting = true;
    LIGHT_ROLES.forEach(function (id) { theme[id] = lighten(lightBase[id], k); });
    syncControls();
    adjusting = false;
    render();
  }
  function swapProteinChemical() {
    var t = theme.protein;
    theme.protein = theme.metabolite;
    theme.metabolite = t;
    if (lightBase) {
      t = lightBase.protein;
      lightBase.protein = lightBase.metabolite;
      lightBase.metabolite = t;
    }
    adjusting = true;
    syncControls();
    adjusting = false;
    render();
  }

  function syncControls() {
    if (!adjusting && lightBase) { // the theme changed some other way
      lightBase = null;
      document.getElementById('c2-light').value = 0;
    }
    ROLES.forEach(function (r) { ROLE_SFX.forEach(function (sfx) {
      if (!document.getElementById('c2-in' + sfx + '-' + r.id)) return;
      document.getElementById('c2-in' + sfx + '-' + r.id).value = theme[r.id].toLowerCase();
      var hx = document.getElementById('c2-hex' + sfx + '-' + r.id);
      if (document.activeElement !== hx) hx.value = theme[r.id];
      var cr = document.getElementById('c2-cr' + sfx + '-' + r.id);
      if (r.cls < 0) { cr.textContent = ''; return; }
      var white = textOn(theme[r.id]) === '#FFFFFF' && theme.text !== '#FFFFFF';
      var v = contrast(theme[r.id], textOn(theme[r.id]));
      cr.textContent = v.toFixed(1) + ':1' + (white ? ' w' : '');
      cr.className = 'c2-cr' + (v < 7 ? ' c2-low' : '');
      cr.title = 'Contrast of text on this fill (WCAG). Below 7:1 reads poorly at small sizes.' +
        (white ? ' w: this fill is dark, so its text is drawn white.' : '');
    }); });
    document.getElementById('c2-export').value = exportText();
    document.getElementById('c2-cdnote').hidden = true;
    syncMixer();
    syncPresets();
    noteChange();
  }

  // ---------- undo ----------
  // Ctrl+Z / Cmd+Z goes back one change, with Shift forward again. Every
  // change passes through syncControls; changes in quick succession (a held
  // arrow key, dragging the slider or a colour picker) count as one step.
  var UNDO_MAX = 50, UNDO_GAP = 700;
  var undoStack = [], redoStack = [], current = null, lastChange = 0, restoring = false;
  function fullCode() {
    return ROLES.map(function (r) { return theme[r.id].slice(1).toUpperCase(); }).join(' ');
  }
  function noteChange() {
    var s = fullCode();
    if (s === current) return;
    if (current !== null && !restoring) {
      var now = Date.now();
      if (now - lastChange > UNDO_GAP) {
        undoStack.push(current);
        if (undoStack.length > UNDO_MAX) undoStack.shift();
      }
      redoStack = [];
      lastChange = now;
    }
    current = s;
  }
  function stepBack(from, to) {
    if (!from.length) return;
    to.push(current);
    restoring = true;
    applyPreset(from.pop());
    restoring = false;
    lastChange = 0;
  }

  // Theme link: Copy link copies the page address (with ?map= for a map other
  // than the first) and the current theme code after # (e.g.
  // /colours/?map=inos#F7F6F3-FFFFFF-...); opening such a link
  // applies the theme. The address bar itself is left unchanged.
  function themeLink() {
    return location.origin + location.pathname + location.search + '#' + exportText().replace(/ /g, '-');
  }
  function themeFromLink() {
    var v = decodeURIComponent(location.hash.slice(1)).replace(/[-\s,]+/g, ' ').trim();
    return /^([0-9a-fA-F]{6} ){6,8}[0-9a-fA-F]{6}$/.test(v) ? v.toUpperCase() : null;
  }
  // ---------- downloads ----------
  // The yEd and CellDesigner files are built from templates made once by
  // make_exports.py: each colour there is a role placeholder such as
  // {protein}, filled here with the colours shown on the map.
  function shownColours() {
    var c = {};
    ROLES.forEach(function (r) { c[r.id] = theme[r.id].slice(1).toUpperCase(); });
    if (!document.getElementById('c2-hl').checked) c.hlProtein = c.protein;
    if (document.getElementById('c2-cxbg').checked) c.complex = c.compartment;
    // names on each fill: white and bold where the map shows white text
    ROLES.forEach(function (r) {
      if (r.cls < 0) return;
      var white = whiteOn('#' + c[r.id]);
      c['t_' + r.id] = white ? 'FFFFFF' : c.text;
      c['f_' + r.id] = white ? 'bold' : 'plain';
    });
    return c;
  }
  function whiteOn(fill) {
    return textOn(fill) === '#FFFFFF' && theme.text !== '#FFFFFF';
  }
  // the CellDesigner note shows after that download while some fill has white text
  function anyWhiteText() {
    var c = shownColours();
    return ROLES.some(function (r) { return r.cls >= 0 && c['f_' + r.id] === 'bold'; });
  }
  // File name: the preset's name if the map shows one, then the
  // background, protein and chemical colours
  function themeSlug() {
    var on = document.querySelector('#c2-presets .c2-on');
    var c = shownColours(), codes = [c.compartment, c.protein, c.metabolite].join('-');
    if (!on) return codes;
    return on.getAttribute('data-name').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') + '-' + codes;
  }
  function download(ext, name, lower) {
    var v = document.querySelector('.c2-under').getAttribute('data-v');
    fetch(mapBase + '.template.' + ext + '?v=' + v).then(function (r) { return r.text(); }).then(function (t) {
      var c = shownColours();
      t = t.replace(/\{(\w+)\}/g, function (m, id) {
        return c[id] ? (lower ? c[id].toLowerCase() : c[id]) : m;
      });
      var a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([t], { type: 'application/xml' }));
      a.download = name.replace('{theme}', themeSlug());
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    });
  }

  function copyLink() {
    var url = themeLink();
    if (navigator.clipboard) navigator.clipboard.writeText(url).catch(function () { window.prompt('Link to this theme:', url); });
    else window.prompt('Link to this theme:', url);
  }

  // Mark the preset that matches the current colours, if any (the highlight
  // is left out of the comparison: it is set in Roles only)
  function withoutHl(code) {
    return code.split(' ').filter(function (h, i) { return i !== 4; }).join(' ');
  }
  function syncPresets() {
    if (!theme.ink) return; // before the first theme is applied
    var cur = withoutHl(themeCode(false));
    Array.prototype.forEach.call(document.querySelectorAll('#c2-presets .c2-preset'), function (b) {
      b.classList.toggle('c2-on', withoutHl(b.getAttribute('data-theme')) === cur);
    });
  }

  // Theme code: 7 colours; an 8th for text when it differs from the lines,
  // a 9th for gene and mRNA when they differ from processes. Shorter codes
  // (all presets) fill in those defaults.
  // keepHl: leave the highlight as set in Roles (presets); a pasted theme
  // code sets it too.
  function applyPreset(str, keepHl) {
    var hs = str.split(/\s+/);
    if (hs.length < 8) hs[7] = hs[6];
    if (hs.length < 9) hs[8] = hs[5];
    ROLES.forEach(function (r, i) {
      if (!(keepHl && r.id === 'hlProtein' && theme.hlProtein)) theme[r.id] = '#' + hs[i];
    });
    syncControls();
    render();
  }

  function themeCode(cxbg) {
    var hs = ROLES.map(function (r) {
      return (cxbg && r.id === 'complex' ? theme.compartment : theme[r.id]).slice(1).toUpperCase();
    });
    // trailing colours equal to their defaults are left out:
    // gene (9th) defaults to the process colour, text (8th) to the lines
    if (hs[8] === hs[5]) {
      hs.pop();
      if (hs[7] === hs[6]) hs.pop();
    }
    return hs.join(' ');
  }
  function exportText() {
    return themeCode(document.getElementById('c2-cxbg').checked);
  }

  // Preset order can be rearranged by dragging the colours; the order is kept
  // in this browser only. Reset returns to the order in PRESETS and shows
  // hidden built-in presets again.
  var ORDER_KEY = 'colours.presetOrder';
  var dragging = null, dragged = false;
  var lastPreset = null;

  function loadOrder() {
    try { return JSON.parse(localStorage.getItem(ORDER_KEY)) || []; } catch (e) { return []; }
  }
  function saveOrder() {
    var names = Array.prototype.map.call(document.querySelectorAll('#c2-presets .c2-preset'), function (el) {
      return el.getAttribute('data-name');
    });
    try { localStorage.setItem(ORDER_KEY, JSON.stringify(names)); } catch (e) { /* storage blocked */ }
  }

  document.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    var box = dragging.parentNode;
    var over = document.elementFromPoint(e.clientX, e.clientY);
    over = over && over.closest('.c2-preset');
    if (!over || over === dragging || over.parentNode !== box) return;
    var r = over.getBoundingClientRect();
    box.insertBefore(dragging, e.clientY < r.top + r.height / 2 ? over : over.nextSibling);
    dragged = true;
  });
  function stopDrag() {
    if (!dragging) return;
    dragging.classList.remove('c2-dragging');
    dragging = null;
    if (dragged) {
      saveOrder();
      // swallow the click that follows the drag, wherever it lands
      setTimeout(function () { dragged = false; }, 0);
    }
  }
  document.addEventListener('pointerup', stopDrag);
  document.addEventListener('pointercancel', stopDrag);

  // Presets added with "Add to presets" are kept in this browser only.
  var CUSTOM_KEY = 'colours.customPresets';
  function loadCustom() {
    try { return JSON.parse(localStorage.getItem(CUSTOM_KEY)) || []; } catch (e) { return []; }
  }
  function saveCustom(list) {
    try { localStorage.setItem(CUSTOM_KEY, JSON.stringify(list)); } catch (e) { /* storage blocked */ }
  }

  // Names for a new preset: the nearest named colour for the protein and for
  // the chemical, "Mono <name>" when both land on the same name.
  // Names are kept short so they fit a Mixer column.
  var COLOUR_NAMES = [
    ['Rose', 'E8C4C4'], ['Blush', 'F2E1DC'], ['Peach', 'F2D2BC'], ['Apricot', 'EFC8A8'], ['Taupe', 'DBCCC7'],
    ['Oat', 'DECEC1'], ['Sand', 'EFE7D8'], ['Linen', 'DDD1BA'], ['Ochre', 'E3C77A'], ['Straw', 'EDE3B8'],
    ['Stone', 'D9D2C7'], ['Paper', 'D4D3CA'], ['Pearl', 'EFEDE7'], ['Silver', 'E8E6E2'], ['Ash', 'C4C8C1'],
    ['Lichen', 'D1D6BD'], ['Celery', 'E4EBDB'], ['Moss', 'BFC7B8'], ['Fern', 'C9D8C1'], ['Sage', 'C1DAC8'],
    ['Mint', 'DDEDE0'], ['Jade', 'BBDBD1'], ['Foam', 'D8EDE7'], ['Sea', 'B8DADA'], ['Aqua', 'D6EDEE'],
    ['Haze', 'B8D9E2'], ['Mist', 'D8ECF4'], ['Powder', 'BBD7E9'], ['Steel', 'BFCFD9'], ['Blue', 'C1D5EE'],
    ['Sky', 'DBEAF9'], ['Ocean', 'BCD3F2'], ['Dusk', 'C5CADD'], ['Frost', 'E2E7F7'], ['Iris', 'D9D0E6'],
    ['Lilac', 'E6D6E6'], ['Grey', 'D6D6D6']];
  function colourName(hex) {
    var o = rgbToOklab(hexToRgb(hex)), best = null;
    var bgs = MIX[0].items.concat([['Chalk', 'F8F8F8'], ['Ivory', 'F7F5F3']]);
    COLOUR_NAMES.concat(bgs).forEach(function (n) {
      var d = dist(o, rgbToOklab(hexToRgb('#' + n[1])));
      if (!best || d < best.d) best = { d: d, name: n[0] };
    });
    return best.name;
  }
  function suggestName() {
    var p = colourName(theme.protein), c = colourName(theme.metabolite);
    return p === c ? 'Mono ' + p.toLowerCase() : p + ' and ' + c.toLowerCase();
  }
  function addPreset() {
    var name = suggestName();
    var taken = function (n) {
      return PRESETS.concat(loadCustom()).some(function (p) { return p[0] === n; });
    };
    var base = name, i = 2;
    while (taken(name)) name = base + ' ' + i++;
    var list = loadCustom();
    list.push([name, themeCode(false)]);
    saveCustom(list);
    buildPresets();
    lastPreset = name;
  }
  // Double-click an added preset to rename it in place: its name turns into
  // a text field inside the row, with the dots and colours left as they are.
  // Enter or clicking elsewhere keeps the new name, Escape cancels.
  function renamePreset(b, name) {
    var label = b.querySelector('.c2-pname');
    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'c2-rename';
    input.value = name;
    label.replaceWith(input);
    ['click', 'dblclick', 'pointerdown'].forEach(function (ev) {
      input.addEventListener(ev, function (e) { e.stopPropagation(); });
    });
    input.focus();
    input.select();
    var done = false;
    var finish = function (keep) {
      if (done) return;
      done = true;
      var v = input.value.trim();
      var taken = PRESETS.concat(loadCustom()).some(function (p) { return p[0] === v; });
      if (keep && v && v !== name && !taken) {
        saveCustom(loadCustom().map(function (p) { return p[0] === name ? [v, p[1]] : p; }));
        var order = loadOrder();
        if (order.length) {
          try {
            localStorage.setItem(ORDER_KEY, JSON.stringify(order.map(function (n) { return n === name ? v : n; })));
          } catch (e) { /* storage blocked */ }
        }
        if (lastPreset === name) lastPreset = v;
      }
      buildPresets();
    };
    input.addEventListener('keydown', function (e) {
      e.stopPropagation();
      if (e.key === 'Enter') finish(true);
      else if (e.key === 'Escape') finish(false);
    });
    input.addEventListener('blur', function () { finish(true); });
  }

  // Built-in presets removed with their cross are only hidden, in this
  // browser; Reset brings them back. Added presets are removed for good.
  var HIDDEN_KEY = 'colours.hiddenPresets';
  function loadHidden() {
    try { return JSON.parse(localStorage.getItem(HIDDEN_KEY)) || []; } catch (e) { return []; }
  }
  function removePreset(name) {
    var custom = loadCustom();
    if (custom.some(function (p) { return p[0] === name; })) {
      saveCustom(custom.filter(function (p) { return p[0] !== name; }));
    } else {
      var hidden = loadHidden();
      if (hidden.indexOf(name) < 0) hidden.push(name);
      try { localStorage.setItem(HIDDEN_KEY, JSON.stringify(hidden)); } catch (e) { /* storage blocked */ }
    }
    buildPresets();
  }

  function buildPresets() {
    var box = document.getElementById('c2-presets');
    box.innerHTML = '';
    var saved = loadOrder();
    var custom = loadCustom();
    var hidden = loadHidden();
    // the first preset (Default) is always shown and has no cross
    var all = PRESETS.filter(function (p, i) { return i === 0 || hidden.indexOf(p[0]) < 0; }).concat(custom);
    var rank = function (p) {
      var i = saved.indexOf(p[0]);
      return i < 0 ? saved.length + all.indexOf(p) : i;
    };
    all.slice().sort(function (x, y) { return rank(x) - rank(y); }).forEach(function (p) {
      // a div acting as a button, so that a text field can sit inside it
      var b = document.createElement('div');
      b.setAttribute('role', 'button');
      b.tabIndex = 0;
      b.className = 'c2-preset';
      b.setAttribute('data-name', p[0]);
      b.setAttribute('data-theme', p[1].toUpperCase());
      var hs = p[1].split(' ');
      b.innerHTML = '<span class="c2-chips" title="Drag to reorder">' + [0, 1, 2, 3, 4].map(function (k) {
          return '<i' + (k === 4 ? ' class="c2-hl"' : '') + ' style="background:#' + hs[k] + '"></i>';
        }).join('') + '</span><span class="c2-pname">' +
        p[0].replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</span>';
      var mine = custom.indexOf(p) >= 0;
      if (mine) {
        b.title = 'Double-click to rename';
        b.addEventListener('dblclick', function (e) {
          if (e.target.closest('.c2-del, .c2-chips')) return;
          renamePreset(b, p[0]);
        });
      }
      if (p !== PRESETS[0]) {
        var x = document.createElement('span');
        x.className = 'c2-del';
        x.title = mine ? 'Remove this preset' : 'Hide this preset (Reset brings it back)';
        x.addEventListener('click', function (e) { e.stopPropagation(); removePreset(p[0]); });
        b.appendChild(x);
      }
      b.addEventListener('click', function () {
        if (dragged) return;
        mixerLinked = false;
        applyPreset(p[1], true);
        lastPreset = p[0];
      });
      b.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); b.click(); }
      });
      b.querySelector('.c2-chips').addEventListener('pointerdown', function (e) {
        e.preventDefault();
        dragging = b;
        dragged = false;
        b.classList.add('c2-dragging');
      });
      box.appendChild(b);
    });
    syncPresets();
  }

  // ---------- palette from an image ----------
  function kmeans(px, k) {
    // px: array of OKLab triples. Farthest-point init keeps the result deterministic.
    var cents = [px[0]];
    while (cents.length < k) {
      var bestI = 0, bestD = -1;
      for (var i = 0; i < px.length; i += 3) {
        var dmin = Infinity;
        for (var c = 0; c < cents.length; c++) dmin = Math.min(dmin, dist(px[i], cents[c]));
        if (dmin > bestD) { bestD = dmin; bestI = i; }
      }
      cents.push(px[bestI]);
    }
    var assign = new Array(px.length);
    for (var it = 0; it < 15; it++) {
      var sums = cents.map(function () { return [0, 0, 0, 0]; });
      for (var p = 0; p < px.length; p++) {
        var bi = 0, bd = Infinity;
        for (var q = 0; q < k; q++) {
          var dd = dist(px[p], cents[q]);
          if (dd < bd) { bd = dd; bi = q; }
        }
        assign[p] = bi;
        sums[bi][0] += px[p][0]; sums[bi][1] += px[p][1]; sums[bi][2] += px[p][2]; sums[bi][3]++;
      }
      cents = cents.map(function (c, q) {
        var s = sums[q];
        return s[3] ? [s[0] / s[3], s[1] / s[3], s[2] / s[3]] : c;
      });
    }
    var counts = cents.map(function () { return 0; });
    assign.forEach(function (a) { counts[a]++; });
    return cents.map(function (c, q) {
      return { lab: c, hex: rgbToHex(oklabToRgb(c)), share: counts[q] / px.length };
    }).filter(function (c) { return c.share >= 0.01; })
      .sort(function (a, b) { return b.share - a.share; });
  }
  function dist(a, b) {
    var x = a[0] - b[0], y = a[1] - b[1], z = a[2] - b[2];
    return x * x + y * y + z * z;
  }

  // Two modes: 'avg' shrinks the image to 160 px and shows cluster averages
  // (good for photos); 'exact' samples at 600 px without smoothing and lists
  // the most frequent exact colours (clean fills from diagrams).
  var lastImage = null;
  function readImage(file) {
    var url = URL.createObjectURL(file);
    var img = new Image();
    img.onload = function () {
      lastImage = img;
      var thumb = document.getElementById('c2-thumb');
      thumb.src = url;
      thumb.hidden = false;
      extractPalette();
    };
    img.src = url;
  }

  // ---------- colours from a map file ----------
  // A map dropped on the image box (CellDesigner XML, yEd GraphML with the
  // SBGN palette, or SBGN-ML with render colours) gives its colours by
  // element type: the most common protein and chemical colours, the complex
  // colour and the compartment colour are applied, and mixes of its protein
  // and chemical colours are offered as suggestions. Anything else, or a map
  // without protein or chemical colours, is ignored without a message.
  var MAP_MAX = 20 * 1024 * 1024;
  function isMapFile(f) {
    return /\.(xml|graphml|sbgn|sbgnml)$/i.test(f.name) && f.size <= MAP_MAX;
  }
  // #RRGGBBAA, ARGB (CellDesigner) or #RRGGBB, drawn on white
  function onWhite(rgb, a) {
    return rgbToHex(rgb.map(function (v) { return v * a + 255 * (1 - a); }));
  }
  function hexRGBA(h) {
    h = h.replace('#', '');
    if (h.length === 6) return onWhite(hexToRgb('#' + h), 1);
    if (h.length === 8) return onWhite(hexToRgb('#' + h.slice(0, 6)), parseInt(h.slice(6), 16) / 255);
    return null;
  }
  function hexARGB(h) {
    if (!/^[0-9a-fA-F]{8}$/.test(h)) return null;
    return onWhite(hexToRgb('#' + h.slice(2)), parseInt(h.slice(0, 2), 16) / 255);
  }
  function tally() {
    var t = { protein: {}, metabolite: {}, complex: {}, compartment: {} };
    t.add = function (role, hex) { if (role && hex) t[role][hex] = (t[role][hex] || 0) + 1; };
    return t;
  }
  function fromCellDesigner(s) {
    if (!/<sbml\b/.test(s) || s.indexOf('celldesigner') < 0) return null;
    var t = tally(), cls = {}, m;
    var spRe = /<(species|celldesigner:species)\s[^>]*?id="([^"]+)"[\s\S]*?<\/\1>/g;
    while ((m = spRe.exec(s))) {
      var c = /<celldesigner:class>([A-Z_]+)<\/celldesigner:class>/.exec(m[0]);
      if (c) cls[m[2]] = c[1];
    }
    var ROLE = { PROTEIN: 'protein', RECEPTOR: 'protein', ION_CHANNEL: 'protein', TRUNCATED: 'protein',
      SIMPLE_MOLECULE: 'metabolite', ION: 'metabolite', COMPLEX: 'complex' };
    var alRe = /<celldesigner:(speciesAlias|complexSpeciesAlias)\s[^>]*?species="([^"]+)"[\s\S]*?<\/celldesigner:\1>/g;
    while ((m = alRe.exec(s))) {
      var u = /<celldesigner:usualView>[\s\S]*?<celldesigner:paint color="([0-9a-fA-F]{8})"/.exec(m[0]);
      if (u) t.add(ROLE[cls[m[2]]], hexARGB(u[1]));
    }
    var coRe = /<celldesigner:compartmentAlias\s[\s\S]*?<\/celldesigner:compartmentAlias>/g;
    while ((m = coRe.exec(s))) {
      var p = /<celldesigner:paint color="([0-9a-fA-F]{8})"/.exec(m[0]);
      // CellDesigner draws this colour as the compartment's double border,
      // with a much paler inside
      if (p) t.add('compartment', lightMix(hexARGB(p[1]), 0.85));
    }
    return t;
  }
  function fromGraphML(s) {
    if (!/<graphml\b/.test(s) || s.indexOf('com.yworks.sbgn') < 0) return null;
    var t = tally(), m;
    var ROLE = { Macromolecule: 'protein', SimpleChemical: 'metabolite' };
    var nRe = /<y:GenericNode\b[^>]*configuration="com\.yworks\.sbgn\.(\w+)"[^>]*>([\s\S]*?)<\/y:GenericNode>/g;
    while ((m = nRe.exec(s))) {
      var f = /<y:Fill\b[^>]*color="(#[0-9a-fA-F]{6,8})"/.exec(m[2]);
      if (f) t.add(ROLE[m[1]], hexRGBA(f[1]));
    }
    var gRe = /<y:(GroupNode|GenericGroupNode)\b([^>]*)>([\s\S]*?)<\/y:\1>/g;
    while ((m = gRe.exec(s))) {
      var g = /<y:Fill\b[^>]*color="(#[0-9a-fA-F]{6,8})"/.exec(m[3]);
      if (g) t.add(/sbgn\.Complex"/.test(m[2]) ? 'complex' : 'compartment', hexRGBA(g[1]));
    }
    return t;
  }
  function fromSBGN(s) {
    if (!/<sbgn\b/.test(s) || !/renderInformation\b/.test(s)) return null;
    var doc = new DOMParser().parseFromString(s, 'application/xml');
    if (doc.getElementsByTagName('parsererror').length) return null;
    // render elements and attributes may carry a namespace prefix (ns2:fill)
    var all = function (name) { return Array.prototype.slice.call(doc.getElementsByTagNameNS('*', name)); };
    var attr = function (el, name) {
      for (var i = 0; i < el.attributes.length; i++) {
        if (el.attributes[i].localName === name) return el.attributes[i].value;
      }
      return null;
    };
    var t = tally(), colours = {}, fill = {}, border = {};
    all('colorDefinition').forEach(function (c) { colours[attr(c, 'id')] = attr(c, 'value'); });
    all('style').forEach(function (st) {
      var g = st.getElementsByTagNameNS('*', 'g')[0], v = g && attr(g, 'fill');
      if (!v) return;
      v = colours[v] || v;
      var line = attr(g, 'stroke');
      (attr(st, 'idList') || '').split(/\s+/).forEach(function (id) {
        if (!id) return;
        fill[id] = v;
        border[id] = (colours[line] || line || '').toLowerCase() === v.toLowerCase();
      });
    });
    var ROLE = { 'macromolecule': 'protein', 'macromolecule multimer': 'protein',
      'simple chemical': 'metabolite', 'simple chemical multimer': 'metabolite',
      'complex': 'complex', 'complex multimer': 'complex', 'compartment': 'compartment' };
    all('glyph').forEach(function (gl) {
      var id = gl.getAttribute('id'), v = fill[id], role = ROLE[gl.getAttribute('class')];
      if (!v || !/^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$/.test(v)) return;
      // a compartment whose fill is its border colour (maps converted from
      // CellDesigner) is drawn paler inside, as CellDesigner does
      var hex = hexRGBA(v);
      t.add(role, role === 'compartment' && border[id] ? lightMix(hex, 0.85) : hex);
    });
    return t;
  }
  function lightMix(hex, k) {
    return rgbToHex(hexToRgb(hex).map(function (v) { return v + (255 - v) * k; }));
  }
  function ranked(counts) {
    return Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a]; });
  }
  function readMapFile(file) {
    var r = new FileReader();
    r.onload = function () {
      var s = String(r.result), t = null;
      try { t = fromCellDesigner(s) || fromGraphML(s) || fromSBGN(s); } catch (e) { t = null; }
      if (!t) return;
      var P = ranked(t.protein), C = ranked(t.metabolite);
      if (!P.length && !C.length) return;
      if (P.length) theme.protein = P[0];
      if (C.length) theme.metabolite = C[0];
      if (ranked(t.complex).length) theme.complex = ranked(t.complex)[0];
      if (ranked(t.compartment).length) theme.compartment = ranked(t.compartment)[0];
      // the protein and chemical colours of the file, by how often they are used
      var n = {};
      [t.protein, t.metabolite].forEach(function (c) {
        Object.keys(c).forEach(function (h) { n[h] = (n[h] || 0) + c[h]; });
      });
      var total = Object.keys(n).reduce(function (a, h) { return a + n[h]; }, 0);
      var pool = ranked(n).map(function (h) { return { hex: h, lab: rgbToOklab(hexToRgb(h)), share: n[h] / total }; });
      // the file's own pairing first, then mixes of its colours; colours
      // close to the highlight red are left out of the mixes
      var base = [theme.compartment, theme.complex];
      var themes = [{ theme: base.concat([theme.protein, theme.metabolite]) }];
      if (pool.length > 1) {
        var mixPool = pool.filter(function (c) { return pairDistance(c.hex, theme.hlProtein) >= 5; });
        suggestThemes([{ hex: '#FFFFFF', lab: rgbToOklab([255, 255, 255]), share: 0 }].concat(mixPool)).forEach(function (sg) {
          var th = base.concat([sg.theme[2], sg.theme[3]]);
          if (!themes.some(function (o) { return o.theme.join() === th.join(); })) themes.push({ theme: th });
        });
      }
      lastImage = null;
      document.getElementById('c2-thumb').hidden = true;
      showSwatches(pool, themes.slice(0, 6));
    };
    r.readAsText(file);
  }

  function extractPalette() {
    var img = lastImage;
    if (!img) return;
    var exact = document.getElementById('c2-mode').value === 'exact';
    var s = Math.min(1, (exact ? 600 : 160) / Math.max(img.naturalWidth, img.naturalHeight));
    var w = Math.max(1, Math.round(img.naturalWidth * s)), h = Math.max(1, Math.round(img.naturalHeight * s));
    var tmp = document.createElement('canvas');
    tmp.width = w; tmp.height = h;
    var tctx = tmp.getContext('2d');
    tctx.imageSmoothingEnabled = !exact;
    tctx.drawImage(img, 0, 0, w, h);
    var d = tctx.getImageData(0, 0, w, h).data, px = [], rgb = [];
    for (var i = 0; i < d.length; i += 4) {
      if (d[i + 3] < 128) continue;
      if (exact) rgb.push(d[i] << 16 | d[i + 1] << 8 | d[i + 2]);
      else px.push(rgbToOklab([d[i], d[i + 1], d[i + 2]]));
    }
    var k = +document.getElementById('c2-k').value;
    showSwatches(exact ? exactColours(rgb, k) : kmeans(px, k));
  }

  // Exact mode: count identical pixels, then keep the most frequent colours
  // that differ visibly from those already kept. Edge and text pixels are all
  // slightly different, so each is rare and drops out; flat fills win.
  function exactColours(rgb, k) {
    var count = {};
    rgb.forEach(function (c) { count[c] = (count[c] || 0) + 1; });
    var keys = Object.keys(count).sort(function (a, b) { return count[b] - count[a]; });
    var out = [];
    for (var i = 0; i < keys.length && out.length < k; i++) {
      var share = count[keys[i]] / rgb.length;
      if (share < 0.002) break;
      var c = +keys[i], m = [c >> 16 & 255, c >> 8 & 255, c & 255], lab = rgbToOklab(m);
      var distinct = out.every(function (o) { return 100 * Math.sqrt(dist(o.lab, lab)) > 2; });
      if (distinct) out.push({ lab: lab, hex: rgbToHex(m), share: share });
    }
    return out;
  }

  var lastSwatches = [];
  function showSwatches(sw, themes) {
    lastSwatches = sw;
    var box = document.getElementById('c2-swatches');
    box.innerHTML = '';
    sw.forEach(function (s) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'c2-swatch';
      b.style.background = s.hex;
      b.style.color = s.lab[0] > 0.6 ? '#000' : '#fff';
      b.textContent = s.hex + ' · ' + (s.share < 0.01 ? '<1' : Math.round(s.share * 100)) + '%';
      b.addEventListener('click', function () {
        armed = armed === s.hex ? null : s.hex;
        Array.prototype.forEach.call(box.children, function (el) {
          el.classList.toggle('c2-armed', armed !== null && el === b);
        });
        Array.prototype.forEach.call(document.querySelectorAll('.c2-roles'), function (rb) {
          rb.classList.toggle('c2-assigning', armed !== null);
        });
      });
      box.appendChild(b);
    });
    showSuggestions(sw, themes);
  }

  // Suggestions: up to six themes built from the swatches as they are, each
  // by its own rule. All share the background (the lightest near-neutral
  // swatch); the highlight is left alone, it is set in Roles only.
  //   1 tonal:    protein muted and mid-light (lightness 0.80 to 0.90);
  //               chemical a softer, lighter partner (0.05 to 0.10 lighter,
  //               a third to four fifths of the protein's chroma, close in
  //               hue); black text on both and the protein darker come first
  //   2 contrast: chemical in another hue (60 to 150 degrees away) at
  //               similar lightness and chroma
  //   3 image:    the two most prominent colours of the image as protein and
  //               chemical, as long as text reads on them
  //   4, 5, 6     the runners-up of rules 1, 2 and 3 (a different protein)
  // Very dark swatches (lightness below 0.5) are never suggested; they stay
  // available as swatches to assign by hand. Fewer than six are shown when
  // the palette does not allow more.
  function suggestThemes(sw) {
    var chroma = function (s) { return Math.hypot(s.lab[1], s.lab[2]); };
    var hue = function (s) { return Math.atan2(s.lab[2], s.lab[1]) * 180 / Math.PI; };
    var hueGap = function (a, b) {
      if (chroma(a) < 0.008 || chroma(b) < 0.008) return null; // a neutral has no hue to speak of
      return Math.abs(((hue(a) - hue(b)) % 360 + 540) % 360 - 180);
    };
    var band = function (x, lo, hi, soft) { // 1 inside [lo, hi], falling to 0 over soft
      return x < lo ? Math.max(0, 1 - (lo - x) / soft) : x > hi ? Math.max(0, 1 - (x - hi) / soft) : 1;
    };
    var textFit = function (s) { // 0 for mid-tones, 1 when text reads easily
      var c = Math.max(contrast(s.hex, '#000000'), contrast(s.hex, '#FFFFFF'));
      return Math.max(0, Math.min(1, (c - 4.5) / 4.5));
    };
    var blackText = function (s) { return contrast(s.hex, '#000000') >= contrast(s.hex, '#FFFFFF'); };
    var muted = function (s) { return 1 - Math.min(1, Math.max(0, chroma(s) - 0.05) / 0.1); };

    var light = sw.filter(function (s) { return s.lab[0] > 0.9 && chroma(s) < 0.03; });
    var bg = (light.length ? light : sw).slice().sort(function (a, b) { return b.lab[0] - a.lab[0]; })[0];
    var rest = sw.filter(function (s) {
      return s !== bg && s.lab[0] >= 0.5 && pairDistance(s.hex, bg.hex) >= 4;
    });
    var offBg = function (s) { return Math.max(0, Math.min(1, (pairDistance(s.hex, bg.hex) - 3) / 2)); };

    var rules = [
      function tonal(p, c, d) {
        var Cp = chroma(p), gap = hueGap(p, c);
        var step = band(c.lab[0] - p.lab[0], 0.05, 0.10, 0.06);
        var tint = Cp < 0.01 ? 1 : band(chroma(c) / Cp, 0.3, 0.8, 0.4);
        var hueFit = gap === null ? 0.9 : gap <= 35 ? 1 : gap >= 60 && gap <= 150 ? 0.9 : 0.5;
        var score = (1.5 * step + tint + hueFit + Math.min(1, (d - 5) / 4) + offBg(c) +
          band(p.lab[0], 0.80, 0.90, 0.1) + muted(p)) *
          (0.7 + 0.6 * Math.sqrt(p.share) + 0.2 * Math.sqrt(c.share)) *
          (0.3 + 0.7 * textFit(p) * textFit(c));
        var tier = (blackText(p) && blackText(c) ? 0 : 2) + (p.lab[0] < c.lab[0] ? 0 : 1);
        return score - 100 * tier;
      },
      function contrasting(p, c, d) {
        var gap = hueGap(p, c);
        if (gap === null) return -1;
        var hueFit = gap < 60 ? gap / 60 : gap > 150 ? Math.max(0, 1 - (gap - 150) / 60) : 1;
        var lightFit = Math.max(0, 1 - Math.abs(p.lab[0] - c.lab[0]) / 0.15);
        var chromaFit = 1 - Math.min(1, Math.abs(chroma(p) - chroma(c)) / 0.08);
        return (2 * hueFit + lightFit + chromaFit + muted(p) + offBg(c)) *
          (0.5 + Math.sqrt(p.share) + 0.5 * Math.sqrt(c.share)) *
          (0.3 + 0.7 * textFit(p) * textFit(c));
      },
      function image(p, c, d) {
        if (textFit(p) === 0 || textFit(c) === 0) return -1;
        return (Math.sqrt(p.share) + Math.sqrt(c.share)) * (1 + Math.min(1, (d - 5) / 4)) * (0.5 + offBg(c));
      }
    ];
    rules = rules.concat(rules);

    var out = [];
    rules.forEach(function (rule) {
      if (out.length >= 6) return;
      var best = null;
      rest.forEach(function (p) {
        rest.forEach(function (c) {
          if (p === c) return;
          // each suggestion differs: no protein used before, no pair repeated
          if (out.some(function (o) { return o.p === p || (o.p === c && o.c === p); })) return;
          var d = pairDistance(p.hex, c.hex);
          if (d < 5) return;
          var score = rule(p, c, d);
          if (score > -1 && (!best || score > best.score)) best = { p: p, c: c, score: score };
        });
      });
      if (!best) return;
      out.push({ p: best.p, c: best.c, theme: [bg.hex, '#FFFFFF', best.p.hex, best.c.hex] });
    });
    return out;
  }

  function showSuggestions(sw, themes) {
    var box = document.getElementById('c2-suggest');
    box.innerHTML = '';
    (themes || suggestThemes(sw)).forEach(function (sg, n) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'c2-sugg';
      b.innerHTML = '<span class="c2-chips">' + sg.theme.map(function (h) {
        return '<i style="background:' + h + '"></i>';
      }).join('') + '</span>';
      b.addEventListener('click', function () {
        ['compartment', 'complex', 'protein', 'metabolite'].forEach(function (id, k) {
          theme[id] = sg.theme[k].toUpperCase();
        });
        Array.prototype.forEach.call(box.children, function (el) { el.classList.toggle('c2-on', el === b); });
        syncControls();
        render();
      });
      box.appendChild(b);
    });
    // the first suggestion is applied straight away, and the arrow keys
    // step through the suggestions
    if (box.firstChild) box.firstChild.click();
  }

  // ---------- arrow keys ----------
  // Down/right and up/left step through the list last clicked: the presets (the default
  // on load), one Mixer column or the image suggestions. Keys typed into a field are left alone.
  var keyGroup = null; // null = presets, otherwise a Mixer column or the suggestions
  document.getElementById('c2-presets').addEventListener('click', function () { keyGroup = null; });
  document.getElementById('c2-suggest').addEventListener('click', function (e) {
    if (e.target.closest('.c2-sugg')) keyGroup = this;
  });
  Array.prototype.forEach.call(document.querySelectorAll('.c2-mixer'), function (box) {
    box.addEventListener('click', function (e) {
      var dot = e.target.closest('.c2-dot');
      if (dot) { keyGroup = dot.closest('.c2-mixcol'); mixerLinked = true; }
    }, true); // capture: the chemical column is rebuilt by the click itself
  });
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && !e.altKey && (e.key === 'z' || e.key === 'Z')) {
      if (e.target.closest && e.target.closest('input[type=text], textarea, [contenteditable]')) return;
      e.preventDefault();
      if (e.shiftKey) stepBack(redoStack, undoStack);
      else stepBack(undoStack, redoStack);
    }
  });
  document.addEventListener('keydown', function (e) {
    var dir = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
    if (!dir) return;
    if (e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    if (e.target.closest && e.target.closest('input, select, textarea, [contenteditable]')) return;
    var items, i;
    if (keyGroup) {
      items = keyGroup.querySelectorAll('.c2-dot, .c2-sugg');
    } else {
      items = document.querySelectorAll('#c2-presets .c2-preset');
    }
    items = Array.prototype.slice.call(items);
    i = items.findIndex(function (b) { return b.classList.contains('c2-on'); });
    if (i < 0 && !keyGroup && lastPreset) {
      i = items.findIndex(function (b) { return b.getAttribute('data-name') === lastPreset; });
    }
    e.preventDefault();
    var n = items.length;
    var next = i < 0 ? (dir > 0 ? 0 : n - 1) : (i + dir + n) % n; // wraps around
    if (items[next]) items[next].click();
  });

  // ---------- wiring ----------
  buildMixer('c2-mixer');
  buildRoles(roleBox, '');
  buildPresets();
  var linked = themeFromLink();
  applyPreset(linked || PRESETS[0][1]);
  // once applied, the theme code leaves the address bar
  if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  // the map menu: each item names the map's files (data-map) and its key in
  // the address (?map=), the first map has none
  var mapMenu = document.getElementById('c2-maps');
  var mapItems = Array.prototype.slice.call(mapMenu.querySelectorAll('a'));
  var mapBase, mapName;
  function chooseMap(a) {
    mapBase = a.getAttribute('data-map');
    mapName = mapBase.split('/').pop();
    document.getElementById('c2-mapname').textContent = a.textContent;
    loadMap(mapBase + '.svg?v=' + map.getAttribute('data-v'), render);
  }
  var wanted = new URLSearchParams(location.search).get('map');
  chooseMap(mapItems.filter(function (a) { return a.getAttribute('data-key') === wanted; })[0] || mapItems[0]);
  mapItems.forEach(function (a, i) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      mapMenu.open = false;
      chooseMap(a);
      history.replaceState(null, '', location.pathname + (i ? '?map=' + a.getAttribute('data-key') : ''));
    });
  });
  document.addEventListener('click', function (e) {
    if (!mapMenu.contains(e.target)) mapMenu.open = false;
  });
  // the list opens upwards when there is no room for it below in the window
  mapMenu.addEventListener('toggle', function () {
    if (!mapMenu.open) return;
    var list = mapMenu.querySelector('.c2-list');
    mapMenu.classList.remove('c2-up');
    var r = list.getBoundingClientRect();
    if (r.bottom > window.innerHeight && mapMenu.getBoundingClientRect().top > r.height) mapMenu.classList.add('c2-up');
  });

  document.getElementById('c2-cvd').addEventListener('change', render);
  var hlBox = document.getElementById('c2-hl');
  function syncHighlight() {
    document.querySelector('.c2-wide').classList.toggle('c2-nohl', !hlBox.checked);
    render();
  }
  hlBox.addEventListener('change', syncHighlight);
  document.getElementById('c2-cxbg').addEventListener('change', function (e) {
    document.querySelector('.c2-wide').classList.toggle('c2-cxbg', e.target.checked);
    syncControls();
    render();
  });
  syncHighlight();
  function readDropped(f) {
    if (!f) return;
    if (/^image\//.test(f.type)) readImage(f);
    else if (isMapFile(f)) readMapFile(f);
  }
  document.getElementById('c2-file').addEventListener('change', function (e) {
    readDropped(e.target.files[0]);
  });
  var drop = document.getElementById('c2-drop');
  ['dragenter', 'dragover'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('c2-over'); });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('c2-over'); });
  });
  drop.addEventListener('drop', function (e) {
    readDropped(e.dataTransfer.files[0]);
  });
  // the map takes dropped files too (a hidden shortcut)
  var mapCol = document.querySelector('.c2-mapcol');
  var hasFiles = function (e) {
    return Array.prototype.indexOf.call((e.dataTransfer || {}).types || [], 'Files') >= 0;
  };
  ['dragenter', 'dragover'].forEach(function (ev) {
    mapCol.addEventListener(ev, function (e) { if (hasFiles(e)) e.preventDefault(); });
  });
  mapCol.addEventListener('drop', function (e) {
    if (!hasFiles(e)) return;
    e.preventDefault();
    readDropped(e.dataTransfer.files[0]);
  });
  document.addEventListener('paste', function (e) {
    var items = (e.clipboardData || {}).items || [];
    for (var i = 0; i < items.length; i++) {
      if (/^image\//.test(items[i].type)) { readImage(items[i].getAsFile()); break; }
    }
  });
  document.getElementById('c2-mode').addEventListener('change', extractPalette);
  document.getElementById('c2-k').addEventListener('change', extractPalette);
  document.getElementById('c2-reset-order').addEventListener('click', function () {
    try {
      localStorage.removeItem(ORDER_KEY);
      localStorage.removeItem(HIDDEN_KEY);
    } catch (e) { /* storage blocked */ }
    buildPresets();
  });
  document.getElementById('c2-swap').addEventListener('click', swapProteinChemical);
  document.getElementById('c2-light').addEventListener('input', applyLight);
  document.getElementById('c2-add').addEventListener('click', addPreset);
  document.getElementById('c2-link').addEventListener('click', copyLink);
  document.getElementById('c2-yed').addEventListener('click', function () {
    download('graphml', mapName + '-{theme}.graphml', false);
  });
  document.getElementById('c2-cd').addEventListener('click', function () {
    download('xml', mapName + '-{theme}.xml', true);
    document.getElementById('c2-cdnote').hidden = !anyWhiteText();
  });
  window.addEventListener('hashchange', function () {
    var v = themeFromLink();
    if (v) applyPreset(v);
    history.replaceState(null, '', location.pathname + location.search);
  });
  document.getElementById('c2-apply').addEventListener('click', function () {
    var v = document.getElementById('c2-export').value.trim().replace(/#/g, '');
    if (/^([0-9a-fA-F]{6}\s+){6,8}[0-9a-fA-F]{6}$/.test(v)) applyPreset(v);
  });
})();
