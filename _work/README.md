# Working area (not published)

Jekyll skips folders that start with `_` unless they are collections, so
nothing here appears on the website. The folder is still visible in the
public GitHub repository.

- `tools/`: helpers for yEd SBGN graphml files (Python 3, lxml; cairosvg for PNG previews).
  - `ygml.py`: parser (nodes, edges, geometry, ports, bends).
  - `check.py`: overlaps, edges through nodes, crossings, orthogonal share, aspect ratio.
  - `render.py`: approximate SBGN preview as PNG or SVG, whole map or a crop.
- `F001-glycolysis/`: one folder per map in progress, with its regulation table,
  references, sources and versions. See its README.
