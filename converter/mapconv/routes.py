# Which files each input gives, as on the Converter page, for the page, the command line and the
# reference files alike. outputs() lists them; each file is made only when asked (made()).
#   GraphML: CellDesigner and SBGN-ML, straight and advanced, SBGN-ML also each for Newt
#            (newt_layout); GraphML (corrected) for a map drawn
#            with other shapes; GraphML (marked) when it breaks a rule (the problems left out)
#   CellDesigner: GraphML and SBGN-ML, straight and advanced, SBGN-ML also each for Newt
#   SBGN-ML, Newt: GraphML; CellDesigner, straight and advanced
#   CellDesigner, SBGN-ML, Newt: also GraphML (standard sizes) for a map drawn at another scale,
#            or for every map when standard (style.standard; user, 2026-10-20)
#   GraphML: GraphML (standard sizes) only when standard (user, 2026-10-22)
import contextlib, io
from dataclasses import dataclass
from . import annotation, celldesigner, graphml, report, rules, sbgnml, style
from .layout import at_centres

LAYOUTS = ('straight', 'advanced')


@dataclass
class Output:
    ending: str     # after the input's base name: -advanced.xml
    label: str      # the page's button: CellDesigner (advanced)
    make: object    # () -> the file's text, or None when the input gives no such file
    red: bool = False  # the page's red button: the map with its problems marked


def made(o):
    # (text or None, messages): the file and what the converter said making it, or why it failed,
    # each message (kind, text); printed lines first, kind None (v1, run by tools/reference.py
    # whole, prints its messages)
    printed = io.StringIO()
    with report.collect() as said, contextlib.redirect_stdout(printed):
        try:
            text = o.make()
        except (Exception, SystemExit) as e:
            text = None
            said.append(('left out', 'Not converted: %s: %s' % (type(e).__name__, e)))
    return text, [(None, l) for l in printed.getvalue().splitlines()] + said


def standardised(read, program, asked):
    # GraphML (standard sizes), None for a map at the usual scale unless asked; the reader's messages
    # are the plain GraphML's
    with report.collect(), contextlib.redirect_stdout(io.StringIO()):
        m = read()
    t = style.standard(m, program, asked)
    return graphml.write(t) if t else None


def outputs(path, standard=False):
    ext = path.lower().rsplit('.', 1)[-1]
    # SBGN-ML straight and advanced, then each for Newt (user, 2026-10-21); read(layout) -> the map
    sbgn = lambda read: [Output('-%s%s.sbgn' % (l, '-newt' * n), 'SBGN-ML (%s%s)' % (l, ', for Newt' * n),
                                lambda l=l, n=n: sbgnml.write(read(l), l, n)) for n in (False, True) for l in LAYOUTS]
    std = lambda read, program: Output('-standard.graphml', 'GraphML (standard sizes)', lambda: standardised(read, program, standard))
    to_cd = lambda m, layout: celldesigner.write(m, annotation.from_graphml(m), layout)
    if ext == 'graphml':
        try:
            with report.collect():
                found = rules.problems(graphml.read(path))
        except Exception:
            return [Output('', '', lambda: rules.problems(graphml.read(path)))]  # made() says why
        read = lambda: rules.clean(graphml.read(path), found)  # a fresh copy for each file

        def marked():
            with report.collect():
                m = graphml.read(path)
            for line in rules.lines(m, found):
                report.say('problem', line)
            return rules.mark(path, found)
        out = [Output('-%s.xml' % l, 'CellDesigner (%s)' % l, lambda l=l: to_cd(read(), l)) for l in LAYOUTS] + \
              sbgn(lambda l: read()) + \
              [Output('-corrected.graphml', 'GraphML (corrected)', lambda: graphml.corrected(read()))] + \
              ([Output('-standard.graphml', 'GraphML (standard sizes)', lambda: graphml.write(style.standardise(read())))] if standard else [])
        return out + ([Output('-marked.graphml', 'GraphML (marked)', marked, red=True)] if found else [])
    if ext == 'xml':
        cd = lambda l: at_centres(celldesigner.read(path)) if l == 'straight' else celldesigner.read(path)
        return [Output('-%s.graphml' % l, 'GraphML (%s)' % l, lambda l=l: graphml.write(cd(l))) for l in LAYOUTS] + \
               [std(lambda: celldesigner.read(path), 'CellDesigner')] + \
               sbgn(lambda l: celldesigner.straight(cd(l)) if l == 'straight' else cd(l))
    return [Output('.graphml', 'GraphML', lambda: graphml.write(sbgnml.read(path))), std(lambda: sbgnml.read(path), 'Newt')] + \
           [Output('-%s.xml' % l, 'CellDesigner (%s)' % l, lambda l=l: to_cd(sbgnml.read(path), l)) for l in LAYOUTS]
