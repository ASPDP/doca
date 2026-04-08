"""html2text converter with pre/post-processing.

Pre-processes HTML:
- Builds code language map from <code data-lang>
- Builds heading text -> id map
- Protects complex tables from conversion
- Converts internal docs.crpt.ru links to #anchor links

Post-processes markdown:
- Converts indented code blocks to fenced with language
- Inserts <a id="..."> anchors before headings
- Restores complex tables as raw HTML

Usage: python convert.py <input.htm> <output_dir>
"""
import sys
import os
import re
from bs4 import BeautifulSoup
import html2text

input_file = sys.argv[1]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)

with open(input_file, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Code language map
lang_map = {}
for pre in soup.find_all('pre', class_='highlight'):
    code = pre.find('code', attrs={'data-lang': True})
    if code:
        key = code.get_text()[:60].strip()
        lang_map[key] = code['data-lang']

# Heading IDs
heading_ids = {}
for h_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    if h_tag.get('id'):
        heading_ids[h_tag.get_text().strip()] = h_tag['id']

# Protect complex tables
complex_tables = {}
for idx, table in enumerate(soup.find_all('table')):
    is_complex = False
    for cell in table.find_all(['td', 'th']):
        if len(cell.find_all(['p', 'ul', 'ol', 'pre'])) > 1:
            is_complex = True
            break
    if is_complex:
        placeholder = 'COMPLEX_TABLE_%d' % idx
        complex_tables[placeholder] = str(table)
        table.replace_with(placeholder)

# Convert
h = html2text.HTML2Text()
h.body_width = 0
html2 = str(soup).replace('https://docs.crpt.ru/gismt/True_API/#', '#')
md = h.handle(html2)

# Replace indented code blocks with fenced ones
lines = md.split('\n')
result = []
i = 0
while i < len(lines):
    if lines[i].startswith('    ') or lines[i].startswith('\t'):
        block = []
        while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t') or lines[i].strip() == ''):
            if lines[i].strip() == '' and i + 1 < len(lines) and not (lines[i + 1].startswith('    ') or lines[i + 1].startswith('\t')):
                break
            block.append(lines[i])
            i += 1
        code_lines = []
        for l in block:
            if l.startswith('    '):
                code_lines.append(l[4:])
            elif l.startswith('\t'):
                code_lines.append(l[1:])
            else:
                code_lines.append(l)
        code_text = '\n'.join(code_lines).strip()
        key = code_text[:60].strip()
        lang = lang_map.get(key, '')
        result.append('```' + lang)
        result.append(code_text)
        result.append('```')
    else:
        result.append(lines[i])
        i += 1

md = '\n'.join(result)


# Insert anchor IDs before headings
def insert_anchor(m):
    hashes, text = m.group(1), m.group(2).strip()
    hid = heading_ids.get(text, '')
    if hid:
        return '<a id="' + hid + '"></a>\n\n' + hashes + ' ' + text
    return m.group(0)


md = re.sub(r'^(#{1,6}) (.+)$', insert_anchor, md, flags=re.MULTILINE)

# Restore complex tables
for placeholder, html_table in complex_tables.items():
    md = md.replace(placeholder, '\n\n' + html_table + '\n\n')

output_file = os.path.join(output_dir, 'README.md')
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md)

print(f'html2text: {input_file} -> {output_file}')
