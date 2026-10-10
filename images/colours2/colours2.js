// Colour theme playground for the iNOS map.
// F007-inos-layers.png stores, per pixel of F007-inos.png:
//   R = fill class * 32, G = fill share t (0..255); the rest is ink.
//   B = 255 where that ink is text, 0 where it is a line or border.
// A pixel is redrawn as t * fill[class] + (1 - t) * ink, ink being the
// text or the line colour.
(function () {
  'use strict';

  var ROLES = [
    { id: 'compartment', name: 'Compartment', cls: 0 },
    { id: 'complex', name: 'Complex', cls: 3 },
    { id: 'protein', name: 'Protein', cls: 2 },
    { id: 'metabolite', name: 'Simple chemical', cls: 4 },
    { id: 'hlProtein', name: 'Highlighted protein', cls: 6, hl: true },
    { id: 'white', name: 'Process, gene, mRNA, labels', cls: 1 },
    { id: 'ink', name: 'Lines', cls: -1 },
    { id: 'text', name: 'Text', cls: -1 }
  ];

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

  function luminance(c) { return 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]); }
  function contrast(a, b) {
    var la = luminance(hexToRgb(a)), lb = luminance(hexToRgb(b));
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }
  // Text on a fill: the Text colour, or white where white reads better
  // (dark fills)
  function textOn(fill) {
    return contrast('#FFFFFF', fill) > contrast(theme.text, fill) ? '#FFFFFF' : theme.text;
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
      var cls = new Uint8Array(cw * ch), t = new Uint8Array(cw * ch), txt = new Uint8Array(cw * ch);
      for (y = 0; y < ch; y++) {
        for (x = 0; x < cw; x++) {
          k = ((y + y0) * w + x + x0) * 4;
          cls[y * cw + x] = Math.round(d[k] / 32);
          t[y * cw + x] = d[k + 1];
          txt[y * cw + x] = d[k + 2] > 127 ? 1 : 0;
        }
      }
      layers = { w: cw, h: ch, cls: cls, t: t, txt: txt };
      canvas.width = cw; canvas.height = ch;
      out = ctx.createImageData(cw, ch);
      done();
    };
    img.src = src;
  }

  function render() {
    if (!layers) return;
    var mode = document.getElementById('c2-cvd').value;
    var hex = [];
    ROLES.forEach(function (r) { if (r.cls >= 0) hex[r.cls] = theme[r.id]; });
    // Highlight off: highlighted elements are drawn like ordinary ones
    if (!document.getElementById('c2-hl').checked) hex[6] = hex[2];
    // "Complex transparent": complexes take the compartment colour;
    // a highlighted complex is always drawn like any other complex
    if (document.getElementById('c2-cxbg').checked) hex[3] = hex[0];
    hex[5] = hex[3];
    var fills = [], texts = [];
    hex.forEach(function (h, k) {
      fills[k] = simulate(hexToRgb(h), mode);
      texts[k] = simulate(hexToRgb(textOn(h)), mode);
    });
    var line = simulate(hexToRgb(theme.ink), mode), text = simulate(hexToRgb(theme.text), mode);
    var d = out.data, cls = layers.cls, t = layers.t, txt = layers.txt, n = layers.w * layers.h;
    for (var i = 0, j = 0; i < n; i++, j += 4) {
      var a = t[i] / 255, b = 1 - a;
      var ink = !txt[i] ? line : cls[i] === 7 ? text : texts[cls[i]];
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
  // Chemical column: a fixed list (false), or the backup that calculates
  // chemicals from the chosen protein by hue angle (true).
  var CHEM_FROM_ANGLE = false;
  // Named colours from the presets; pick one per column to build a theme.
  var MIX = [
    { role: 'compartment', title: 'Background', items: [
      // warm to cool (OKLab b, yellow to blue)
      ['Shell', 'FBFAF6'], ['Paper', 'F7F6F3'], ['Chalk', 'F8F8F8'],
      ['Mist', 'F6F7F9'], ['Slate', 'F3F4F6']] },
    { role: 'protein', title: 'Protein', items: [
      // OKLCH lightness 0.865, hue 85 to 255 degrees in ~20 degree steps,
      // chroma 0.033 to 0.042; Paper (0.012) as a near-neutral
      ['Linen', 'DDD1BA'], ['Paper', 'D4D3CA'], ['Lichen', 'D1D6BD'], ['Pistachio', 'C9D8C1'],
      ['Sage', 'C1DAC8'], ['Celadon', 'BBDBD1'], ['Sea', 'B8DADA'], ['Haze', 'B8D9E2'],
      ['Powder', 'BBD7E9'], ['Blue', 'C1D5EE']] },
    CHEM_FROM_ANGLE ? { role: 'metabolite', title: 'Chemical', generated: true } :
    { role: 'metabolite', title: 'Chemical', items: [
      // the protein hues again, lighter and softer: OKLCH lightness 0.93,
      // chroma about 0.6 of the protein column's; Pearl and Silver as in
      // the presets
      ['Sand', 'EFE7D8'], ['Pearl', 'EFEDE7'], ['Silver', 'E8E6E2'], ['Willow', 'E8E8DE'],
      ['Celery', 'E4EBDB'], ['Mint', 'DDEDE0'], ['Seafoam', 'D8EDE7'], ['Aqua', 'D6EDEE'],
      ['Mist', 'D8ECF4'], ['Sky', 'DBEAF9']] }
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
          if (CHEM_FROM_ANGLE && col.role === 'protein') {
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
    ROLES.forEach(function (r) {
      document.getElementById('c2-in-' + r.id).value = theme[r.id].toLowerCase();
      var hx = document.getElementById('c2-hex-' + r.id);
      if (document.activeElement !== hx) hx.value = theme[r.id];
      var cr = document.getElementById('c2-cr-' + r.id);
      if (r.cls < 0) { cr.textContent = ''; return; }
      var white = textOn(theme[r.id]) === '#FFFFFF' && theme.text !== '#FFFFFF';
      var v = contrast(theme[r.id], textOn(theme[r.id]));
      cr.textContent = v.toFixed(1) + ':1' + (white ? ' w' : '');
      cr.className = 'c2-cr' + (v < 7 ? ' c2-low' : '');
      cr.title = 'Contrast of text on this fill (WCAG). Below 7:1 reads poorly at small sizes.' +
        (white ? ' w: this fill is dark, so its text is drawn white.' : '');
    });
    document.getElementById('c2-export').value = exportText();
    syncMixer();
    syncPresets();
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

  // Theme code: 7 colours, or 8 when text differs from lines. A 7-colour
  // code (all presets) draws text in the line colour.
  // keepHl: leave the highlight as set in Roles (presets); a pasted theme
  // code sets it too.
  function applyPreset(str, keepHl) {
    var hs = str.split(/\s+/);
    if (hs.length < 8) hs[7] = hs[6];
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
    if (hs[7] === hs[6]) hs.pop();
    return hs.join(' ');
  }
  function exportText() {
    return themeCode(document.getElementById('c2-cxbg').checked);
  }

  // Preset order can be rearranged by dragging the handle; the order is kept
  // in this browser only. Reset order returns to the order in PRESETS.
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
  var COLOUR_NAMES = [
    ['Rose', 'E8C4C4'], ['Blush', 'F2E1DC'], ['Peach', 'F2D2BC'], ['Apricot', 'EFC8A8'], ['Taupe', 'DBCCC7'],
    ['Mushroom', 'DECEC1'], ['Sand', 'EFE7D8'], ['Linen', 'DDD1BA'], ['Ochre', 'E3C77A'], ['Straw', 'EDE3B8'],
    ['Stone', 'D9D2C7'], ['Paper', 'D4D3CA'], ['Pearl', 'EFEDE7'], ['Silver', 'E8E6E2'], ['Ash', 'C4C8C1'],
    ['Lichen', 'D1D6BD'], ['Celery', 'E4EBDB'], ['Moss', 'BFC7B8'], ['Pistachio', 'C9D8C1'], ['Sage', 'C1DAC8'],
    ['Mint', 'DDEDE0'], ['Celadon', 'BBDBD1'], ['Seafoam', 'D8EDE7'], ['Sea', 'B8DADA'], ['Aqua', 'D6EDEE'],
    ['Haze', 'B8D9E2'], ['Mist', 'D8ECF4'], ['Powder', 'BBD7E9'], ['Steel', 'BFCFD9'], ['Blue', 'C1D5EE'],
    ['Sky', 'DBEAF9'], ['Ocean', 'BCD3F2'], ['Dusk', 'C5CADD'], ['Periwinkle', 'E2E7F7'], ['Lavender', 'D9D0E6'],
    ['Lilac', 'E6D6E6'], ['Grey', 'D6D6D6']];
  function colourName(hex) {
    var o = rgbToOklab(hexToRgb(hex)), best = null;
    COLOUR_NAMES.forEach(function (n) {
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
  function removePreset(name) {
    saveCustom(loadCustom().filter(function (p) { return p[0] !== name; }));
    buildPresets();
  }

  function buildPresets() {
    var box = document.getElementById('c2-presets');
    box.innerHTML = '';
    var saved = loadOrder();
    var custom = loadCustom();
    var all = PRESETS.concat(custom);
    var rank = function (p) {
      var i = saved.indexOf(p[0]);
      return i < 0 ? saved.length + all.indexOf(p) : i;
    };
    all.slice().sort(function (x, y) { return rank(x) - rank(y); }).forEach(function (p) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'c2-preset';
      b.setAttribute('data-name', p[0]);
      b.setAttribute('data-theme', p[1].toUpperCase());
      var hs = p[1].split(' ');
      b.innerHTML = '<span class="c2-handle" title="Drag to reorder">&#8942;&#8942;</span>' +
        '<span class="c2-chips">' + [0, 1, 2, 3, 4].map(function (k) {
          return '<i' + (k === 4 ? ' class="c2-hl"' : '') + ' style="background:#' + hs[k] + '"></i>';
        }).join('') + '</span>' + p[0];
      if (custom.indexOf(p) >= 0) {
        var x = document.createElement('span');
        x.className = 'c2-del';
        x.title = 'Remove this preset';
        x.innerHTML = '&times;';
        x.addEventListener('click', function (e) { e.stopPropagation(); removePreset(p[0]); });
        b.appendChild(x);
      }
      b.addEventListener('click', function () {
        if (dragged) return;
        mixerLinked = false;
        applyPreset(p[1], true);
        lastPreset = p[0];
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
      b.textContent = s.hex + ' · ' + (s.share < 0.01 ? '<1' : Math.round(s.share * 100)) + '%';
      b.addEventListener('click', function () {
        armed = armed === s.hex ? null : s.hex;
        Array.prototype.forEach.call(box.children, function (el) {
          el.classList.toggle('c2-armed', armed !== null && el === b);
        });
        roleBox.classList.toggle('c2-assigning', armed !== null);
      });
      box.appendChild(b);
    });
    showSuggestions(sw);
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

  function showSuggestions(sw) {
    var box = document.getElementById('c2-suggest');
    box.innerHTML = '';
    suggestThemes(sw).forEach(function (sg, n) {
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
  document.getElementById('c2-mixer').addEventListener('click', function (e) {
    var dot = e.target.closest('.c2-dot');
    if (dot) { keyGroup = dot.closest('.c2-mixcol'); mixerLinked = true; }
  }, true); // capture: the chemical column is rebuilt by the click itself
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
  document.getElementById('c2-cxbg').addEventListener('change', function (e) {
    document.querySelector('.c2-wide').classList.toggle('c2-cxbg', e.target.checked);
    syncControls();
    render();
  });
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
  document.getElementById('c2-mode').addEventListener('change', extractPalette);
  document.getElementById('c2-k').addEventListener('change', extractPalette);
  document.getElementById('c2-reset-order').addEventListener('click', function () {
    try { localStorage.removeItem(ORDER_KEY); } catch (e) { /* storage blocked */ }
    buildPresets();
  });
  document.getElementById('c2-swap').addEventListener('click', swapProteinChemical);
  document.getElementById('c2-light').addEventListener('input', applyLight);
  document.getElementById('c2-add').addEventListener('click', addPreset);
  document.getElementById('c2-apply').addEventListener('click', function () {
    var v = document.getElementById('c2-export').value.trim().replace(/#/g, '');
    if (/^([0-9a-fA-F]{6}\s+){6,7}[0-9a-fA-F]{6}$/.test(v)) applyPreset(v);
  });
})();
