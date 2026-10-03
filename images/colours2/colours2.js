// Colour theme playground for the iNOS map.
// F007-inos-layers.png stores, per pixel of F007-inos.png:
//   R = fill class * 32, G = fill share t (0..255); the rest is ink.
// A pixel is redrawn as t * fill[class] + (1 - t) * ink.
(function () {
  'use strict';

  var ROLES = [
    { id: 'compartment', name: 'Compartment', cls: 0, L: 0.975, C: 0.008 },
    { id: 'complex', name: 'Complex', cls: 3, L: 0.99, C: 0.012 },
    { id: 'protein', name: 'Protein (macromolecule)', cls: 2, L: 0.87, C: 0.05 },
    { id: 'metabolite', name: 'Simple chemical', cls: 4, L: 0.91, C: 0.05 },
    { id: 'hlProtein', name: 'Highlighted protein', cls: 6, L: 0.80, C: 0.08, hl: true },
    { id: 'white', name: 'Process, gene, mRNA, labels', cls: 1, L: 1, C: 0 },
    { id: 'ink', name: 'Lines and text', cls: -1, L: 0.2, C: 0.01 }
  ];

  // Themes: compartment, complex, protein, metabolite, hlProtein, white, ink
  var PRESETS = [
    ['Default', 'F7F6F3 FFFFFF C8D8EB DBEBDB E2ACA3 FFFFFF 000000'],
    ['Ocean', 'F3F4F6 FFFFFF BCD3F2 C0EBEA E2ACA3 FFFFFF 000000'],
    ['Paper and ink blue', 'F7F6F3 FFFFFF D3D1CA CCE4FE E2ACA3 FFFFFF 000000'],
    ['Mushroom and green', 'F9F6F2 FFFFFF DECEC1 DBEBDB E2ACA3 FFFFFF 000000'],
    ['Linen and teal', 'F6F4EF FFFFFF DAD0BF CFE4DF E2ACA3 FFFFFF 000000'],
    ['Linen and mist', 'F7F6F3 FFFFFF DAD0BF CDE6F0 E2ACA3 FFFFFF 000000'],
    ['Ocean and green', 'F9F6F2 FFFFFF BCD3F2 DBEBDB E2ACA3 FFFFFF 000000'],
    ['Blue and silver', 'F3F4F6 FFFFFF C8D8EB E8E6E2 E2ACA3 FFFFFF 000000'],
    ['Sage and pearl', 'F7F6F3 FFFFFF C7DDCA EFEDE7 E2ACA3 FFFFFF 000000'],
    ['Ocean and silver', 'F3F4F6 FFFFFF BCD3F2 E8E6E2 E2ACA3 FFFFFF 000000'],
    ['Slate and pearl', 'F3F4F6 FFFFFF CDD6E0 EFEDE7 E2ACA3 FFFFFF 000000']
  ];

  // Machado et al. 2009, severity 1.0, applied in linear RGB
  var CVD = {
    none: null,
    deuteranopia: [0.367322, 0.860646, -0.227968, 0.280085, 0.672501, 0.047413, -0.01182, 0.04294, 0.968881],
    protanopia: [0.152286, 1.052583, -0.204868, 0.114503, 0.786281, 0.099216, -0.003882, -0.048116, 1.051998],
    tritanopia: [1.255528, -0.076749, -0.178779, -0.078411, 0.930809, 0.147602, 0.004733, 0.691367, 0.3039]
  };

  var theme = {};
  var armed = null; // swatch picked from an image, waiting to be assigned
  var layers = null; // { w, h, cls: Uint8Array, t: Uint8Array }
  var canvas = document.getElementById('c2-map');
  var ctx = canvas.getContext('2d');
  var out = null;

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

  // Keep the hue of a colour, move it to a fixed lightness and cap its chroma,
  // so black text stays readable on it whatever the source image looked like.
  function pastelise(hex, role) {
    var o = rgbToOklab(hexToRgb(hex));
    var C = Math.hypot(o[1], o[2]);
    var hue = Math.atan2(o[2], o[1]);
    var c = Math.min(C, role.C);
    var lab = [role.L, c * Math.cos(hue), c * Math.sin(hue)];
    while (!inGamut(lab) && c > 0) {
      c -= 0.002;
      lab = [role.L, c * Math.cos(hue), c * Math.sin(hue)];
    }
    return rgbToHex(oklabToRgb(lab));
  }

  function luminance(c) { return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]); }
  function contrast(a, b) {
    var la = luminance(hexToRgb(a)), lb = luminance(hexToRgb(b));
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
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
  function loadLayers(src, done) {
    var img = new Image();
    img.onload = function () {
      var w = img.naturalWidth, h = img.naturalHeight;
      var tmp = document.createElement('canvas');
      tmp.width = w; tmp.height = h;
      var tctx = tmp.getContext('2d');
      tctx.drawImage(img, 0, 0);
      var d = tctx.getImageData(0, 0, w, h).data;
      // Crop the white page margin (class 7) so only the map is shown
      var x0 = w, y0 = h, x1 = -1, y1 = -1, x, y, k;
      for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
          k = (y * w + x) * 4;
          // pure margin: page class with no ink in it
          if (Math.round(d[k] / 32) === 7 && d[k + 1] > 250) continue;
          if (x < x0) x0 = x;
          if (x > x1) x1 = x;
          if (y < y0) y0 = y;
          if (y > y1) y1 = y;
        }
      }
      var cw = x1 - x0 + 1, ch = y1 - y0 + 1;
      var cls = new Uint8Array(cw * ch), t = new Uint8Array(cw * ch);
      for (y = 0; y < ch; y++) {
        for (x = 0; x < cw; x++) {
          k = ((y + y0) * w + x + x0) * 4;
          cls[y * cw + x] = Math.round(d[k] / 32);
          t[y * cw + x] = d[k + 1];
        }
      }
      layers = { w: cw, h: ch, cls: cls, t: t };
      canvas.width = cw; canvas.height = ch;
      out = ctx.createImageData(cw, ch);
      done();
    };
    img.src = src;
  }

  function render() {
    if (!layers) return;
    var mode = document.getElementById('c2-cvd').value;
    var fills = [];
    ROLES.forEach(function (r) {
      if (r.cls >= 0) fills[r.cls] = simulate(hexToRgb(theme[r.id]), mode);
    });
    // Highlight off: highlighted elements are drawn like ordinary ones
    if (!document.getElementById('c2-hl').checked) fills[6] = fills[2];
    // A highlighted complex is always drawn like any other complex
    fills[5] = fills[3];
    var ink = simulate(hexToRgb(theme.ink), mode);
    var d = out.data, cls = layers.cls, t = layers.t, n = layers.w * layers.h;
    for (var i = 0, j = 0; i < n; i++, j += 4) {
      var a = t[i] / 255, b = 1 - a;
      if (cls[i] === 7) {
        // margin left at the rounded outer corners: transparent, keeping the ink edge
        d[j] = ink[0]; d[j + 1] = ink[1]; d[j + 2] = ink[2];
        d[j + 3] = 255 * b;
        continue;
      }
      var f = fills[cls[i]];
      d[j] = f[0] * a + ink[0] * b;
      d[j + 1] = f[1] * a + ink[1] * b;
      d[j + 2] = f[2] * a + ink[2] * b;
      d[j + 3] = 255;
    }
    ctx.putImageData(out, 0, 0);
  }

  // ---------- mixer ----------
  // Named colours from the presets; pick one per column to build a theme.
  var MIX = [
    { role: 'compartment', title: 'Background', items: [
      ['Paper', 'F7F6F3'], ['Shade', 'F3F0EA'], ['Linen', 'F9F6F2'], ['Clay', 'F6F4EF'],
      ['Slate', 'F3F4F6'], ['Fog', 'F3F7FA'], ['Grey', 'F2F2F2']] },
    { role: 'protein', title: 'Protein', items: [
      ['Mushroom', 'DECEC1'], ['Stone', 'E3CDB5'], ['Putty', 'DACFC3'], ['Clay', 'E1CEB6'],
      ['Sand', 'E3CDB1'], ['Linen', 'DAD0BF'], ['Paper', 'D3D1CA'], ['Grey', 'CBD2D9'],
      ['Slate', 'CDD6E0'], ['Fog', 'CAD2DB'], ['Powder', 'B3CDE3'], ['Blue', 'C8D8EB'],
      ['Ocean', 'BCD3F2']] },
    { role: 'metabolite', title: 'Chemical', generated: true }
  ];

  // Chemicals are calculated from the chosen protein: eleven hues on the
  // OKLCH wheel from +80 through 180 to -80 degrees from the protein's hue in
  // 20-degree steps (hues within 60 degrees of the protein are left out), one
  // lightness step (+0.04) above the protein, colour strength 90% of the protein's.
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
    var L = Math.min(p.L + 0.04, 0.955), C = 0.9 * Math.min(Math.max(p.C, 0.025), 0.045);
    return CHEM_OFFSETS.map(function (off) {
      var h = Math.round((p.h + off + 360) % 360);
      var name = CHEM_NAMES.filter(function (n) { return h <= n[0]; })[0][1];
      var sign = off > 0 && off < 180 ? '+' : off < 0 ? '\u2212' : '';
      return { off: off, h: h, name: name + ' ' + sign + Math.abs(off) + '\u00B0', hex: lchHex(L, C, h) };
    });
  }
  var chemSlot = null; // offset of the chosen chemical; null when it is not from the list
  var CLOSE = 4.5; // OKLab distance x100 below which protein and chemical are hard to tell apart

  function oklabDist(a, b, mode) {
    var x = rgbToOklab(simulate(hexToRgb(a), mode)), y = rgbToOklab(simulate(hexToRgb(b), mode));
    return 100 * Math.sqrt(dist(x, y));
  }
  function pairDistance(a, b) {
    return Math.min(oklabDist(a, b, 'none'), oklabDist(a, b, 'deuteranopia'));
  }

  function buildMixer() {
    var box = document.getElementById('c2-mixer');
    MIX.forEach(function (col) {
      var c = document.createElement('div');
      c.className = 'c2-mixcol';
      c.innerHTML = '<div class="c2-mixtitle">' + col.title + '</div>';
      if (col.generated) {
        c.id = 'c2-chemcol';
        box.appendChild(c);
        return;
      }
      col.items.forEach(function (it) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'c2-dot';
        b.setAttribute('data-role', col.role);
        b.setAttribute('data-hex', '#' + it[1]);
        b.title = it[0] + ' #' + it[1];
        b.innerHTML = '<i style="background:#' + it[1] + '"></i>' + it[0];
        b.addEventListener('click', function () {
          // a new protein brings the chosen chemical along, recalculated for it
          // the chemical keeps its offset when the protein changes; 180 degrees
          // when no chemical from the list was chosen yet
          if (col.role === 'protein') {
            var off = chemSlot !== null ? chemSlot : 180;
            theme.metabolite = chemOptions('#' + it[1]).filter(function (o) { return o.off === off; })[0].hex;
          }
          setRole(col.role, '#' + it[1]);
        });
        c.appendChild(b);
      });
      box.appendChild(c);
    });
  }

  function syncMixer() {
    var names = {};
    Array.prototype.forEach.call(document.querySelectorAll('.c2-dot'), function (b) {
      var role = b.getAttribute('data-role'), hex = b.getAttribute('data-hex');
      var on = theme[role] === hex;
      b.classList.toggle('c2-on', on);
      if (on) names[role] = b.textContent;
    });
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
      if (theme.metabolite === o.hex) { b.classList.add('c2-on'); match = o; }
      b.addEventListener('click', function () {
        chemSlot = o.off;
        setRole('metabolite', o.hex);
      });
      col.appendChild(b);
    });
    chemSlot = match ? match.off : null;
    if (match) names.metabolite = match.name;
    var label = (names.compartment || 'custom') + ' background, ' +
      (names.protein || 'custom') + ' and ' + (names.metabolite || 'custom');
    var near = pairDistance(theme.protein, theme.metabolite) < CLOSE;
    var el = document.getElementById('c2-mixname');
    el.textContent = label + (near ? ' (protein and chemical too close)' : '');
    el.classList.toggle('c2-low', near);
  }

  // ---------- controls ----------
  var roleBox = document.getElementById('c2-roles');

  function buildRoles() {
    ROLES.forEach(function (r) {
      var row = document.createElement('div');
      row.className = 'c2-role' + (r.hl ? ' c2-hl' : '');
      row.innerHTML =
        '<input type="color" id="c2-in-' + r.id + '">' +
        '<span class="c2-role-name">' + r.name + '</span>' +
        '<input type="text" class="c2-hexin" id="c2-hex-' + r.id + '" maxlength="7" spellcheck="false">' +
        '<span class="c2-cr" id="c2-cr-' + r.id + '"></span>';
      roleBox.appendChild(row);
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
        var keep = document.getElementById('c2-raw').checked;
        setRole(r.id, keep ? armed : pastelise(armed, r));
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

  function syncControls() {
    ROLES.forEach(function (r) {
      document.getElementById('c2-in-' + r.id).value = theme[r.id].toLowerCase();
      var hx = document.getElementById('c2-hex-' + r.id);
      if (document.activeElement !== hx) hx.value = theme[r.id];
      var cr = document.getElementById('c2-cr-' + r.id);
      if (r.id === 'ink') { cr.textContent = ''; return; }
      var v = contrast(theme[r.id], theme.ink);
      cr.textContent = v.toFixed(1) + ':1';
      cr.className = 'c2-cr' + (v < 7 ? ' c2-low' : '');
      cr.title = 'Contrast of text on this fill (WCAG). Below 7:1 reads poorly at small sizes.';
    });
    document.getElementById('c2-export').value = exportText();
    syncMixer();
  }

  function applyPreset(str) {
    var hs = str.split(/\s+/);
    ROLES.forEach(function (r, i) { theme[r.id] = '#' + hs[i]; });
    syncControls();
    render();
  }

  function exportText() {
    return ROLES.map(function (r) { return theme[r.id].slice(1); }).join(' ');
  }

  // Preset order can be rearranged by dragging the handle; the order is kept
  // in this browser only. Reset order returns to the order in PRESETS.
  var ORDER_KEY = 'colours.presetOrder';
  var dragging = null, dragged = false;

  function loadOrder() {
    try { return JSON.parse(localStorage.getItem(ORDER_KEY)) || []; } catch (e) { return []; }
  }
  function saveOrder() {
    var names = Array.prototype.map.call(document.querySelectorAll('.c2-preset'), function (el) {
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

  function buildPresets() {
    var box = document.getElementById('c2-presets');
    box.innerHTML = '';
    var saved = loadOrder();
    var rank = function (p) {
      var i = saved.indexOf(p[0]);
      return i < 0 ? saved.length + PRESETS.indexOf(p) : i;
    };
    PRESETS.slice().sort(function (x, y) { return rank(x) - rank(y); }).forEach(function (p) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'c2-preset';
      b.setAttribute('data-name', p[0]);
      var hs = p[1].split(' ');
      b.innerHTML = '<span class="c2-handle" title="Drag to reorder">&#8942;&#8942;</span>' +
        '<span class="c2-chips">' + [0, 1, 2, 3, 4].map(function (k) {
          return '<i' + (k === 4 ? ' class="c2-hl"' : '') + ' style="background:#' + hs[k] + '"></i>';
        }).join('') + '</span>' + p[0];
      b.addEventListener('click', function () {
        if (dragged) return;
        applyPreset(p[1]);
      });
      var handle = b.querySelector('.c2-handle');
      handle.addEventListener('pointerdown', function (e) {
        e.preventDefault();
        dragging = b;
        dragged = false;
        b.classList.add('c2-dragging');
      });
      box.appendChild(b);
    });
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

  function readImage(file) {
    var url = URL.createObjectURL(file);
    var img = new Image();
    img.onload = function () {
      var s = Math.min(1, 160 / Math.max(img.naturalWidth, img.naturalHeight));
      var w = Math.max(1, Math.round(img.naturalWidth * s)), h = Math.max(1, Math.round(img.naturalHeight * s));
      var tmp = document.createElement('canvas');
      tmp.width = w; tmp.height = h;
      var tctx = tmp.getContext('2d');
      tctx.drawImage(img, 0, 0, w, h);
      var d = tctx.getImageData(0, 0, w, h).data, px = [];
      for (var i = 0; i < d.length; i += 4) {
        if (d[i + 3] < 128) continue;
        px.push(rgbToOklab([d[i], d[i + 1], d[i + 2]]));
      }
      var thumb = document.getElementById('c2-thumb');
      thumb.src = url;
      thumb.hidden = false;
      showSwatches(kmeans(px, +document.getElementById('c2-k').value));
    };
    img.src = url;
  }

  var lastSwatches = [];
  function showSwatches(sw) {
    lastSwatches = sw;
    var box = document.getElementById('c2-swatches');
    box.innerHTML = '';
    sw.forEach(function (s) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'c2-swatch';
      b.style.background = s.hex;
      b.style.color = s.lab[0] > 0.6 ? '#000' : '#fff';
      b.textContent = s.hex + ' · ' + Math.round(s.share * 100) + '%';
      b.addEventListener('click', function () {
        armed = armed === s.hex ? null : s.hex;
        Array.prototype.forEach.call(box.children, function (el) {
          el.classList.toggle('c2-armed', armed !== null && el === b);
        });
        roleBox.classList.toggle('c2-assigning', armed !== null);
      });
      box.appendChild(b);
    });
    document.getElementById('c2-auto').disabled = sw.length === 0;
  }

  // Auto-assign: the protein takes the most colourful prominent swatch. The
  // chemical is then chosen among all other swatches, each tried at a few
  // lightness steps after softening, keeping the one that stays furthest from
  // the protein in normal and deuteranopia vision without fading into the
  // compartment. The highlight colour is left as it is.
  function autoAssign() {
    var sw = lastSwatches.slice();
    if (!sw.length) return;
    var chroma = function (s) { return Math.hypot(s.lab[1], s.lab[2]); };
    var role = function (id) { return ROLES.filter(function (r) { return r.id === id; })[0]; };

    var neutral = sw.filter(function (s) { return chroma(s) < 0.04; })[0] || sw[0];
    var compartment = pastelise(neutral.hex, role('compartment'));

    var ranked = sw.slice().sort(function (a, b) {
      return chroma(b) * Math.sqrt(b.share) - chroma(a) * Math.sqrt(a.share);
    });
    var proteinSw = ranked[0];
    var protein = pastelise(proteinSw.hex, role('protein'));

    var chemRole = role('metabolite');
    var best = null;
    sw.forEach(function (s) {
      if (s === proteinSw) return;
      [0.90, 0.92, 0.94].forEach(function (L) {
        var hex = pastelise(s.hex, { L: L, C: chemRole.C });
        if (pairDistance(hex, compartment) < 4) return;
        // separation first; a small bonus for colours that matter in the image
        var score = pairDistance(protein, hex) + 2 * Math.sqrt(s.share);
        if (!best || score > best.score) best = { score: score, hex: hex };
      });
    });

    theme.compartment = compartment;
    theme.complex = '#FFFFFF';
    theme.protein = protein;
    if (best) theme.metabolite = best.hex;
    syncControls();
    render();
  }

  // ---------- wiring ----------
  buildMixer();
  buildRoles();
  buildPresets();
  applyPreset(PRESETS[0][1]);
  loadLayers(document.getElementById('c2-map').getAttribute('data-layers'), render);

  document.getElementById('c2-cvd').addEventListener('change', render);
  var hlBox = document.getElementById('c2-hl');
  function syncHighlight() {
    document.querySelector('.c2-wide').classList.toggle('c2-nohl', !hlBox.checked);
    render();
  }
  hlBox.addEventListener('change', syncHighlight);
  syncHighlight();
  document.getElementById('c2-file').addEventListener('change', function (e) {
    if (e.target.files[0]) readImage(e.target.files[0]);
  });
  var drop = document.getElementById('c2-drop');
  ['dragenter', 'dragover'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('c2-over'); });
  });
  ['dragleave', 'drop'].forEach(function (ev) {
    drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('c2-over'); });
  });
  drop.addEventListener('drop', function (e) {
    var f = e.dataTransfer.files[0];
    if (f && /^image\//.test(f.type)) readImage(f);
  });
  document.addEventListener('paste', function (e) {
    var items = (e.clipboardData || {}).items || [];
    for (var i = 0; i < items.length; i++) {
      if (/^image\//.test(items[i].type)) { readImage(items[i].getAsFile()); break; }
    }
  });
  document.getElementById('c2-auto').addEventListener('click', autoAssign);
  document.getElementById('c2-reset-order').addEventListener('click', function () {
    try { localStorage.removeItem(ORDER_KEY); } catch (e) { /* storage blocked */ }
    buildPresets();
  });
  document.getElementById('c2-apply').addEventListener('click', function () {
    var v = document.getElementById('c2-export').value.trim().replace(/#/g, '');
    if (/^([0-9a-fA-F]{6}\s+){6}[0-9a-fA-F]{6}$/.test(v)) applyPreset(v);
  });
  document.getElementById('c2-download').addEventListener('click', function () {
    canvas.toBlob(function (blob) {
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'F007-inos-' + exportText().split(' ').slice(0, 4).join('-') + '.png';
      a.click();
    });
  });
})();
