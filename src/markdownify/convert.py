"""markdownify converter with pre/post-processing.

Pre-processes HTML:
- Strips <style>/<script> tags
- Converts internal docs.crpt.ru links to #anchor links
- Protects complex tables (cells with multiple block elements) from conversion
- Extracts code language from <code data-lang>

Post-processes markdown:
- Restores complex tables as raw HTML
- Inserts <a id="..."> anchors before headings

Usage: python convert.py <input.htm> <output_dir> [internal_link_base]
"""
import sys
import os
import re
from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common import extract_images, generate_toc

input_file = sys.argv[1]
output_dir = sys.argv[2]
link_base = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else ''
os.makedirs(output_dir, exist_ok=True)


def get_lang(el):
    code = el.find('code', attrs={'data-lang': True})
    return code['data-lang'] if code else ''


with open(input_file, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Strip style/script
for tag in soup.find_all(['script', 'style']):
    tag.decompose()

# Internal links
if link_base:
    for a in soup.find_all('a', href=True):
        if a['href'].startswith(link_base + '#'):
            a['href'] = a['href'].replace(link_base, '')

# Extract base64 images to files
n_imgs = extract_images(soup, output_dir)

# Protect complex tables
complex_tables = {}
for idx, table in enumerate(soup.find_all('table')):
    is_complex = False
    for cell in table.find_all(['td', 'th']):
        if len(cell.find_all(['p', 'ul', 'ol', 'pre'])) > 1:
            is_complex = True
            break
    if is_complex:
        placeholder = 'COMPLEXTABLE%d' % idx
        complex_tables[placeholder] = str(table)
        table.replace_with(placeholder)

# Heading IDs
heading_ids = {}
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    if h.get('id'):
        heading_ids[h.get_text().strip()] = h['id']

# Convert
md = md_convert(str(soup), heading_style='ATX', code_language_callback=get_lang)

# Restore complex tables
for placeholder, html_table in complex_tables.items():
    md = md.replace(placeholder, '\n\n' + html_table + '\n\n')


# Insert anchor IDs before headings
def insert_anchor(m):
    hashes, text = m.group(1), m.group(2).strip()
    hid = heading_ids.get(text, '')
    if hid:
        return '<a id="' + hid + '"></a>\n\n' + hashes + ' ' + text
    return m.group(0)


md = re.sub(r'^(#{1,6}) (.+)$', insert_anchor, md, flags=re.MULTILINE)

# Generate TOC
md = generate_toc(md)

output_file = os.path.join(output_dir, 'README.md')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f'markdownify: {input_file} -> {output_file}')
