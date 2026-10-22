---
layout: default
title: Colours
permalink: /colours/
sitemap: false
noindex: true
---

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
  /* the map window, as the Atlas's (#m2-view) */
  #c2-view { position: relative; width: 100%; height: 504px; min-height: 300px; max-height: calc(100vh / var(--zoom, 1) - 70px); resize: vertical; overflow: hidden; box-sizing: border-box; border: 1px solid #ddd; border-radius: 4px; background: #fff; cursor: grab; touch-action: none; user-select: none; }
  #c2-view.c2-drag { cursor: grabbing; }
  #c2-view:focus, .c2-ctrl button:focus { outline: none; }
  .c2-ctrl { position: absolute; top: 8px; right: 8px; display: flex; gap: 4px; align-items: center; }
  .c2-ctrl button { font-size: 13px; min-width: 28px; padding: 2px 8px; color: #222; background: #fffffff0; border: 1px solid #bbb; border-radius: 4px; cursor: pointer; }
  .c2-ctrl button:hover { border-color: #4183c4; color: #4183c4; }
  #c2-out, #c2-in { box-sizing: border-box; width: 21px; height: 21px; min-width: 0; padding: 0; }
  #c2-fit { box-sizing: border-box; width: 44px; height: 21px; padding: 0; }
  #c2-zoom { font-size: 12px; color: #666; min-width: 40px; text-align: right; margin-right: 4px; }
  /* what a dropped map is waiting for, or why it is not drawn */
  #c2-status { position: absolute; left: 8px; top: 8px; max-width: calc(100% - 200px); max-height: calc(100% - 16px); overflow: auto; box-sizing: border-box; padding: 3px 8px; font-size: 13px; color: #666; background: #fffffff0; border: 1px solid #ddd; border-radius: 4px; white-space: pre-wrap; cursor: auto; user-select: text; }
  #c2-status.c2-bad { color: #c62828; }
  /* the map's roles, set by colours2.js */
  #c2-map svg { position: absolute; left: 0; top: 0; max-width: none; fill: var(--ink); stroke: var(--ink); }
  #c2-map .c-compartment { fill: var(--c-compartment); }
  #c2-map .t-compartment { fill: var(--t-compartment); font-weight: var(--w-compartment); }
  #c2-map .c-complex { fill: var(--c-complex); }
  #c2-map .t-complex { fill: var(--t-complex); font-weight: var(--w-complex); }
  #c2-map .c-protein { fill: var(--c-protein); }
  #c2-map .t-protein { fill: var(--t-protein); font-weight: var(--w-protein); }
  #c2-map .c-hlProtein { fill: var(--c-hlProtein); }
  #c2-map .t-hlProtein { fill: var(--t-hlProtein); font-weight: var(--w-hlProtein); }
  #c2-map .c-metabolite { fill: var(--c-metabolite); }
  #c2-map .t-metabolite { fill: var(--t-metabolite); font-weight: var(--w-metabolite); }
  #c2-map .c-white { fill: var(--c-white); }
  #c2-map .t-white { fill: var(--t-white); font-weight: var(--w-white); }
  #c2-map .c-gene { fill: var(--c-gene); }
  #c2-map .t-gene { fill: var(--t-gene); font-weight: var(--w-gene); }
  #c2-map .t-page { fill: var(--t-page); }
  /* the map's background: white, whatever the theme (user, 2026-10-22) */
  #c2-map .c-page { fill: #fff; }
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
  button.c2-act, summary.c2-act { display: inline-block; font-family: inherit; font-size: 14px; line-height: 20px; padding: 4px 10px; margin: 4px 4px 0 0; cursor: pointer; color: #777; background: #fff; border: 1px solid #777; border-radius: 5px; }
  button.c2-act:hover, summary.c2-act:hover, .c2-menu[open] summary.c2-act { background: #4183c4; border-color: #4183c4; color: #fff; }
  button.c2-act:disabled, button.c2-act:disabled:hover { color: #bbb; background: #fff; border-color: #ccc; cursor: default; }
  /* the map menu, as the Atlas's Images menu */
  .c2-menu { display: inline-block; position: relative; vertical-align: top; }
  .c2-menu summary { list-style: none; }
  .c2-menu summary::-webkit-details-marker { display: none; }
  .c2-caret { margin-left: 4px; font-size: 11px; flex: none; }
  /* one width for any map name, so the buttons after it never move: a long
     name (a dropped file's) is cut with …, the full name on hover */
  .c2-menu summary.c2-act { display: inline-flex; box-sizing: border-box; width: 140px; vertical-align: top; }
  #c2-mapname { flex: 1; min-width: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
  .c2-list { position: absolute; z-index: 5; left: 0; top: 34px; min-width: 110px; background: #fff; border: 1px solid #ccc; border-radius: 5px; box-shadow: 0 2px 8px rgba(0, 0, 0, .12); padding: 4px 0; }
  .c2-up .c2-list { top: auto; bottom: 30px; }
  .c2-list a { display: block; font-size: 14px; line-height: 20px; padding: 4px 12px; color: #777; text-decoration: none; white-space: nowrap; }
  .c2-list a:hover { background: #4183c4; color: #fff; }
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
<div id="c2-view" tabindex="0">
<div id="c2-map" data-v="{{ site.time | date: '%s' }}"></div>
<div id="c2-status" hidden></div>
<div class="c2-ctrl">
<span id="c2-zoom"></span>
<button type="button" id="c2-out" title="Zoom out">&minus;</button>
<button type="button" id="c2-in" title="Zoom in">+</button>
<button type="button" id="c2-fit" title="Whole map">Fit</button>
</div>
</div>
<div class="c2-under" data-v="{{ site.time | date: '%s' }}">
<details class="c2-menu" id="c2-maps"><summary class="c2-act"><span id="c2-mapname">iNOS</span><span class="c2-caret">▾</span></summary><div class="c2-list">
<a href="?map=inos" data-key="inos" data-map="/images/colours2/F007-inos">iNOS</a>
<a href="?map=glycolysis" data-key="glycolysis" data-map="/images/colours2/F001-glycolysis">Glycolysis</a>
</div></details>
<button type="button" class="c2-act" id="c2-link">Copy link</button>
<button type="button" class="c2-act" id="c2-yed">Download yEd file<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></button>
<button type="button" class="c2-act" id="c2-cd">Download CellDesigner file<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></button>
<button type="button" class="c2-act" id="c2-add">Add to Presets</button>
</div>
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

<script>
{% include mapconv.js %}
</script>
<script src="/images/colours2/presets.js?v={{ site.time | date: '%s' }}"></script>
<script src="/images/colours2/colours2.js?v={{ site.time | date: '%s' }}"></script>
