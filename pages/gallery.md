---
layout: default
title: Gallery
permalink: /gallery/
---

<style>
.gallery {
  display: grid;
  grid-template-columns: repeat(4, 225px);
  justify-content: center;
  column-gap: 0;
  row-gap: 28px;
}

.gallery-item {
  width: 225px;
  text-align: center;
}

.gallery-title {
  display: block;
  margin-bottom: 2px;
}

.gallery-downloads {
  font-size: 0.85em;
  margin-bottom: 8px;
}

.gallery-downloads a + a {
  margin-left: 8px;
}

.gallery-image {
  width: 190px;
  border: 1px solid #c6c6c6;
  background-color: #edebe472;
}

@media (max-width: 920px) {
  .gallery {
    grid-template-columns: repeat(2, 225px);
  }
}

@media (max-width: 480px) {
  .gallery {
    grid-template-columns: 225px;
  }
}
</style>

<div class="gallery">

  <div class="gallery-item">
    <a class="gallery-title" href="/glycolysis/">Glycolysis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F001-glycolysis.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F001-glycolysis" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/glycolysis/">
      <img class="gallery-image" src="/images/gallery/F001-glycolysis-cut.svg" alt="Glycolysis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/eicosanoids/">Eicosanoid production</a>
    <div class="gallery-downloads">
      <a href="/downloads/F002-eicosanoids.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F002-eicosanoids" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/eicosanoids/">
      <img class="gallery-image" src="/images/gallery/F002-eicosanoids-cut.svg" alt="Eicosanoid production map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/mevalonate/">Mevalonate biosynthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F003-mevalonate.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F003-mevalonate" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/mevalonate/">
      <img class="gallery-image" src="/images/gallery/F003-mevalonate-cut.svg" alt="Mevalonate biosynthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/glycogen/">Glycogen metabolism</a>
    <div class="gallery-downloads">
      <a href="/downloads/F004-glycogen-muscle.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F004-glycogen-muscle" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/glycogen/">
      <img class="gallery-image" src="/images/gallery/F004-glycogen-muscle-cut.svg" alt="Glycogen metabolism map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/acly/">Acetyl-CoA synthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F006-acly.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F006-acly" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/acly/">
      <img class="gallery-image" src="/images/gallery/F006-ACLY-cut.svg" alt="Acetyl-CoA synthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/camp/">cAMP hydrolysis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F012-camp.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F012-camp" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/camp/">
      <img class="gallery-image" src="/images/gallery/F012-cAMP-cut.svg" alt="cAMP hydrolysis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/inos/">iNOS pathway</a>
    <div class="gallery-downloads">
      <a href="/downloads/F007-inos.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F007-inos" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/inos/">
      <img class="gallery-image" src="/images/gallery/F007-inos-cut.svg" alt="iNOS pathway map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/enos/">eNOS pathway</a>
    <div class="gallery-downloads">
      <a href="/downloads/F008-enos.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F008-enos" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/enos/">
      <img class="gallery-image" src="/images/gallery/F008-enos-cut.svg" alt="eNOS pathway map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/carnitine/">Acyl-carnitine synthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F014-carnitine.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F014-carnitine" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/carnitine/">
      <img class="gallery-image" src="/images/gallery/F014-carnitine-cut.svg" alt="Acyl-carnitine synthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/srebp/">SREBP signalling</a>
    <div class="gallery-downloads">
      <a href="/downloads/F005-srebp.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F005-srebp" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/srebp/">
      <img class="gallery-image" src="/images/gallery/F005-srebp-cut.svg" alt="SREBP signalling map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/tag/">Triacylglycerol hydrolysis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F015-tag.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F015-tag" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/tag/">
      <img class="gallery-image" src="/images/gallery/F015-tag-cut.svg" alt="Triacylglycerol hydrolysis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/estrogen/">Estradiol biosynthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F018-estrogen.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F018-estrogen" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/estrogen/">
      <img class="gallery-image" src="/images/gallery/F018-estrogen-cut.svg" alt="Estradiol biosynthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/phosphoinositides/">Phosphoinositide</a>
    <div class="gallery-downloads">
      <a href="/downloads/F009-phosphoinositides.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F009-phosphoinositides" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/phosphoinositides/">
      <img class="gallery-image" src="/images/gallery/F009-phosphoinositides-cut.svg" alt="Phosphoinositide map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/glutaminase/">Glutaminolysis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F019-glutaminase.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F019-glutaminase" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/glutaminase/">
      <img class="gallery-image" src="/images/gallery/F019-glutaminase-cut.svg" alt="Glutaminolysis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/pyrimidine/">Pyrimidine biosynthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F020-pyrimidine.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F020-pyrimidine" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/pyrimidine/">
      <img class="gallery-image" src="/images/gallery/F020-pyrimidine-cut.svg" alt="Pyrimidine biosynthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/aspirin/">Aspirin</a>
    <div class="gallery-downloads">
      <a href="/downloads/F100-aspirin.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
      <a href="https://mreg.elixir-luxembourg.org/minerva/index.html?id=F100-aspirin" target="_blank" rel="noopener">MINERVA{% include icon-external.html %}</a>
    </div>
    <a href="/aspirin/">
      <img class="gallery-image" src="/images/gallery/F100-aspirin-cut.svg" alt="Aspirin map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/ureacycle/">Urea cycle</a>
    <div class="gallery-downloads">
      <a href="/downloads/F021-ureacycle.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
    </div>
    <a href="/ureacycle/">
      <img class="gallery-image" src="/images/gallery/F021-ureacycle-cut.svg" alt="Urea cycle map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/bcaa/">BCAA catabolism</a>
    <div class="gallery-downloads">
      <a href="/downloads/F022-bcaa.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
    </div>
    <a href="/bcaa/">
      <img class="gallery-image" src="/images/gallery/F022-bcaa-cut.svg" alt="BCAA catabolism map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/pdh/">Pyruvate dehydrogenase</a>
    <div class="gallery-downloads">
      <a href="/downloads/F023-pdh.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
    </div>
    <a href="/pdh/">
      <img class="gallery-image" src="/images/gallery/F023-pdh-cut.svg" alt="Pyruvate dehydrogenase map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/nnos/">nNOS pathway</a>
    <div class="gallery-downloads">
      <a href="/downloads/F025-nnos.graphml">GraphML<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" style="margin-left:3px;vertical-align:-2px" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5"/><path d="M4 15v5h16v-5"/></svg></a>
    </div>
    <a href="/nnos/">
      <img class="gallery-image" src="/images/gallery/F025-nnos-cut.svg" alt="nNOS pathway map">
    </a>
  </div>

</div>
