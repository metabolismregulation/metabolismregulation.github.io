---
layout: default
title: Colour examples
permalink: /colour-examples/
---

<style>
  .cx-wide { width: 96vw; max-width: 2000px; position: relative; left: 50%; transform: translateX(-50%); }
  .cx-bar { font-size: 13px; color: #555; margin: 0 0 12px; }
  .cx-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px 24px; }
  @media (max-width: 900px) { .cx-grid { grid-template-columns: 1fr; } }
  .cx-card h3 { margin: 0 0 4px; font-size: 15px; display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }
  .cx-card code { font-size: 11px; color: #777; font-weight: normal; background: none; }
  .cx-card canvas { width: 100%; height: auto; display: block; }
</style>

<div class="cx-wide">
<p class="cx-bar"><label><input type="checkbox" id="cx-hl" autocomplete="off"> Highlighted protein</label> &nbsp; <a href="/colours/">Colours</a></p>
<div class="cx-grid" id="cx-grid" data-layers="/images/colours2/F007-inos-layers.png"></div>
</div>

<script src="/images/colours2/presets.js?v={{ site.time | date: '%s' }}"></script>
<script src="/images/colours2/examples.js?v={{ site.time | date: '%s' }}"></script>
