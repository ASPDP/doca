"""Shared pre/post-processing utilities for all converters."""
import os
import base64
import re
import urllib.parse


def extract_images(soup, output_dir):
    """Extract base64 data: URI images to files, replace src with relative paths.

    Saves images to <output_dir>/images/ and updates <img> src attributes.
    """
    img_dir = os.path.join(output_dir, 'images')
    count = 0

    for img in soup.find_all('img', src=True):
        src = img['src']
        if not src.startswith('data:'):
            continue

        # Parse data URI: data:<mime>;base64,<data>
        m = re.match(r'data:image/([^;]+);base64,(.*)', src, re.DOTALL)
        if not m:
            continue

        ext = m.group(1).lower()
        if ext == 'svg+xml':
            ext = 'svg'
        data = m.group(2)

        os.makedirs(img_dir, exist_ok=True)
        count += 1
        filename = f'img_{count:03d}.{ext}'
        filepath = os.path.join(img_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(data))

        img['src'] = f'images/{filename}'

    return count


def generate_toc(md):
    """Generate a table of contents from markdown headings and prepend it.

    Scans for ATX headings (## ... ######), uses existing <a id="..."> or
    <span id="..."> anchors when available, falls back to GitHub-style anchors.
    Inserts TOC after the first H1 (or at the top if no H1).
    """
    # Match headings, optionally preceded by <a id="..."></a> on previous line
    anchor_heading_re = re.compile(
        r'^(?:<a id="([^"]*)"></a>\n\n)?'  # optional anchor before heading
        r'(#{1,6}) (.+)$',
        re.MULTILINE
    )
    headings = []
    for m in anchor_heading_re.finditer(md):
        anchor_id = m.group(1)  # from <a id="...">
        level = len(m.group(2))
        raw_text = m.group(3).strip()
        if level == 1:
            continue
        # Clean display text: strip any inline <span id="..."></span> or <a id="..."></a>
        display = re.sub(r'<(?:a|span) id="[^"]*"></(?:a|span)>', '', raw_text).strip()
        # Extract inline <span id="..."> if present (Pandoc puts it inside heading)
        inline_id = re.search(r'<span id="([^"]*)"></span>', raw_text)
        # Use anchor: explicit <a id> > inline <span id> > GitHub-generated
        if anchor_id:
            anchor = urllib.parse.quote(anchor_id, safe='-_')
        elif inline_id:
            anchor = urllib.parse.quote(inline_id.group(1), safe='-_')
        else:
            anchor = _github_anchor(display)
        headings.append((level, display, anchor))

    if not headings:
        return md

    min_level = min(h[0] for h in headings)
    toc_lines = ['## Оглавление\n']
    for level, display, anchor in headings:
        indent = '  ' * (level - min_level)
        toc_lines.append(f'{indent}- [{display}](#{anchor})')
    toc_lines.append('')
    toc_block = '\n'.join(toc_lines)

    # Insert after first H1 heading, or at the top
    h1_match = re.search(r'^# .+$', md, re.MULTILINE)
    if h1_match:
        pos = h1_match.end()
        return md[:pos] + '\n\n' + toc_block + '\n' + md[pos:]
    else:
        return toc_block + '\n' + md


def _github_anchor(text):
    """Generate GitHub-compatible anchor from heading text."""
    anchor = re.sub(r'[*_`\[\]()]', '', text)
    anchor = anchor.lower()
    anchor = re.sub(r'[^\w\s-]', '', anchor)
    anchor = re.sub(r'[\s]+', '-', anchor.strip())
    return urllib.parse.quote(anchor, safe='-_')
