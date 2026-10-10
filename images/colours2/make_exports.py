# Build the export templates for /colours/ from the iNOS map files.
# Usage: python3 images/colours2/make_exports.py
# Reads downloads/F007-inos.graphml and downloads/F007-inos.xml once and writes
# images/colours2/F007-inos.template.graphml and F007-inos.template.xml, where
# every colour the page controls is replaced by a role placeholder such as
# {protein}. The page fills the placeholders with the current theme when a
# download button is clicked; the files in downloads/ are not used by the page.
# Roles are decided by element type, not by colour, because several roles
# share white in the source files.
import re, sys

SRC = 'downloads/F007-inos'
OUT = 'images/colours2/F007-inos.template'


def graphml():
    s = open(SRC + '.graphml', encoding='utf-8').read()
    counts = {}

    def node(m):
        b = m.group(0)
        kind = re.search(r'<y:(GenericNode|ProxyAutoBoundsNode)', b)
        conf = re.search(r'configuration="com\.yworks\.sbgn\.([A-Za-z]+)"', b)
        fills = re.findall(r'<y:Fill color="#([0-9A-Fa-f]+)"', b)
        if not kind:
            sys.exit('unexpected node graphics')
        if kind.group(1) == 'ProxyAutoBoundsNode':
            role = 'compartment' if fills[0].upper().startswith('EDEBE4') else 'complex'
        else:
            role = {'Macromolecule': 'hlProtein' if fills[0].upper() == 'E2ACA3' else 'protein',
                    'SimpleChemical': 'metabolite', 'Process': 'white', 'EmptySet': 'white',
                    'Operator': 'white', 'NucleicAcidFeature': 'gene'}[conf.group(1)]
        counts[role] = counts.get(role, 0) + 1
        # every fill of the node, both states of a group, becomes the role colour (opaque)
        return re.sub(r'(<y:Fill color=")#[0-9A-Fa-f]+(")', r'\1#{%s}\2' % role, b)

    s = re.sub(r'<data key="d14">.*?</data>', node, s, flags=re.S)
    # label icons (units of information, state variables) in the resources
    s = re.sub(r'(<y:Fill color=")#FFFFFF(")', r'\1#{white}\2', s)
    # label backgrounds keep their transparency
    s = re.sub(r'backgroundColor="#FFFFFF(7F)?"', lambda m: 'backgroundColor="#{white}%s"' % (m.group(1) or ''), s)
    s = re.sub(r'(<y:(?:BorderStyle|LineStyle) color=")#000000(")', r'\1#{ink}\2', s)
    s = s.replace('lineColor="#000000"', 'lineColor="#{ink}"')
    s = s.replace('textColor="#000000"', 'textColor="#{text}"')
    left = re.findall(r'color="#[0-9A-Fa-f]{6}', s)
    open(OUT + '.graphml', 'w', encoding='utf-8').write(s)
    print('yEd nodes by role', counts, '| hex colours left:', len(left))


def celldesigner():
    s = open(SRC + '.xml', encoding='utf-8').read()
    cls = {}
    for m in re.finditer(r'<(species|celldesigner:species) [^>]*id="([^"]+)".*?</\1>', s, re.S):
        c = re.search(r'<celldesigner:class>([A-Z_]+)</celldesigner:class>', m.group(0))
        cls[m.group(2)] = c.group(1) if c else None
    counts = {}

    def alias(m):
        b = m.group(0)
        c = cls[m.group(3)]
        brief = re.search(r'<celldesigner:briefView>.*?<celldesigner:paint color="([^"]+)"', b, re.S)
        role = {'PROTEIN': 'hlProtein' if brief and brief.group(1).lower() == 'ffe2aca3' else 'protein',
                'SIMPLE_MOLECULE': 'metabolite', 'GENE': 'gene', 'RNA': 'gene',
                'COMPLEX': 'complex', 'DEGRADED': 'white'}[c]
        counts[role] = counts.get(role, 0) + 1
        # only the usual view is drawn; the brief view is left as it was
        return re.sub(r'(<celldesigner:usualView>.*?<celldesigner:paint color=")[0-9a-fA-F]{8}(")',
                      r'\1ff{%s}\2' % role, b, count=1, flags=re.S)

    s = re.sub(r'<celldesigner:(speciesAlias|complexSpeciesAlias) id="([^"]+)" species="([^"]+)".*?</celldesigner:\1>',
               alias, s, flags=re.S)
    s = re.sub(r'(<celldesigner:line [^>]*color=")ff000000(")', r'\1ff{ink}\2', s)
    open(OUT + '.xml', 'w', encoding='utf-8').write(s)
    print('CellDesigner aliases by role', counts)


graphml()
celldesigner()
