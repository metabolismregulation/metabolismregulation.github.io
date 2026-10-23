---
paths:
  - "_projects/**"
  - "draftpages/**"
  - "index.html"
  - "_data/contributors.yml"
  - "_includes/contributors.html"
---

## Map pages

A map whose connection was chosen from the Reactome-Recon lists says so visibly on its page (user,
2026-10-14): a section "Reactome-Recon connection" above the Description, naming the
Reactome processes (linked). The Atlas list has no tag for it (the "lists" tag was removed, user
2026-10-17).

Map pages, drafts too (user, 2026-10-17): no "Downloads:" word, the links in the order GraphML, PNG, SVG,
CellDesigner, SBML, SBGN-ML, Annotation, Newt, MINERVA (a file missing in `downloads/` is left out), each
file with the download icon after its name (an inline SVG, copied from an existing map page; the include file was removed, user 2026-10-17), Newt and MINERVA with
`{% include icon-external.html %}` after it. The Gallery links carry the same icons.

## Home page

The pathway highlight on the home page (`index.html`) is chosen by `highlight:` in its front
matter, the permalink of a `_projects/` page (e.g. `/glycolysis/`). Its title, links and image
are taken from that page (everything before its first section heading), so they change with it.
Never copy them into `index.html` by hand.

## Contributors

People, their affiliations and ORCID iDs are in `_data/contributors.yml`
(names and each person's affiliations as in the manuscript author list, so
they can be checked against it in one place; institutions end with town and
country, without street addresses or postcodes). A map page lists people in its
front matter, one per line (`contributors:` then `  - alexander-mazein`), and
shows them under `## Contributors`, the last section of the page after the References (user,
2026-10-16), with `{% include contributors.html %}`:
names with affiliation numbers, then a closed "Affiliations" list (user,
2026-10-15). A page can give a person other affiliations for that map only:
`  - alexander-mazein: [lcsb]`. A new map with no other contributors
gets `  - alexander-mazein: [lih-cancer]` (user, 2026-10-15). Key:
first and family name, lowercase, hyphens, no accents; a key never changes
once used. Contributions are not recorded separately: the map pages are the
record. Add an ORCID only after checking it on orcid.org.

## Map image size on the pages

Every map page shows its map at the same zoom, so a protein node (80 x 40 yEd units) looks
the same size on every page (user; first set in commit 64daf5d, 2026-10-11). yEd exports
SVG at 1:1 (one pixel per yEd unit), so the image `width` on the page is the SVG's own
width times the common zoom: 0.67 (a protein about 54 px wide), the level of most pages
(e.g. 892 -> 600, 1541 -> 1030). This holds only for SVGs exported from yEd the same way
(1:1, default margin), as all current ones are. For any other image (PNG, another program,
another export setting) measure a protein node in the image and set the width so it comes
out at about 54 px. Never copy a width from another page. Exceptions to look
at with the user: iNOS (0.75), eNOS (0.60), glycogen (two maps, 0.43).

