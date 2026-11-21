import contextlib, io
from dataclasses import dataclass
from . import annotation, celldesigner, graphml, report, rules, sbgnml, style
from .layout import aligned, at_centres

LAYOUTS = ('straight', 'advanced')


@dataclass
class Output:
    ending: str
    label: str
    make: object
    red: bool = False


def made(o):
    printed = io.StringIO()
    with report.collect() as said, contextlib.redirect_stdout(printed):
        try:
            text = o.make()
        except (Exception, SystemExit) as e:
            text = None
            said.append(('left out', 'Not converted: %s: %s' % (type(e).__name__, e)))
    return text, [(None, l) for l in printed.getvalue().splitlines()] + said


def standardised(read, program, asked):
    with report.collect(), contextlib.redirect_stdout(io.StringIO()):
        m = read()
    t = style.standard(m, program, asked)
    return graphml.write(t) if t else None


def outputs(path, standard=False):
    ext = path.lower().rsplit('.', 1)[-1]
    sbgn = lambda read: [Output('-%s%s.sbgn' % (l, '-newt' * n), 'SBGN-ML (%s%s)' % (l, ', for Newt' * n),
                                lambda l=l, n=n: sbgnml.write(read(l), l, n)) for n in (False, True) for l in LAYOUTS]
    std = lambda read, program: Output('-standard.graphml', 'GraphML (standard sizes)', lambda: standardised(read, program, standard))
    name = {'straight': 'straight', 'bends': 'straight & bends', 'advanced': 'advanced', 'drawn': 'as drawn'}
    cds = lambda read: [Output('-%s.xml' % l, 'CellDesigner (%s)' % name[l],
                               lambda l=l: (lambda m: celldesigner.write(m, annotation.from_graphml(m), l))(read()))
                        for l in celldesigner.LAYOUTS]
    if ext == 'graphml':
        try:
            with report.collect():
                found = rules.problems(graphml.read(path))
        except Exception:
            return [Output('', '', lambda: rules.problems(graphml.read(path)))]
        read = lambda: rules.clean(graphml.read(path), found)

        def marked():
            with report.collect():
                m = graphml.read(path)
            for line in rules.lines(m, found):
                report.say('problem', line)
            return rules.mark(path, found)
        out = cds(read) + sbgn(lambda l: read()) + \
              [Output('-corrected.graphml', 'GraphML (corrected)', lambda: graphml.corrected(read()))] + \
              ([Output('-standard.graphml', 'GraphML (standard sizes)', lambda: graphml.write(style.standardise(read()), soft=True))] if standard else [])
        return out + ([Output('-marked.graphml', 'GraphML (marked)', marked, red=True)] if found else [])
    if ext == 'xml':
        cd = lambda l: at_centres(aligned(celldesigner.read(path))) if l == 'straight' else aligned(celldesigner.read(path))
        return [Output('-%s.graphml' % l, 'GraphML (%s)' % l, lambda l=l: graphml.write(cd(l))) for l in LAYOUTS] + \
               [std(lambda: celldesigner.read(path), 'CellDesigner')] + \
               sbgn(lambda l: celldesigner.straight(cd(l)) if l == 'straight' else cd(l))
    return [Output('.graphml', 'GraphML', lambda: graphml.write(sbgnml.read(path))), std(lambda: sbgnml.read(path), 'Newt')] + \
           cds(lambda: sbgnml.read(path))
