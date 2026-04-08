"""Shared pre-processing utilities for all converters."""
import os
import base64
import re


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
