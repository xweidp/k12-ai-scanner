#!/usr/bin/env python3
"""
Build a single self-contained HTML block for pasting into a WordPress page.

Generated rather than hand-maintained so the WordPress copy can be rebuilt
whenever the standalone app changes: `python3 build-wordpress-embed.py`.

Three problems this has to solve:

1. CSS leakage. styles.css styles bare `body`, `button`, `input`, `select`,
   `a`, `h1`, `h2`, `p` and `label`. Pasted into a themed WordPress page those
   rules would restyle the whole site. Every selector is rescoped under
   `.k12-scanner`, and `:root` custom properties move onto that wrapper so
   they can't clash with theme variables.

2. Relative data path. The app fetches `data/k12_inventory_latest.csv`, which
   would resolve against k12-ai-infrastructure.org and 404. Rewritten to the
   absolute GitHub Pages URL, which serves `access-control-allow-origin: *`,
   so the page keeps reading whatever the monthly scan last committed.

3. Full-viewport layout. The standalone page is a 100vh two-column shell with
   its own sidebar. Inside a WordPress page that already has a header and nav,
   it needs to flow in the content column instead.
"""

import re
import sys
from pathlib import Path

CSV_URL = 'https://xweidp.github.io/k12-ai-scanner/data/k12_inventory_latest.csv'
WRAPPER = 'k12-scanner'
OUT = Path('wordpress-embed.html')

# Properties that only make sense on a real <body>; drop them when the body
# rule is rescoped onto the wrapper.
BODY_DROP = {'margin', 'min-height'}


def split_rules(css):
    """Yield (prelude, body, is_at_block) for each top-level CSS rule."""
    out, i, n = [], 0, len(css)
    while i < n:
        brace = css.find('{', i)
        if brace == -1:
            tail = css[i:].strip()
            if tail:
                out.append((tail, None, False))
            break
        prelude = css[i:brace].strip()
        # Match the closing brace, accounting for nesting (@media).
        depth, j = 1, brace + 1
        while j < n and depth:
            if css[j] == '{':
                depth += 1
            elif css[j] == '}':
                depth -= 1
            j += 1
        body = css[brace + 1:j - 1]
        out.append((prelude, body, prelude.startswith('@')))
        i = j
    return out


def scope_selector(sel):
    """Rescope one comma-separated selector list under the wrapper."""
    parts = []
    for raw in sel.split(','):
        s = raw.strip()
        if not s:
            continue
        if s in (':root', 'html'):
            parts.append(f'.{WRAPPER}')
        elif s == 'body':
            parts.append(f'.{WRAPPER}')
        elif s.startswith('*'):
            # `*` and `*, *::before` -> confine to inside the wrapper
            parts.append(f'.{WRAPPER} {s}')
        else:
            parts.append(f'.{WRAPPER} {s}')
    return ',\n'.join(parts)


def filter_body_props(body):
    kept = []
    for decl in body.split(';'):
        if not decl.strip():
            continue
        prop = decl.split(':', 1)[0].strip().lower()
        if prop in BODY_DROP:
            continue
        kept.append(decl.strip())
    return ';\n  '.join(kept) + (';' if kept else '')


def scope_css(css):
    lines = []
    for prelude, body, is_at in split_rules(css):
        if body is None:
            continue
        if is_at:
            # @media / @supports: scope the selectors inside, keep the prelude.
            inner = []
            for p2, b2, _ in split_rules(body):
                if b2 is None:
                    continue
                inner.append(f'{scope_selector(p2)} {{{b2}}}')
            lines.append(f'{prelude} {{\n' + '\n'.join(inner) + '\n}')
        else:
            b = filter_body_props(body) if prelude.strip() == 'body' else body
            lines.append(f'{scope_selector(prelude)} {{{b}}}')
    return '\n'.join(lines)


def extract_app_markup(html):
    """Pull the <main class="app-shell"> block out of index.html."""
    m = re.search(r'(<main class="app-shell".*?</main>)', html, re.S)
    if not m:
        sys.exit('ERROR: could not find <main class="app-shell"> in index.html')
    return m.group(1)


