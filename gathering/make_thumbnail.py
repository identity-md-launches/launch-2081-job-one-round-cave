"""Run with blender -b -t 1 -P gathering/make_thumbnail.py; no scene rendering."""
from pathlib import Path
import bpy

image = bpy.data.images.load(str(Path('artifacts/gathering/wall-v2.png').resolve()))
assert tuple(image.size) == (1254, 1254)
image.scale(512, 512)
image.file_format = 'JPEG'
image.filepath_raw = str(Path('dist/gathering/22.jpg').resolve())
image.save()
assert Path('dist/gathering/22.jpg').stat().st_size < 100000
print('Saved dist/gathering/22.jpg (512 x 512 JPEG)')
