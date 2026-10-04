// Every preset from presets.js drawn on the iNOS map, for side-by-side comparison.
// Same decoding as colours2.js: pixel = t * fill[class] + (1 - t) * ink.
(function () {
  'use strict';

  var MAX_W = 2000; // card canvases are downscaled to this width
  var grid = document.getElementById('cx-grid');
  var hlBox = document.getElementById('cx-hl');
  var layers = null, full = null, fctx = null, out = null, cards = [], job = 0;

  function rgb(h) { return [0, 2, 4].map(function (i) { return parseInt(h.substr(i, 2), 16); }); }

  function loadLayers(src, done) {
    var img = new Image();
    img.onload = function () {
      var w = img.naturalWidth, h = img.naturalHeight;
      var tmp = document.createElement('canvas');
      tmp.width = w; tmp.height = h;
      var tctx = tmp.getContext('2d');
      tctx.drawImage(img, 0, 0);
      var d = tctx.getImageData(0, 0, w, h).data;
      // Crop the white page margin (class 7 with no ink)
      var x0 = w, y0 = h, x1 = -1, y1 = -1, x, y, k;
      for (y = 0; y < h; y++) {
        for (x = 0; x < w; x++) {
          k = (y * w + x) * 4;
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
      full = document.createElement('canvas');
      full.width = cw; full.height = ch;
      fctx = full.getContext('2d');
      out = fctx.createImageData(cw, ch);
      done();
    };
    img.src = src;
  }

  // Theme order: compartment, complex, protein, metabolite, hlProtein, white, ink
  function draw(card) {
    var hs = card.theme.split(/\s+/).map(rgb);
    var fills = [];
    fills[0] = hs[0]; fills[3] = hs[1]; fills[2] = hs[2]; fills[4] = hs[3];
    fills[6] = hlBox.checked ? hs[4] : hs[2];
    fills[1] = hs[5]; fills[5] = fills[3];
    var ink = hs[6];
    var d = out.data, cls = layers.cls, t = layers.t, n = layers.w * layers.h;
    for (var i = 0, j = 0; i < n; i++, j += 4) {
      var a = t[i] / 255, b = 1 - a;
      if (cls[i] === 7) {
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
    fctx.putImageData(out, 0, 0);
    var c = card.canvas, cctx = c.getContext('2d');
    cctx.imageSmoothingQuality = 'high';
    cctx.clearRect(0, 0, c.width, c.height);
    cctx.drawImage(full, 0, 0, c.width, c.height);
  }

  // One preset per frame so the page stays responsive
  function drawAll() {
    var id = ++job, i = 0;
    (function next() {
      if (id !== job || i >= cards.length) return;
      draw(cards[i++]);
      setTimeout(next, 0);
    })();
  }

  window.C2_PRESETS.forEach(function (p) {
    var card = document.createElement('div');
    card.className = 'cx-card';
    var h = document.createElement('h3');
    h.textContent = p[0];
    var code = document.createElement('code');
    code.textContent = p[1];
    h.appendChild(code);
    var c = document.createElement('canvas');
    card.appendChild(h);
    card.appendChild(c);
    grid.appendChild(card);
    cards.push({ theme: p[1], canvas: c });
  });

  loadLayers(grid.getAttribute('data-layers'), function () {
    var w = Math.min(layers.w, MAX_W), h = Math.round(layers.h * w / layers.w);
    cards.forEach(function (card) { card.canvas.width = w; card.canvas.height = h; });
    drawAll();
  });
  hlBox.addEventListener('change', drawAll);
})();
