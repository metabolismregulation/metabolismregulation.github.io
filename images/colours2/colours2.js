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
    { id: 'page', name: 'Page background', cls: 7, L: 1, C: 0 },
    { id: 'ink', name: 'Lines and text', cls: -1, L: 0.2, C: 0.01 }
  ];

  // Themes: compartment, complex, protein, metabolite, hlProtein, white, page, ink
  var PRESETS = [
    ['Default', 'F7F6F3 FFFFFF C8D8EB DBEBDB E2ACA3 FFFFFF FFFFFF 000000'],
    ['Mushroom and teal', 'F9F6F2 FFFFFF DECEC1 BCECEB E2ACA3 FFFFFF FFFFFF 000000'],
    ['Mushroom and sky', 'F9F6F2 FFFFFF DECEC1 C5E7FB E2ACA3 FFFFFF FFFFFF 000000'],
    ['Stone and moss', 'F9F6F2 FFFFFF E3CDB5 CFEACF E2ACA3 FFFFFF FFFFFF 000000'],
    ['Stone and mist', 'F9F6F2 FFFFFF E3CDB5 CDE6F0 E2ACA3 FFFFFF FFFFFF 000000'],
    ['Stone and cornflower', 'F9F6F2 FFFFFF DACFC3 D1E2FE E2ACA3 FFFFFF FFFFFF 000000'],
    ['Clay and sage', 'F6F4EF FFFFFF E1CEB6 D3E7DE E2ACA3 FFFFFF FFFFFF 000000'],
    ['Clay and aqua', 'F6F4EF FFFFFF E1CEB6 C0EBEA E2ACA3 FFFFFF FFFFFF 000000'],
    ['Clay and sky', 'F6F4EF FFFFFF E1CEB6 C5E7FB E2ACA3 FFFFFF FFFFFF 000000'],
    ['Sand and aqua', 'F9F6F2 FFFFFF E3CDB1 C0EBEA E2ACA3 FFFFFF FFFFFF 000000'],
    ['Sand and cornflower', 'F9F6F2 FFFFFF E3CDB1 D1E2FE E2ACA3 FFFFFF FFFFFF 000000'],
    ['Sand and mist', 'F9F6F2 FFFFFF E2CEB1 CDE6F0 E2ACA3 FFFFFF FFFFFF 000000'],
    ['Linen and sky', 'F9F6F2 FFFFFF DAD0BF C5E7FB E2ACA3 FFFFFF FFFFFF 000000'],
    ['Linen and cornflower', 'F9F6F2 FFFFFF DAD0BF D1E2FE E2ACA3 FFFFFF FFFFFF 000000'],
    ['Wheat and seafoam', 'F9F6F2 FFFFFF E2CFA8 C5ECDD E2ACA3 FFFFFF FFFFFF 000000'],
    ['Wheat and cornflower', 'F9F6F2 FFFFFF E2CFA8 D1E2FE E2ACA3 FFFFFF FFFFFF 000000'],
    ['Paper and sky', 'F9F6F2 FFFFFF D3D1CA C5E7FB E2ACA3 FFFFFF FFFFFF 000000'],
    ['Paper and ink blue', 'F9F6F2 FFFFFF D3D1CA CCE4FE E2ACA3 FFFFFF FFFFFF 000000'],
    ['Grey with red accent', 'F9F6F2 FFFFFF CBD2D9 E4E1D8 E2ACA3 FFFFFF FFFFFF 000000'],
    ['Slate', 'F3F4F6 FFFFFF CDD6E0 E4E1D3 E2ACA3 FFFFFF FFFFFF 000000'],
    ['Fog and green', 'F3F7FA FFFFFF CAD2DB DBEBDB E2ACA3 FFFFFF FFFFFF 000000'],
    ['Fog and mint', 'F3F7FA FFFFFF CAD2DB C9EBD7 E2ACA3 FFFFFF FFFFFF 000000'],
    ['Arctic and oat', 'F3F8FA FFFFFF B9D6E8 E4E1D3 E2ACA3 FFFFFF FFFFFF 000000'],
    ['Arctic and green', 'F3F8FA FFFFFF B9D6E8 DBEBDB E2ACA3 FFFFFF FFFFFF 000000'],
    ['Arctic', 'F3F8FA FFFFFF B9D6E8 C9E9E4 E2ACA3 FFFFFF FFFFFF 000000'],
    ['Blue and moss', 'F7F6F3 FFFFFF C8D8EB CFEACF E2ACA3 FFFFFF FFFFFF 000000'],
    ['Ocean and oat', 'F3F8FA FFFFFF BCD3F2 E4E1D3 E2ACA3 FFFFFF FFFFFF 000000'],
    ['Ocean and moss', 'F3F8FA FFFFFF BCD3F2 CFEACF E2ACA3 FFFFFF FFFFFF 000000'],
    ['Ocean', 'F3F8FA FFFFFF BCD3F2 C0EBEA E2ACA3 FFFFFF FFFFFF 000000'],
    ['Lavender and moss', 'F7F6F9 FFFFFF D5D3EC CFEACF E2ACA3 FFFFFF FFFFFF 000000'],
    ['Lavender and mint', 'F7F6F9 FFFFFF D5D3EC D3EADF E2ACA3 FFFFFF FFFFFF 000000']
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
      var n = w * h, cls = new Uint8Array(n), t = new Uint8Array(n);
      for (var i = 0; i < n; i++) {
        cls[i] = Math.round(d[i * 4] / 32);
        t[i] = d[i * 4 + 1];
      }
      layers = { w: w, h: h, cls: cls, t: t };
      canvas.width = w; canvas.height = h;
      out = ctx.createImageData(w, h);
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
      var f = fills[cls[i]], a = t[i] / 255, b = 1 - a;
      d[j] = f[0] * a + ink[0] * b;
      d[j + 1] = f[1] * a + ink[1] * b;
      d[j + 2] = f[2] * a + ink[2] * b;
      d[j + 3] = 255;
    }
    ctx.putImageData(out, 0, 0);
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
        '<code id="c2-hex-' + r.id + '"></code>' +
        '<span class="c2-cr" id="c2-cr-' + r.id + '"></span>';
      roleBox.appendChild(row);
      var input = row.querySelector('input');
      input.addEventListener('input', function () { setRole(r.id, input.value); });
      row.addEventListener('click', function (e) {
        if (!armed || e.target === input) return;
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
      document.getElementById('c2-hex-' + r.id).textContent = theme[r.id];
      var cr = document.getElementById('c2-cr-' + r.id);
      if (r.id === 'ink' || r.id === 'page') { cr.textContent = ''; return; }
      var v = contrast(theme[r.id], theme.ink);
      cr.textContent = v.toFixed(1) + ':1';
      cr.className = 'c2-cr' + (v < 7 ? ' c2-low' : '');
      cr.title = 'Contrast of text on this fill (WCAG). Below 7:1 reads poorly at small sizes.';
    });
    document.getElementById('c2-export').value = exportText();
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

  // Auto-assign: the three most chromatic, well separated hues go to protein,
  // simple chemical and highlight (the reddest of the three); the most common
  // near-neutral colour tints the compartment.
  function autoAssign() {
    var sw = lastSwatches.slice();
    if (!sw.length) return;
    var chroma = function (s) { return Math.hypot(s.lab[1], s.lab[2]); };
    var hue = function (s) { return Math.atan2(s.lab[2], s.lab[1]); };
    var picks = [];
    sw.filter(function (s) { return chroma(s) > 0.02; })
      .sort(function (a, b) { return chroma(b) * Math.sqrt(b.share) - chroma(a) * Math.sqrt(a.share); })
      .forEach(function (s) {
        if (picks.length >= 3) return;
        var far = picks.every(function (p) {
          var dh = Math.abs(hue(p) - hue(s));
          return Math.min(dh, 2 * Math.PI - dh) > 0.6;
        });
        if (far) picks.push(s);
      });
    while (picks.length < 3) picks.push(sw[picks.length % sw.length]);
    // red-orange hue sits around 0.5 rad in OKLab
    var redIdx = 0, redD = Infinity;
    picks.forEach(function (p, i) {
      var dh = Math.abs(hue(p) - 0.5);
      dh = Math.min(dh, 2 * Math.PI - dh);
      if (dh < redD) { redD = dh; redIdx = i; }
    });
    var hl = picks.splice(redIdx, 1)[0];
    var role = function (id) { return ROLES.filter(function (r) { return r.id === id; })[0]; };
    theme.protein = pastelise(picks[0].hex, role('protein'));
    theme.metabolite = pastelise(picks[1].hex, role('metabolite'));
    theme.hlProtein = pastelise(hl.hex, role('hlProtein'));
    theme.complex = '#FFFFFF';
    var neutral = sw.filter(function (s) { return chroma(s) < 0.04; })[0] || sw[0];
    theme.compartment = pastelise(neutral.hex, role('compartment'));
    syncControls();
    render();
  }

  // ---------- wiring ----------
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
    if (/^([0-9a-fA-F]{6}\s+){7}[0-9a-fA-F]{6}$/.test(v)) applyPreset(v);
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
