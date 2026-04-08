"""Pandoc converter with pre-processing.

Pre-processes HTML:
- Converts internal docs.crpt.ru links to #anchor links
- Copies data-lang from <code> to <pre> class for language detection
- Inserts <a id="..."> anchors inside headings for internal link targets

Usage: python convert.py <input.htm> <output_dir> [internal_link_base]
"""
import sys
import os
import subprocess
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from common import extract_images

input_file = sys.argv[1]
output_dir = sys.argv[2]
link_base = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else ''
os.makedirs(output_dir, exist_ok=True)

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

# Anchor IDs inside headings
for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    if h.get('id'):
        anchor = soup.new_tag('a', id=h['id'])
        h.insert(0, anchor)

# Extract base64 images to files
n_imgs = extract_images(soup, output_dir)

# Code language on <pre>
for code in soup.find_all('code', attrs={'data-lang': True}):
    lang = code['data-lang']
    pre = code.find_parent('pre')
    if pre:
        pre['class'] = ['language-' + lang]

preprocessed = os.path.join(output_dir, '_preprocessed.htm')
with open(preprocessed, 'w', encoding='utf-8') as f:
    f.write(str(soup))

output_file = os.path.join(output_dir, 'README.md')
subprocess.run([
    'pandoc', preprocessed,
    '-f', 'html-native_divs-native_spans',
    '-t', 'gfm',
    '--wrap=none',
    '-o', output_file
], check=True)

print(f'Pandoc: {input_file} -> {output_file}')
