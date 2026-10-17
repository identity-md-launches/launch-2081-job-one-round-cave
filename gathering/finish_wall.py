#!/usr/bin/env python3
"""Apply only a small generated mark; encode PNG with the standard library.

Build helper, not a generator. Reads the inherited wall and the image tool's
returned draft, then replaces the draft with the finished wall. No extra images.
"""
import hashlib
import json
from pathlib import Path
import struct
import zlib


def read_png(path):
    raw = path if isinstance(path, bytes) else Path(path).read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a PNG')
    at, packed = 8, bytearray()
    while at < len(raw):
        size = int.from_bytes(raw[at:at + 4], 'big')
        kind, body = raw[at + 4:at + 8], raw[at + 8:at + 8 + size]
        checksum = int.from_bytes(raw[at + 8 + size:at + 12 + size], 'big')
        if zlib.crc32(kind + body) != checksum:
            raise ValueError('PNG checksum mismatch')
        if kind == b'IHDR':
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', body)
            if (depth, color, compression, filtering, interlace) != (8, 2, 0, 0, 0):
                raise ValueError('expected noninterlaced 8-bit RGB PNG')
        elif kind == b'IDAT':
            packed.extend(body)
        elif kind == b'IEND':
            break
        at += size + 12
    data = zlib.decompress(packed)
    stride = width * 3
    if len(data) != height * (stride + 1):
        raise ValueError('PNG data length mismatch')
    result, previous = bytearray(), bytearray(stride)
    for y in range(height):
        at = y * (stride + 1)
        mode, row = data[at], bytearray(data[at + 1:at + stride + 1])
        for x in range(stride):
            left = row[x - 3] if x >= 3 else 0
            above = previous[x]
            upper_left = previous[x - 3] if x >= 3 else 0
            if mode == 0:
                predictor = 0
            elif mode == 1:
                predictor = left
            elif mode == 2:
                predictor = above
            elif mode == 3:
                predictor = (left + above) // 2
            elif mode == 4:
                p = left + above - upper_left
                distances = (abs(p - left), abs(p - above), abs(p - upper_left))
                predictor = (left, above, upper_left)[distances.index(min(distances))]
            else:
                raise ValueError('unsupported PNG filter')
            row[x] = (row[x] + predictor) & 255
        result.extend(row)
        previous = row
    return width, height, result


def write_png(path, width, height, pixels):
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    rows = b''.join(b'\0' + pixels[y * width * 3:(y + 1) * width * 3] for y in range(height))
    raw = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))
    Path(path).write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def main():
    ancestor = Path('artifacts/gathering/wall.png')
    output = Path('artifacts/gathering/wall-v2.png')
    ancestor_sha = hashlib.sha256(ancestor.read_bytes()).hexdigest()
    if ancestor_sha != '0f6a1d04cc77f550fe19e9f743b009aa7b338700d7ffc41921b10e284d4c158c':
        raise ValueError('expected inherited gathering 01 wall; do not apply twice')
    width, height, original = read_png(ancestor)
    dw, dh, draft = read_png(output)
    if (width, height) != (dw, dh):
        raise ValueError('draft dimensions differ')
    final = original[:]
    # Isolate the generated ochre rings and charcoal sprout. Composite pigment
    # only, retaining the ancestor's stone beneath and between the new strokes.
    sx, sy, dx, dy, pw, ph = 740, 840, 780, 915, 210, 165
    for y in range(ph):
        for x in range(pw):
            source = ((sy + y) * width + sx + x) * 3
            target = ((dy + y) * width + dx + x) * 3
            r, g, b = draft[source:source + 3]
            ellipses = [((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                        for cx, cy, rx, ry in [(78, 83, 59, 57), (137, 86, 58, 57)]]
            ring = any(0.53 < distance < 1.48 for distance in ellipses)
            alpha = 0.0
            if ring and r > 50 and g < 125 and r > 1.7 * g and r > 2.2 * b:
                alpha = min(0.88, (r / max(g, 1) - 1.7) * 2)
            if 82 < x < 132 and 68 < y < 119 and r < 125 and g < 100:
                alpha = max(alpha, min(0.92, (125 - r) / 50))
            alpha *= min(1.0, x / 18, y / 18, (pw - 1 - x) / 18, (ph - 1 - y) / 18)
            for c in range(3):
                final[target + c] = round(original[target + c] * (1 - alpha) + draft[source + c] * alpha)
    changed = outside = 0
    for i in range(width * height):
        if final[3 * i:3 * i + 3] != original[3 * i:3 * i + 3]:
            changed += 1
            x, y = i % width, i // width
            outside += not (dx <= x < dx + pw and dy <= y < dy + ph)
    assert outside == 0
    sha = write_png(output, width, height, final)
    ancestor.write_bytes(output.read_bytes())
    evidence = {'ancestor_sha256': ancestor_sha, 'wall_sha256': sha,
                'dimensions': [width, height], 'format': 'PNG',
                'new_mark_rectangle': [dx, dy, pw, ph], 'changed_pixels': changed,
                'changed_pixels_outside_rectangle': outside}
    Path('gathering/image-preservation.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
