# Build the export templates for the website's /colours/ page from a map's files.
# Usage: python3 tools/colours_templates.py <website>/downloads/F001-glycolysis <website>/images/colours2/F001-glycolysis
# Reads <map>.graphml and <map>.xml once and writes <out>.template.graphml and
# <out>.template.xml. The page also runs graphml() and celldesigner() on a map dropped on it
# (its copy in the website's yrender/). In a template
# every colour the page controls is replaced by a role placeholder such as
# {protein}. The page fills the placeholders with the current theme when a
# download button is clicked; the files in downloads/ are not used by the page.
# Roles are decided by element type, not by colour, because several roles
# share white in the source files.
# yEd names written on a node's fill get {t_<role>} for their colour and
# {f_<role>} for plain or bold, so that dark fills can take white bold text
# as on the page; labels on their own boxes and edge labels keep {text}.
import re, sys
import yrender  # the role table


def graphml(s):
    # the GraphML text -> (template, what it did)
    counts = {}

    def node(m):
        b = m.group(0)
        # the first realizer: a group's open state
        tag = re.search(r'<y:(GenericNode|GenericGroupNode|GroupNode)\b', b).group(1)
        conf = re.search(r'configuration="com\.yworks\.sbgn\.([A-Za-z]+)"', b)
        fill = re.search(r'<y:Fill color="(#[0-9A-Fa-f]+)"', b)
        role = yrender.role(tag, conf and conf.group(1), fill and fill.group(1))
        counts[role] = counts.get(role, 0) + 1

        def label(lm):
            a = lm.group(0)
            if 'backgroundColor=' in a or 'hasText="false"' in a or 'iconData=' in a:
                return a
            return (a.replace('textColor="#000000"', 'textColor="#{t_%s}"' % role)
                     .replace('fontStyle="plain"', 'fontStyle="{f_%s}"' % role))
        b = re.sub(r'<y:NodeLabel\b[^>]*>', label, b)
        # every fill of the node, both states of a group, becomes the role colour (opaque), also a
        # fill without colour (SBGN-ML has none)
        b = re.sub(r'<y:Fill\b[^>]*hasColor="false"[^>]*/>', '<y:Fill color="#000000" transparent="false"/>', b)
        return re.sub(r'(<y:Fill color=")#[0-9A-Fa-f]+(")', r'\1#{%s}\2' % role, b)

    # the node graphics, whatever key the file gives them
    s = re.sub(r'<data key="[^"]+">\s*<y:(?:GenericNode|ProxyAutoBoundsNode|GroupNode)\b.*?</data>', node, s, flags=re.S)
    # label icons (units of information, state variables) in the resources
    s = re.sub(r'(<y:Fill color=")#FFFFFF(")', r'\1#{white}\2', s)
    # label backgrounds keep their transparency
    s = re.sub(r'backgroundColor="#FFFFFF(7F)?"', lambda m: 'backgroundColor="#{white}%s"' % (m.group(1) or ''), s)
    s = re.sub(r'(<y:(?:BorderStyle|LineStyle) color=")#000000(")', r'\1#{ink}\2', s)
    s = s.replace('lineColor="#000000"', 'lineColor="#{ink}"')
    s = s.replace('textColor="#000000"', 'textColor="#{text}"')
    left = re.findall(r'color="#[0-9A-Fa-f]{6}', s)
    return s, 'yEd nodes by role %s | hex colours left: %d | names on fills: %d' % (
        counts, len(left), len(re.findall(r'textColor="#\{t_', s)))


# CellDesigner classes by role, as the converter reads them; others (phenotype, unknown,
# degraded) white
CLASS = {'PROTEIN': 'protein', 'RECEPTOR': 'protein', 'ION_CHANNEL': 'protein', 'TRUNCATED': 'protein',
         'SIMPLE_MOLECULE': 'metabolite', 'ION': 'metabolite', 'DRUG': 'metabolite',
         'GENE': 'gene', 'RNA': 'gene', 'ANTISENSE_RNA': 'gene', 'COMPLEX': 'complex'}


def celldesigner(s):
    # the CellDesigner text -> (template, what it did)
    cls = {}
    for m in re.finditer(r'<(species|celldesigner:species) [^>]*id="([^"]+)".*?</\1>', s, re.S):
        c = re.search(r'<celldesigner:class>([A-Z_]+)</celldesigner:class>', m.group(0))
        cls[m.group(2)] = c.group(1) if c else None
    counts = {}

    def alias(m):
        b = m.group(0)
        c = cls[m.group(3)]
        brief = re.search(r'<celldesigner:briefView>.*?<celldesigner:paint color="([^"]+)"', b, re.S)
        role = CLASS.get(c, 'white')
        if role == 'protein' and brief and brief.group(1).lower() == 'ffe2aca3':
            role = 'hlProtein'
        counts[role] = counts.get(role, 0) + 1
        # only the usual view is drawn; the brief view is left as it was
        return re.sub(r'(<celldesigner:usualView>.*?<celldesigner:paint color=")[0-9a-fA-F]{8}(")',
                      r'\1ff{%s}\2' % role, b, count=1, flags=re.S)

    s = re.sub(r'<celldesigner:(speciesAlias|complexSpeciesAlias) id="([^"]+)" species="([^"]+)".*?</celldesigner:\1>',
               alias, s, flags=re.S)
    s = re.sub(r'(<celldesigner:line [^>]*color=")ff000000(")', r'\1ff{ink}\2', s)
    return s, 'CellDesigner aliases by role %s' % counts


if __name__ == '__main__':
    for ext, make in (('graphml', graphml), ('xml', celldesigner)):
        t, said = make(open('%s.%s' % (sys.argv[1], ext), encoding='utf-8').read())
        open('%s.template.%s' % (sys.argv[2], ext), 'w', encoding='utf-8').write(t)
        print(said)
