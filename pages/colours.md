---
layout: default
title: Colours
permalink: /colours/
---

<style>
  .c2-wide { width: 96vw; max-width: 2000px; position: relative; left: 50%; transform: translateX(-50%); }
  .c2-grid { display: grid; grid-template-columns: 270px 1fr 270px; grid-template-areas: "left map right"; gap: 20px; align-items: start; }
  .c2-left { grid-area: left; }
  .c2-mapcol { grid-area: map; min-width: 0; }
  .c2-right { grid-area: right; }
  @media (max-width: 1150px) { .c2-grid { grid-template-columns: 270px 1fr; grid-template-areas: "left map" "right map"; } }
  @media (max-width: 900px) { .c2-grid { grid-template-columns: 1fr; grid-template-areas: "left" "map" "right"; } }
  .c2-panel h3 { margin: 0 0 8px; font-size: 15px; }
  .c2-panel section { margin-bottom: 18px; }
  #c2-map { width: 100%; height: auto; display: block; }
  .c2-role { display: grid; grid-template-columns: 30px 1fr auto auto; gap: 6px; align-items: center; font-size: 13px; padding: 2px 4px; border-radius: 4px; }
  .c2-role input[type=color] { width: 28px; height: 22px; padding: 0; border: 1px solid #bbb; background: none; cursor: pointer; }
  .c2-hexin { width: 62px; font: 11px monospace; color: #333; border: 1px solid #ccc; border-radius: 3px; padding: 2px 3px; }
  .c2-role[draggable=true] { cursor: grab; }
  .c2-dropping { background: #e8eef6; outline: 1px dashed #666; }
  .c2-cr { font-size: 11px; color: #777; min-width: 42px; text-align: right; }
  .c2-nohl .c2-hl { display: none; }
  .c2-cxbg #c2-roles .c2-role:nth-child(2) { opacity: 0.4; pointer-events: none; }
  .c2-low { color: #b3261e; font-weight: bold; }
  .c2-assigning .c2-role { cursor: copy; outline: 1px dashed #999; margin-bottom: 2px; }
  .c2-assigning .c2-role:hover { background: #f0f0f0; }
  #c2-presets { display: flex; flex-direction: column; gap: 4px; }
  #c2-mixer { display: grid; grid-template-columns: 64px 88px minmax(0, 1fr); gap: 4px; }
  .c2-mixtitle { font-size: 12px; color: #666; margin-bottom: 2px; }
  .c2-dot { display: flex; align-items: center; gap: 5px; width: 100%; font-size: 12px; padding: 2px 3px; border: 1px solid transparent; border-radius: 4px; background: none; cursor: pointer; text-align: left; white-space: nowrap; }
  .c2-dot i { flex: none; width: 14px; height: 14px; border-radius: 50%; border: 1px solid #0003; }
  .c2-dot:hover { border-color: #bbb; }
  .c2-dot.c2-on { border-color: #333; font-weight: bold; }
  .c2-preset { display: flex; align-items: center; gap: 8px; text-align: left; font-size: 13px; padding: 4px 6px; border: 1px solid #ddd; border-radius: 4px; background: #fff; cursor: pointer; }
  .c2-preset:hover { border-color: #888; }
  .c2-handle { color: #aaa; cursor: grab; touch-action: none; user-select: none; letter-spacing: -3px; padding: 0 4px 0 0; }
  .c2-handle:hover { color: #333; }
  .c2-dragging { border-color: #333; box-shadow: 0 2px 6px #0003; }
  .c2-dragging .c2-handle { cursor: grabbing; }
  .c2-chips { display: inline-flex; }
  .c2-chips i { width: 14px; height: 14px; border: 1px solid #0003; margin-right: -1px; }
  #c2-drop { border: 2px dashed #bbb; border-radius: 6px; padding: 10px; font-size: 13px; text-align: center; }
  #c2-drop.c2-over { border-color: #333; background: #f6f6f6; }
  #c2-thumb { max-width: 100%; max-height: 140px; margin-top: 8px; }
  #c2-swatches { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
  .c2-swatch { font-size: 11px; padding: 6px; border: 1px solid #0002; border-radius: 4px; cursor: pointer; font-family: monospace; }
  .c2-armed { outline: 3px solid #000; outline-offset: 1px; }
  #c2-export { width: 100%; font-family: monospace; font-size: 11px; box-sizing: border-box; }
  .c2-small { font-size: 12px; color: #666; }
  .c2-panel button.c2-act { font-size: 13px; padding: 4px 10px; margin: 4px 4px 0 0; cursor: pointer; }
</style>

<div class="c2-wide">
<div class="c2-grid">
<div class="c2-panel c2-left">

<section>
<h3>Presets</h3>
<div id="c2-presets"></div>
<p class="c2-small" style="margin:6px 0 0"><button type="button" class="c2-act" id="c2-reset-order">Reset order</button></p>
</section>

<section>
<h3>Palette from image</h3>
<div id="c2-drop">
Drop, paste or <label style="text-decoration:underline;cursor:pointer">choose<input type="file" id="c2-file" accept="image/*" hidden></label> an image
<br><span class="c2-small">Processed in your browser only.</span>
<br><img id="c2-thumb" hidden alt="">
</div>
<p class="c2-small" style="margin:6px 0 0">
Mode: <select id="c2-mode"><option value="avg" selected>average</option><option value="exact">exact fills</option></select><br>
Clusters: <select id="c2-k"><option>6</option><option>8</option><option>10</option><option>12</option><option>14</option><option selected>16</option></select>
&nbsp; <label><input type="checkbox" id="c2-soften"> soften for role</label>
</p>
<div id="c2-swatches"></div>
<button type="button" class="c2-act" id="c2-auto" disabled>Auto-assign</button>
</section>

<section>
<h3>View and export</h3>
<p class="c2-small" style="margin:0 0 6px">Colour vision:
<select id="c2-cvd">
  <option value="none">normal</option>
  <option value="deuteranopia">deuteranopia</option>
  <option value="protanopia">protanopia</option>
  <option value="tritanopia">tritanopia</option>
</select></p>
<textarea id="c2-export" rows="3" spellcheck="false"></textarea>
<button type="button" class="c2-act" id="c2-apply">Apply</button>
<button type="button" class="c2-act" id="c2-download">Download PNG</button>
</section>

</div>
<div class="c2-mapcol">
<canvas id="c2-map" data-layers="/images/colours2/F007-inos-layers.png"></canvas>
<div class="c2-text" markdown="1">

## Colour themes on the iNOS map

The map above is the <a href="/inos/">iNOS pathway</a> export, recoloured live in the browser. Every pixel of the original PNG was split into a fill (one of the colour roles) and the black ink of lines and text, so changing a role recolours the map exactly as yEd would draw it, without touching the GraphML.

## How to build a theme

1. Fix lightness first, then choose hues. Fills that carry black text work best between OKLCH lightness 0.85 and 0.92 with low chroma. Two fills at the same lightness but different hues read as categories; fills at different lightness read as importance.
2. Keep to three hues: one for proteins, one for small molecules, one for highlights. Complexes and compartments stay near-neutral so the nesting reads from borders, not colour.
3. Check each candidate under deuteranopia. Blue against yellow or orange survives; green against red does not.
4. From a figure in Nature or Science, or a Cell SnapShot, take the hues only. Journal figures are usually printed at full saturation on white, so their colours are too strong as fills behind text; the swatch picker keeps the hue and resets lightness and chroma for each role.

</div>
</div>
<div class="c2-panel c2-right">

<section>
<h3>Mixer</h3>
<div id="c2-mixer"></div>
</section>

<section>
<h3>Roles</h3>
<p class="c2-small" style="margin:0 0 6px"><label><input type="checkbox" id="c2-hl" autocomplete="off"> Highlighted protein</label> &nbsp; <label><input type="checkbox" id="c2-cxbg" autocomplete="off"> Complex transparent</label></p>
<div id="c2-roles"></div>
<p class="c2-small">Number on the right: contrast of text on that fill against the ink colour. Red means below 7:1.</p>
</section>

</div>
</div>
</div>

<script src="/images/colours2/colours2.js?v={{ site.time | date: '%s' }}"></script>
