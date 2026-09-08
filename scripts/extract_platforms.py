"""Reconstruct the three platform images exactly from their PDF image/mask pairs."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools'))
from PIL import Image

for image_id, mask_id, name in [
    (3, 4, 'uav-platform-01.png'),
    (5, 6, 'uav-platform-02.png'),
    (7, 8, 'uav-platform-03.png'),
]:
    color = Image.open(ROOT / '.preview' / f'cv-extract-{image_id:03d}.jpg').convert('RGB')
    alpha = Image.open(ROOT / '.preview' / f'cv-extract-{mask_id:03d}.ppm').convert('L')
    assert color.size == alpha.size
    color.putalpha(alpha)
    color.save(ROOT / 'assets' / name, optimize=True)
    print(f'Extracted {name}: {color.size}')
