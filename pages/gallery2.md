---
layout: default
title: Gallery
permalink: /gallery2/
---

<style>
.gallery {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28px 18px;
  margin-top: 10px;
}

.gallery-item {
  text-align: center;
  background-color: #edebe472;
  padding: 12px 10px 14px 10px;
  border: 1px solid #d8d8d8;
  box-sizing: border-box;
}

.gallery-title {
  display: block;
  margin-bottom: 4px;
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
  max-width: 100%;
  border: 1px solid #c6c6c6;
  background-color: white;
}

@media (max-width: 800px) {
  .gallery {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 450px) {
  .gallery {
    grid-template-columns: 1fr;
  }
}
</style>

<div class="gallery">

  <div class="gallery-item">
    <a class="gallery-title" href="/glycolysis/">Glycolysis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F001-glycolysis-alt.graphml">GraphML</a>
      <a href="/downloads/F001-glycolysis-alt-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/glycolysis/">
      <img class="gallery-image" src="/images/gallery/F001-glycolysis-vcut.png" alt="Glycolysis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/eicosanoids/">Eicosanoid production</a>
    <div class="gallery-downloads">
      <a href="/downloads/F002-eicosanoids.graphml">GraphML</a>
      <a href="/downloads/F002-eicosanoids-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/eicosanoids/">
      <img class="gallery-image" src="/images/gallery/F002-eicosanoids-vcut.png" alt="Eicosanoid production map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/mevalonate/">Mevalonate biosynthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F003-mevalonate.graphml">GraphML</a>
      <a href="/downloads/F003-mevalonate-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/mevalonate/">
      <img class="gallery-image" src="/images/gallery/F003-mevalonate-vcut.png" alt="Mevalonate biosynthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/glycogen/">Glycogen metabolism</a>
    <div class="gallery-downloads">
      <a href="/downloads/F004-glycogen-muscle.graphml">GraphML</a>
      <a href="/downloads/F004-glycogen-muscle-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/glycogen/">
      <img class="gallery-image" src="/images/gallery/F004-glycogen-muscle-vcut.png" alt="Glycogen metabolism map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/acly/">Acetyl-CoA synthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F006-ACLY.graphml">GraphML</a>
      <a href="/downloads/F006-ACLY.sbgn">SBGN-ML</a>
    </div>
    <a href="/acly/">
      <img class="gallery-image" src="/images/gallery/F006-ACLY-vcut.png" alt="Acetyl-CoA synthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/camp/">cAMP hydrolysis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F012-cAMP.graphml">GraphML</a>
      <a href="/downloads/F012-cAMP-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/camp/">
      <img class="gallery-image" src="/images/gallery/F012-cAMP-vcut.png" alt="cAMP hydrolysis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/inos/">iNOS pathway</a>
    <div class="gallery-downloads">
      <a href="/downloads/F007-inos.graphml">GraphML</a>
      <a href="/downloads/F007-inos-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/inos/">
      <img class="gallery-image" src="/images/gallery/F007-inos-vcut.png" alt="iNOS pathway map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/enos/">eNOS pathway</a>
    <div class="gallery-downloads">
      <a href="/downloads/F008-enos.graphml">GraphML</a>
      <a href="/downloads/F008-enos-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/enos/">
      <img class="gallery-image" src="/images/gallery/F008-enos-vcut.png" alt="eNOS pathway map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/carnitine/">Acyl-carnitine synthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F014-carnitine.graphml">GraphML</a>
      <a href="/downloads/F014-carnitine-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/carnitine/">
      <img class="gallery-image" src="/images/gallery/F014-carnitine-vcut.png" alt="Acyl-carnitine synthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/srebp/">SREBP signalling</a>
    <div class="gallery-downloads">
      <a href="/downloads/F005-SREBP.graphml">GraphML</a>
      <a href="/downloads/F005-SREBP.sbgn">SBGN-ML</a>
    </div>
    <a href="/srebp/">
      <img class="gallery-image" src="/images/gallery/F005-SREBP-vcut.png" alt="SREBP signalling map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/tag/">Triacylglycerol hydrolysis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F015-tag.graphml">GraphML</a>
      <a href="/downloads/F015-tag.sbgn">SBGN-ML</a>
    </div>
    <a href="/tag/">
      <img class="gallery-image" src="/images/gallery/F015-tag-vcut.png" alt="Triacylglycerol hydrolysis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/estrogen/">Estradiol biosynthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F018-estrogen.graphml">GraphML</a>
      <a href="/downloads/F018-estrogen.sbgn">SBGN-ML</a>
    </div>
    <a href="/estrogen/">
      <img class="gallery-image" src="/images/gallery/F018-estrogen-vcut.png" alt="Estradiol biosynthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/phosphoinositides/">Phosphoinositide</a>
    <div class="gallery-downloads">
      <a href="/downloads/F009-phosphoinositides.graphml">GraphML</a>
      <a href="/downloads/F009-phosphoinositides-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/phosphoinositides/">
      <img class="gallery-image" src="/images/gallery/F009-phosphoinositides-vcut.png" alt="Phosphoinositide map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/glutaminase/">Glutaminolysis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F019-glutaminase.graphml">GraphML</a>
      <a href="/downloads/F019-glutaminase.sbgn">SBGN-ML</a>
    </div>
    <a href="/glutaminase/">
      <img class="gallery-image" src="/images/gallery/F019-glutaminase-vcut.png" alt="Glutaminolysis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/pyrimidine/">Pyrimidine biosynthesis</a>
    <div class="gallery-downloads">
      <a href="/downloads/F020-pyrimidine.graphml">GraphML</a>
      <a href="/downloads/F020-pyrimidine.sbgn">SBGN-ML</a>
    </div>
    <a href="/pyrimidine/">
      <img class="gallery-image" src="/images/gallery/F020-pyrimidine-vcut.png" alt="Pyrimidine biosynthesis map">
    </a>
  </div>

  <div class="gallery-item">
    <a class="gallery-title" href="/aspirin/">Aspirin</a>
    <div class="gallery-downloads">
      <a href="/downloads/F100-aspirin-V003B.graphml">GraphML</a>
      <a href="/downloads/F100-aspirin-V003B-SBGNv02.sbgn">SBGN-ML</a>
    </div>
    <a href="/aspirin/">
      <img class="gallery-image" src="/images/gallery/F100-aspirin-cut.png" alt="Aspirin map">
    </a>
  </div>

</div>
