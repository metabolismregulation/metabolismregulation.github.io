import re, sys
import yrender


def graphml(s):
    counts = {}

    def node(m):
        b = m.group(0)
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
        b = re.sub(r'<y:Fill\b[^>]*hasColor="false"[^>]*/>', '<y:Fill color="#000000" transparent="false"/>', b)
        return re.sub(r'(<y:Fill color=")#[0-9A-Fa-f]+(")', r'\1#{%s}\2' % role, b)

    s = re.sub(r'<data key="[^"]+">\s*<y:(?:GenericNode|ProxyAutoBoundsNode|GroupNode)\b.*?</data>', node, s, flags=re.S)
    s = re.sub(r'(<y:Fill color=")#FFFFFF(")', r'\1#{white}\2', s)
    s = re.sub(r'backgroundColor="#FFFFFF(7F)?"', lambda m: 'backgroundColor="#{white}%s"' % (m.group(1) or ''), s)
    s = re.sub(r'(<y:(?:BorderStyle|LineStyle) color=")#000000(")', r'\1#{ink}\2', s)
    s = s.replace('lineColor="#000000"', 'lineColor="#{ink}"')
    s = s.replace('textColor="#000000"', 'textColor="#{text}"')
    left = re.findall(r'color="#[0-9A-Fa-f]{6}', s)
    return s, 'yEd nodes by role %s | hex colours left: %d | names on fills: %d' % (
        counts, len(left), len(re.findall(r'textColor="#\{t_', s)))


CLASS = {'PROTEIN': 'protein', 'RECEPTOR': 'protein', 'ION_CHANNEL': 'protein', 'TRUNCATED': 'protein',
         'SIMPLE_MOLECULE': 'metabolite', 'ION': 'metabolite', 'DRUG': 'metabolite',
         'GENE': 'gene', 'RNA': 'gene', 'ANTISENSE_RNA': 'gene', 'COMPLEX': 'complex'}


def celldesigner(s):
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