def pair_filter_fields(markup):
    """Wrap each <label>+<select> pair in a .field div.

    In the sidebar layout the label and select are flat siblings stacked
    vertically, which is fine. Laid out as a horizontal grid, each becomes its
    own grid cell and the labels stagger away from their controls. Grid can't
    group flat siblings, so pair them in the markup instead.
    """
    pattern = re.compile(
        r'(<label for="(\w+)">.*?</label>)\s*(<select id="\2">.*?</select>)',
        re.S)
    paired, n = pattern.subn(
        lambda m: f'<div class="field">{m.group(1)}{m.group(3)}</div>', markup)
    if n < 4:
        sys.exit(f'ERROR: expected to pair >=4 filter fields, paired {n}')
    print(f'  paired {n} label/select fields for the horizontal filter row')
    return paired


def main():
    css = Path('styles.css').read_text()
    js = Path('app.js').read_text()
    html = Path('index.html').read_text()

    scoped = scope_css(css)

    # Sanity check: no bare element selector may survive at top level.
    leaks = re.findall(r'(?m)^(body|html|button|input|select|a|h1|h2|p|label|\*)\s*[,{]',
                       scoped)
    if leaks:
        sys.exit(f'ERROR: unscoped selectors would leak into the theme: {set(leaks)}')

    # Point the fetch at GitHub Pages so the monthly scan still flows through.
    js2, n = re.subn(r"fetch\('data/k12_inventory_latest\.csv\?v=' \+ v\)",
                     f"fetch('{CSV_URL}?v=' + v)", js)
    if n != 1:
        sys.exit(f'ERROR: expected exactly 1 CSV fetch to rewrite, found {n}')

    markup = pair_filter_fields(extract_app_markup(html))

    out = f"""<!-- ============================================================
     Public Goods for AI in K-12 Education Scanner
     Generated by build-wordpress-embed.py - do not edit by hand.
     Re-run that script and re-paste if the scanner changes.

     Data is read live from GitHub Pages, so the monthly scan
     (1st of each month) appears here automatically with no
     edit to this page.
     ============================================================ -->
<div class="{WRAPPER}">
<style>
/* All selectors scoped to .{WRAPPER} so nothing touches the site theme. */
.{WRAPPER} {{ box-sizing: border-box; }}
/* Inherit the page's own background instead of the standalone app's gradient,
   so the block reads as part of the page rather than a pasted-in panel. */
.{WRAPPER} {{ background: none !important; }}
.{WRAPPER} .sidebar,
.{WRAPPER} .results {{ background: transparent !important; }}
/* A sidebar-width call-to-action button becomes a full-width bar up top. */
.{WRAPPER} .button-row {{ flex-direction: row !important; }}
.{WRAPPER} .button-row a {{ display: inline-block !important; width: auto; }}

/* A WordPress content column is far narrower than the standalone app's full
   viewport. Keeping the left sidebar would steal ~300px from a ~1180px column
   and clip the table, so the filters run across the top instead and the table
   gets the entire width. */
.{WRAPPER} .app-shell {{
  display: block !important;
  min-height: 0 !important;
}}
.{WRAPPER} .sidebar {{
  border-right: 0 !important;
  border-bottom: 1px solid var(--line);
  padding: 0 0 20px !important;
  margin-bottom: 22px;
  overflow: visible !important;
  background: transparent !important;
}}
.{WRAPPER} .workspace {{ padding: 0 !important; }}
.{WRAPPER} .results {{ overflow-x: auto; }}

/* Intro text spans the width; filters sit in a responsive row beneath it. */
.{WRAPPER} .brand-block {{ margin-bottom: 20px !important; }}
.{WRAPPER} .research-areas {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px 18px;
  align-items: start;
  border-top: 0 !important;
  padding-top: 0 !important;
}}
.{WRAPPER} .research-areas > h2 {{ grid-column: 1 / -1; margin-bottom: 0; }}
.{WRAPPER} .field label {{ margin-top: 0 !important; }}
.{WRAPPER} .research-areas .toggle-group {{ align-self: end; margin-top: 0; }}
.{WRAPPER} .research-areas .score-grid {{
  grid-column: 1 / -1;
  grid-template-columns: repeat(4, 1fr);
}}
/* Panels that only made sense in a vertical sidebar. */
.{WRAPPER} .status-panel {{ display: none !important; }}

@media (max-width: 700px) {{
  .{WRAPPER} .research-areas .score-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}

{scoped}
</style>

{markup}

<script>
{js2}
</script>
</div>
"""
    OUT.write_text(out)
    kb = len(out) / 1024
    print(f'Wrote {OUT} ({kb:.0f} KB)')
    print(f'  CSS rescoped under .{WRAPPER}, no leaking element selectors')
    print(f'  CSV source: {CSV_URL}')


if __name__ == '__main__':
    main()
