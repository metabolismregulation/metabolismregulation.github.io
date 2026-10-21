---
layout: default
title: Colours, dark
permalink: /colours/dark/
sitemap: false
noindex: true
---

<!-- Test page: /colours/ with the page around the map in dark, and dark map
     presets after Default. The button under the map switches the page
     between dark and light. -->
<script>
  window.C2_STORE = 'colours-dark';
  try { if (localStorage.getItem('colours-dark.page') === 'light') document.documentElement.classList.add('c2-lt'); } catch (e) { /* storage blocked */ }
</script>
<style>
  html:not(.c2-lt) { color-scheme: dark; }
  html:not(.c2-lt), html:not(.c2-lt) body { background: #1b1d21; color: #d4d4d4; }
  html:not(.c2-lt) .site-name a, html:not(.c2-lt) nav a, html:not(.c2-lt) h3 { color: #e4e4e4; }
  html:not(.c2-lt) .site-description { color: #999; }
  html:not(.c2-lt) .wrapper-masthead { border-bottom-color: #33363c; }
  html:not(.c2-lt) .wrapper-footer { border-top-color: #33363c; }
  html:not(.c2-lt) .svg-icon { filter: invert(0.85); }
  html:not(.c2-lt) .c2-small, html:not(.c2-lt) .c2-mixtitle, html:not(.c2-lt) .c2-cr { color: #999; }
  html:not(.c2-lt) .c2-low { color: #ff8a80; }
  html:not(.c2-lt) .c2-preset { color: #d4d4d4; }
  html:not(.c2-lt) .c2-role:hover, html:not(.c2-lt) .c2-dot:hover, html:not(.c2-lt) .c2-preset:hover,
  html:not(.c2-lt) .c2-mixadd:hover, html:not(.c2-lt) .c2-renaming { border-color: #555; }
  html:not(.c2-lt) .c2-preset.c2-on, html:not(.c2-lt) .c2-dot.c2-on, html:not(.c2-lt) .c2-sugg.c2-on { border-color: #bbb; }
  html:not(.c2-lt) .c2-dragging, html:not(.c2-lt) .c2-dot.c2-dragging { background: #2a2d33; border-color: #bbb; box-shadow: 0 2px 6px #0008; }
  html:not(.c2-lt) .c2-dropping { background: #2a2d33; outline-color: #999; }
  html:not(.c2-lt) .c2-assigning .c2-role:hover { background: #2a2d33; }
  html:not(.c2-lt) .c2-chips i, html:not(.c2-lt) .c2-dot i, html:not(.c2-lt) .c2-role input[type=color] { border-color: #fff3; }
  html:not(.c2-lt) .c2-mixadd svg { color: #888; }
  html:not(.c2-lt) .c2-mixadd svg rect { fill: #24272c; stroke: #555; }
  html:not(.c2-lt) .c2-mixadd:hover svg { color: #ddd; }
  html:not(.c2-lt) .c2-hexin, html:not(.c2-lt) #c2-export, html:not(.c2-lt) .c2-panel select, html:not(.c2-lt) .c2-rename {
    background: #24272c; color: #d4d4d4; border: 1px solid #484b52; }
  html:not(.c2-lt) #c2-light { background: #444; }
  html:not(.c2-lt) #c2-light::-webkit-slider-thumb { background: #2a2d33; border-color: #999; }
  html:not(.c2-lt) #c2-light::-moz-range-thumb { background: #2a2d33; border-color: #999; }
  html:not(.c2-lt) #c2-light::-moz-range-progress { background: #444; }
  html:not(.c2-lt) .c2-del { color: #777; }
  html:not(.c2-lt) .c2-del:hover { color: #ddd; }
  html:not(.c2-lt) #c2-drop { border-color: #555; }
  html:not(.c2-lt) #c2-drop.c2-over { border-color: #bbb; background: #24272c; }
  html:not(.c2-lt) .c2-sugg { background: #24272c; border-color: #444; }
  html:not(.c2-lt) .c2-sugg:hover { border-color: #999; }
  html:not(.c2-lt) .c2-armed { outline-color: #fff; }
  html:not(.c2-lt) button.c2-act { color: #aaa; background: transparent; border-color: #777; }
  html:not(.c2-lt) button.c2-act:hover { background: #4183c4; border-color: #4183c4; color: #fff; }
  html:not(.c2-lt) button.c2-act:disabled, html:not(.c2-lt) button.c2-act:disabled:hover { color: #666; background: transparent; border-color: #444; }
</style>

<style>
  .c2-wide { width: calc(96vw / var(--zoom, 1)); max-width: 2000px; position: relative; left: 50%; transform: translateX(-50%); }
  .c2-grid { display: grid; grid-template-columns: 270px 1fr 270px; grid-template-areas: "left map right"; gap: 20px; align-items: start; }
  .c2-left { grid-area: left; }
  .c2-mapcol { grid-area: map; min-width: 0; }
  .c2-right { grid-area: right; }
  @media (max-width: 1150px) { .c2-grid { grid-template-columns: 270px 1fr; grid-template-areas: "left map" "right map"; } }
  @media (max-width: 900px) { .c2-grid { grid-template-columns: 1fr; grid-template-areas: "left" "map" "right"; } }
  .c2-panel h3 { margin: 0 0 8px; font-size: 15px; }
  .c2-panel section { margin-bottom: 18px; }
  #c2-map { width: 100%; height: auto; display: block; }
  /* Roles in the presets style: no box until hovered, colour as a plain
     rectangle with the preset squares' border */
  #c2-roles { display: flex; flex-direction: column; gap: 1px; }
  .c2-role { display: grid; grid-template-columns: 24px 1fr auto auto; gap: 6px; align-items: center; font-size: 13px; padding: 2px 4px; border: 1px solid transparent; border-radius: 4px; }
  .c2-role:hover { border-color: #bbb; }
  .c2-role input[type=color] { -webkit-appearance: none; appearance: none; box-sizing: border-box; width: 24px; height: 16px; padding: 0; border: 1px solid #0003; border-radius: 0; background: none; cursor: pointer; }
  .c2-role input[type=color]::-webkit-color-swatch-wrapper { padding: 0; }
  .c2-role input[type=color]::-webkit-color-swatch { border: none; border-radius: 0; }
  .c2-role input[type=color]::-moz-color-swatch { border: none; border-radius: 0; }
  .c2-hexin { width: 62px; font: 11px monospace; color: #333; border: 1px solid #ccc; border-radius: 3px; padding: 2px 3px; }
  .c2-role[draggable=true] { cursor: grab; }
  .c2-dropping { background: #e8eef6; outline: 1px dashed #666; }
  .c2-cr { font-size: 11px; color: #777; min-width: 42px; text-align: right; }
  .c2-nohl .c2-hl { display: none; }
  .c2-cxbg .c2-roles .c2-role:nth-child(2) { opacity: 0.4; pointer-events: none; }
  .c2-low { color: #b3261e; font-weight: bold; }
  .c2-assigning .c2-role { cursor: copy; outline: 1px dashed #999; margin-bottom: 2px; }
  .c2-assigning .c2-role:hover { background: #f0f0f0; }
  #c2-presets { display: flex; flex-direction: column; gap: 4px; }
  .c2-mixer { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 6px; }
  .c2-mixcol { display: flex; flex-direction: column; gap: 2px; }
  .c2-mixtitle { font-size: 13px; color: #666; margin-bottom: 2px; }
  .c2-dot { display: flex; align-items: center; gap: 6px; width: 100%; font-size: 13px; padding: 2px 4px; border: 1px solid transparent; border-radius: 4px; background: none; cursor: pointer; text-align: left; white-space: nowrap; }
  .c2-dot i { flex: none; width: 14px; height: 14px; border: 1px solid #0003; box-sizing: content-box; cursor: grab; touch-action: none; }
  .c2-dot.c2-dragging { border-color: #333; box-shadow: 0 2px 6px #0003; background: #fff; }
  .c2-dot:hover { border-color: #bbb; }
  .c2-dot.c2-on { border-color: #333; font-weight: bold; }
  .c2-dname { flex: 1; min-width: 0; overflow: hidden; text-overflow: clip; }
  .c2-dot .c2-del { width: 12px; height: 12px; }
  .c2-dot .c2-del::before, .c2-dot .c2-del::after { left: 2px; top: 5.5px; width: 8px; }
  .c2-mixadd { display: flex; width: 100%; padding: 2px 4px; background: none; border: 1px solid transparent; border-radius: 4px; cursor: pointer; }
  .c2-mixadd:hover { border-color: #bbb; }
  /* square and plus drawn as one small picture, so the plus stays centred
     wherever the column puts the square (columns fall between screen pixels) */
  .c2-mixadd svg { display: block; width: 16px; height: 16px; color: #999; }
  .c2-mixadd svg rect { fill: #fff; stroke: #ccc; }
  .c2-mixadd:hover svg { color: #333; }
  .c2-mixadd:hover svg rect { stroke: #888; }
  .c2-preset { display: flex; align-items: center; gap: 6px; text-align: left; font: -webkit-small-control; font-size: 13px; line-height: normal; color: #000; user-select: none; padding: 2px 4px; border: 1px solid transparent; border-radius: 4px; background: none; cursor: pointer; }
  .c2-preset:hover { border-color: #bbb; }
  .c2-preset .c2-chips { cursor: grab; touch-action: none; }
  .c2-pname { flex: 1; min-width: 0; }
  .c2-renaming { cursor: default; border-color: #bbb; }
  .c2-rename { flex: 1; min-width: 0; font: inherit; padding: 0 3px; margin: -1px 0; border: 1px solid #999; border-radius: 3px; outline: none; background: #fff; }
  .c2-preset.c2-on { border-color: #333; font-weight: bold; }
  .c2-preset:focus, .c2-dot:focus { outline: none; }
  #c2-light { -webkit-appearance: none; appearance: none; height: 4px; border-radius: 2px; background: #ddd; outline: none; }
  #c2-light::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%; background: #fff; border: 1px solid #888; cursor: pointer; }
  #c2-light::-moz-range-thumb { width: 16px; height: 16px; border-radius: 50%; background: #fff; border: 1px solid #888; cursor: pointer; }
  #c2-light::-moz-range-progress { background: #ddd; }
  .c2-del { margin-left: auto; position: relative; flex: none; width: 16px; height: 16px; color: #aaa; }
  .c2-del::before, .c2-del::after { content: ""; position: absolute; left: 3px; top: 7.5px; width: 10px; height: 1px; background: currentColor; transform: rotate(45deg); }
  .c2-del::after { transform: rotate(-45deg); }
  .c2-del:hover { color: #333; }
  /* the remove cross shows on hover, on the chosen row and where there is no hover;
     its space stays reserved so names do not move */
  .c2-preset .c2-del, .c2-dot .c2-del { opacity: 0; transition: opacity 0.12s; }
  .c2-preset:hover .c2-del, .c2-preset.c2-on .c2-del, .c2-preset:focus-visible .c2-del,
  .c2-dot:hover .c2-del, .c2-dot.c2-on .c2-del, .c2-dot:focus-visible .c2-del { opacity: 1; }
  @media (hover: none) { .c2-preset .c2-del, .c2-dot .c2-del { opacity: 1; } }
  .c2-preset .c2-del { width: 12px; height: 12px; }
  .c2-preset .c2-del::before, .c2-preset .c2-del::after { left: 2px; top: 5.5px; width: 8px; }
  .c2-dragging { border-color: #333; box-shadow: 0 2px 6px #0003; background: #fff; }
  .c2-dragging .c2-chips { cursor: grabbing; }
  .c2-chips { display: inline-flex; }
  .c2-chips i { width: 14px; height: 14px; border: 1px solid #0003; margin-right: -1px; }
  #c2-drop { border: 2px dashed #bbb; border-radius: 6px; padding: 10px; font-size: 13px; text-align: center; }
  #c2-drop.c2-over { border-color: #333; background: #f6f6f6; }
  #c2-thumb { max-width: 100%; max-height: 140px; margin-top: 8px; }
  #c2-suggest { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 8px; }
  #c2-suggest:empty { display: none; }
  .c2-sugg { flex: 1; display: flex; justify-content: center; padding: 5px 4px; border: 1px solid #ddd; border-radius: 4px; background: #fff; cursor: pointer; }
  .c2-sugg:hover { border-color: #888; }
  .c2-sugg.c2-on { border-color: #333; }
  .c2-sugg:focus { outline: none; }
  #c2-swatches { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
  .c2-swatch { font-size: 11px; padding: 6px; border: 1px solid #0002; border-radius: 4px; cursor: pointer; font-family: monospace; }
  .c2-armed { outline: 3px solid #000; outline-offset: 1px; }
  .c2-under { margin: 8px 0 0; }
  #c2-export { width: 100%; resize: none; font-family: monospace; font-size: 11px; box-sizing: border-box; }
  .c2-small { font-size: 12px; color: #666; }
  .c2-panel select { font-size: 13px; }
  /* the Atlas download buttons: white, grey edge and text, filled blue on hover */
  button.c2-act { font-family: inherit; font-size: 14px; line-height: 20px; padding: 4px 10px; margin: 4px 4px 0 0; cursor: pointer; color: #777; background: #fff; border: 1px solid #777; border-radius: 5px; }
  button.c2-act:hover { background: #4183c4; border-color: #4183c4; color: #fff; }
  button.c2-act:disabled, button.c2-act:disabled:hover { color: #bbb; background: #fff; border-color: #ccc; cursor: default; }
  button.c2-act svg { width: 14px; height: 14px; margin-left: 5px; vertical-align: -2px; }
</style>

<div class="c2-wide">
<div class="c2-grid">
<div class="c2-panel c2-left">

<section>
<h3 title="Arrow keys step through them. Drag the colours to reorder. Hover over a preset to remove it; Reset brings back built-in ones. Double-click an added preset to rename it.">Presets</h3>
<div id="c2-presets"></div>
<p class="c2-small" style="margin:6px 0 0"><button type="button" class="c2-act" id="c2-reset-order" title="Original order, and hidden built-in presets back. Added presets stay.">Reset</button></p>
</section>

<section>
<h3 title="Drop or paste an image. Arrow keys step through the suggestions. Swap colours between protein and chemical.">Palette from image</h3>
<p class="c2-small" style="margin:6px 0 0;display:flex;align-items:center;gap:3px;white-space:nowrap">
<span>Mode:</span> <select id="c2-mode"><option value="avg" selected>average</option><option value="exact">exact fills</option></select>
<span style="margin-left:4px">Clusters:</span> <select id="c2-k"><option>6</option><option>8</option><option>10</option><option>12</option><option>14</option><option selected>16</option></select>
<button type="button" class="c2-act" id="c2-swap" style="margin:0 0 0 auto" title="Swap protein and chemical colours">Swap</button>
</p>
<div id="c2-suggest"></div>
<p class="c2-small" style="margin:8px 0 0;display:flex;align-items:center;gap:6px">
<span>Lighter</span><input type="range" id="c2-light" min="0" max="100" value="0" dir="rtl" style="flex:1" title="Right: the colours as they are; left: lighter and softer">
</p>
<div id="c2-swatches"></div>
<div id="c2-drop" style="margin-top:8px">
Drop, paste or <label style="text-decoration:underline;cursor:pointer">choose<input type="file" id="c2-file" accept="image/*,.xml,.graphml,.sbgn,.sbgnml" hidden></label> an image
<br><span class="c2-small">Processed in your browser only.</span>
<br><img id="c2-thumb" hidden alt="">
</div>
</section>

<section>
<h3 title="Colour vision shows the map as seen with each type of colour blindness. Paste a theme code of 7 to 9 colours. The last two, for text and gene, are optional.">Colour vision and theme code</h3>
<p class="c2-small" style="margin:0 0 6px;display:flex;align-items:center;gap:6px">Colour vision:
<select id="c2-cvd">
  <option value="none">normal</option>
  <option value="deuteranopia">deuteranopia</option>
  <option value="protanopia">protanopia</option>
  <option value="tritanopia">tritanopia</option>
</select>
<!-- applies the theme code below -->
<button type="button" class="c2-act" id="c2-apply" style="margin:0 0 0 auto">Apply</button></p>
<textarea id="c2-export" rows="3" spellcheck="false"></textarea>
</section>

</div>
<div class="c2-mapcol">
<canvas id="c2-map" data-layers="/images/colours2/F007-inos-layers.png?v={{ site.time | date: '%s' }}"></canvas>
<p class="c2-under" data-v="{{ site.time | date: '%s' }}">
<button type="button" class="c2-act" id="c2-link">Copy link</button>
<button type="button" class="c2-act" id="c2-yed">Download yEd file<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></button>
<button type="button" class="c2-act" id="c2-cd">Download CellDesigner file<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></button>
<button type="button" class="c2-act" id="c2-add">Add to Presets</button>
<button type="button" class="c2-act" id="c2-page" title="Switch the page around the map between dark and light">Light page</button>
</p>
<p class="c2-small" id="c2-cdnote" style="margin:6px 0 0" hidden>The CellDesigner file does not store text colour; the text will remain black in CellDesigner. The yEd file keeps the current view.</p>
</div>
<div class="c2-panel c2-right">

<section>
<h3 title="Arrow keys move within a column. + adds the map’s current colour. Drag a square to reorder. Hover over an added colour to remove it; double-click it to rename it.">Mixer</h3>
<div id="c2-mixer" class="c2-mixer"></div>
</section>

<section>
<h3 title="Set any single colour. The highlight red is changed only here. Ctrl+Z or ⌘Z undoes a change, with Shift redoes it.">Roles</h3>
<p class="c2-small" style="margin:0 0 6px"><label><input type="checkbox" id="c2-hl" autocomplete="off"> Highlighted protein</label> &nbsp; <label><input type="checkbox" id="c2-cxbg" autocomplete="off"> Complex transparent</label></p>
<div id="c2-roles" class="c2-roles"></div>
<p class="c2-small">Number on the right: contrast of the text colour on that fill. Red means below 7:1.</p>
</section>

</div>
</div>
</div>

<script src="/images/colours2/presets.js?v={{ site.time | date: '%s' }}"></script>
<script src="/images/colours2/presets-dark.js?v={{ site.time | date: '%s' }}"></script>
<script src="/images/colours2/colours2.js?v={{ site.time | date: '%s' }}"></script>
<script>
  (function () {
    var b = document.getElementById('c2-page'), h = document.documentElement;
    function label() { b.textContent = h.classList.contains('c2-lt') ? 'Dark page' : 'Light page'; }
    label();
    b.addEventListener('click', function () {
      h.classList.toggle('c2-lt');
      try { localStorage.setItem('colours-dark.page', h.classList.contains('c2-lt') ? 'light' : 'dark'); } catch (e) { /* storage blocked */ }
      label();
    });
  })();
</script>
