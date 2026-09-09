#!/usr/bin/env python3
"""
Run the Classic Editor build through a port of WordPress's wpautop() and
verify it comes out intact.

The Classic Editor pipes post content through wpautop, which inserts <p> and
<br /> tags around newlines. Applied to inline CSS or JS that corrupts the
block silently - it renders, but the script is broken. The site will not have
the block editor enabled, so this is the only path available and it needs
proof rather than optimism.

Port follows wp-includes/formatting.php: wpautop(). Faithful on the parts that
matter here (block-tag newline injection, paragraph splitting, <br>
conversion, and the script/style preservation helper).
"""

import re
import sys
from pathlib import Path

ALLBLOCKS = ('(?:table|thead|tfoot|caption|col|colgroup|tbody|tr|td|th|div|dl'
             '|dd|dt|ul|ol|li|pre|form|map|area|blockquote|address|style|p'
             '|h[1-6]|hr|fieldset|legend|section|article|aside|hgroup|header'
             '|footer|nav|figure|figcaption|details|menu|summary)')


def wpautop(pee, br=True):
    """Port of WordPress wpautop()."""
    if pee.strip() == '':
        return ''

    pee = pee + '\n'
    pee = pee.replace("\r\n", "\n").replace("\r", "\n")

    # Protect <pre>.
    pre_tags = {}
    if '<pre' in pee:
        parts = re.split(r'(<pre[^>]*>.*?</pre>)', pee, flags=re.S)
        pee = ''
        for i, part in enumerate(parts):
            if part.startswith('<pre'):
                key = f'<pre wp-pre-tag-{i}></pre>'
                pre_tags[key] = part
                pee += key
            else:
                pee += part

    # Newlines around block elements.
    pee = re.sub(r'<br />\s*<br />', "\n\n", pee)
    pee = re.sub(r'(<' + ALLBLOCKS + r'[\s/>])', r"\n\1", pee)
    pee = re.sub(r'(</' + ALLBLOCKS + r'>)', r"\1\n\n", pee)
    pee = pee.replace("\n\n\n", "\n\n")

    # Paragraphs.
    pee = re.sub(r'\n\n+', "\n\n", pee)
    pees = [p for p in re.split(r'\n\s*\n', pee) if p.strip() != '']
    pee = ''.join(f'<p>{p.strip()}</p>\n' for p in pees)
    pee = re.sub(r'<p>\s*</p>', '', pee)
    pee = re.sub(r'<p>([^<]+)</(div|address|form)>', r'<p>\1</p></\2>', pee)
    pee = re.sub(r'<p>\s*(</?' + ALLBLOCKS + r'[^>]*>)\s*</p>', r'\1', pee)
    pee = re.sub(r'<p>(<li.+?)</p>', r'\1', pee)
    pee = re.sub(r'<p><blockquote([^>]*)>', r'<blockquote\1><p>', pee, flags=re.I)
    pee = pee.replace('</blockquote></p>', '</p></blockquote>')
    pee = re.sub(r'<p>\s*(</?' + ALLBLOCKS + r'[^>]*>)', r'\1', pee)
    pee = re.sub(r'(</?' + ALLBLOCKS + r'[^>]*>)\s*</p>', r'\1', pee)

    if br:
        # Preserve newlines inside <script> and <style> before <br> insertion.
        def preserve(m):
            return m.group(0).replace("\n", '<WPPreserveNewline />')
        pee = re.sub(r'<(script|style).*?</\1>', preserve, pee, flags=re.S)
        pee = re.sub(r'(?<!<br />)\s*\n', "<br />\n", pee)
        pee = pee.replace('<WPPreserveNewline />', "\n")

    pee = re.sub(r'(</?' + ALLBLOCKS + r'[^>]*>)\s*<br />', r'\1', pee)
    pee = re.sub(r'<br />(\s*</?(?:p|li|div|dl|dd|dt|th|pre|td|ul|ol)[^>]*>)',
                 r'\1', pee)
    pee = re.sub(r'\n</p>$', '</p>', pee)

    for key, val in pre_tags.items():
        pee = pee.replace(key, val)

    return pee


def extract(tag, html):
    m = re.search(rf'<{tag}[^>]*>(.*?)</{tag}>', html, re.S)
    return m.group(1) if m else ''


def main():
    src = Path('wordpress-embed-classic.html')
    if not src.exists():
        sys.exit('Run build-wordpress-embed.py first')
    original = src.read_text()

    print(f'Input: {len(original)/1024:.0f} KB, '
          f'{original.count(chr(10))} newlines\n')

    out = wpautop(original)

    css_before, css_after = extract('style', original), extract('style', out)
    js_before, js_after = extract('script', original), extract('script', out)

    problems = []
    for label, before, after in (('CSS', css_before, css_after),
                                 ('JS', js_before, js_after)):
        if not after:
            problems.append(f'{label}: block disappeared entirely')
            continue
        for junk in ('<br />', '<br>', '<p>', '</p>'):
            if junk in after and junk not in before:
                n = after.count(junk)
                problems.append(f'{label}: wpautop injected {n} x "{junk}"')
        if after != before:
            problems.append(f'{label}: content changed '
                            f'({len(before)} -> {len(after)} chars)')

    print('=== wpautop result ===')
    print(f'  CSS block: {len(css_before)} -> {len(css_after)} chars')
    print(f'  JS block:  {len(js_before)} -> {len(js_after)} chars')

    if problems:
        print('\n❌ CORRUPTED:')
        for p in problems:
            print(f'   - {p}')
        Path('/tmp/wpautop_out.html').write_text(out)
        print('\n   full output written to /tmp/wpautop_out.html')
        return 1

    print('\n✅ CSS and JS pass through wpautop byte-for-byte unchanged.')
    print('   Safe to paste into the Classic Editor Text tab.')
    Path('/tmp/wpautop_out.html').write_text(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
