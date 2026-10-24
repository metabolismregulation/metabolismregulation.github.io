  // the converter's files that a page loads into Python (Pyodide): converter/mapconv/, copied there by
  // map-converter's tools/to_website.sh; used by /converter/ and /colours/
  window.MAPCONV = {
    base: '{{ "/converter/mapconv/" | relative_url }}',
    modules: ['model', 'report', 'graphml', 'annotation', 'biology', 'celldesigner', 'cd_layout', 'layout', 'newt_layout',
              'cd_tidy', 'style', 'sbgnml', 'rules', 'routes'],
    data: ['yed.graphml', 'conjugates.json']  // the yEd templates; ChEBI's conjugate acids and bases
  };
