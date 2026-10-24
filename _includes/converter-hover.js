  // the buttons' hover texts (user, 2026-10-21), shared by /converter/ and /ysbgn-js/: a button with
  // only its main word says what its file holds, a button with more words says what each adds, one
  // line per word ("plain: ..."), then the file's name
  const HOVER_MAIN = {
    'CellDesigner': 'Process glyphs, bends and modifier arcs where the input map has them. A few nodes moved slightly so that lines meet straight, listed under the map.',
    'GraphML from CellDesigner': 'Node sizes as in CellDesigner, arcs at its connection points, modifier arcs ending beside the process glyph.',
    'GraphML from SBGN-ML': 'Node positions, sizes and bends as in the SBGN-ML file.',
    'SBGN-ML': 'Compartments enlarged and moved apart, so that Newt keeps them as drawn.',
    'Open in Newt': 'Opens the file in Newt, in a new tab.',
  };
  const HOVER_WORD = {
    'newt-adjusted': 'newt-adjusted: compartments enlarged and moved apart, so that Newt keeps them as drawn.',
    'plain': 'plain: compartments as drawn, not adjusted for any tool.',
    'straight line': 'straight line: every arc a straight line between node centres.',
    'straight & bends': 'straight & bends: straight lines with the key bends of the input map, no node moved.',
    'as drawn': 'as drawn: every node and process glyph where the input map has it, held by extra edit points.',
    'standard sizes': 'standard sizes: proteins 80 x 40, metabolites 40 x 40, the map rescaled to match.',
    'corrected': 'corrected: the map redrawn in the SBGN palette, its shapes recognised by their outline.',
    'marked': 'marked: the elements that break the SBGN rules drawn red. yEd shows the reason on hover.',
  };
  // format and variant as on the button ("SBGN-ML", "plain, straight line"), the dropped file's name,
  // the file's name
  function hover(format, variant, input, name) {
    const words = variant ? variant.split(', ') : [];
    const from = /\.xml$/i.test(input) ? ' from CellDesigner' : /\.(sbgn|nwt)$/i.test(input) ? ' from SBGN-ML' : '';
    const main = HOVER_MAIN[format + from] || HOVER_MAIN[format];
    const lines = words.map(w => (HOVER_WORD[w] || '') +
      (w === 'straight line' && format === 'CellDesigner' ? ' The process glyph sits midway between the main reactant and product.' : ''));
    return [!words.length || format === 'Open in Newt' ? main : '', ...lines, name].filter(Boolean).join('\n');
  }
