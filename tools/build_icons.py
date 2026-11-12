#!/usr/bin/env python3
"""Build 35 Mac app icons in the style of the flat.icns (Tina Latif) set:
flat squircle badge (840px box, ~105 radius, on 1024 canvas) + simple bold glyph."""
import io, math, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

SRC = '/home/hatch/workspace/mac-icons/flat3-src'
os.makedirs(SRC, exist_ok=True)
CACHE = '/tmp/glyphs'
os.makedirs(CACHE, exist_ok=True)

BOX = (92, 92, 932, 932)
RADIUS = 105
CENTER = 512

def fetch_glyph(names, color_hex):
    """Download a mono glyph PNG from Iconify. names: fallback list of 'set:name' or bare mdi names."""
    for name in names:
        prefix, _, iname = name.partition(':')
        if not iname:
            prefix, iname = 'mdi', prefix
        path = os.path.join(CACHE, f'{prefix}_{iname}_{color_hex}.png')
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            return Image.open(path).convert('RGBA')
        url = f'https://api.iconify.design/{prefix}/{iname}.svg?height=1024&color=%23{color_hex}'
        try:
            import cairosvg
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            svg = urllib.request.urlopen(req, timeout=30).read()
            data = cairosvg.svg2png(bytestring=svg, output_width=1024, output_height=1024)
            im = Image.open(io.BytesIO(data)).convert('RGBA')
            if im.getbbox() is None:
                continue
            im.save(path)
            return im
        except Exception as e:
            print('glyph fail', name, e)
    raise RuntimeError(f'no glyph for {names}')

def base(bg):
    canvas = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle(BOX, radius=RADIUS, fill=bg)
    return canvas

def paste_glyph(canvas, glyph, size=500, dx=0, dy=0):
    g = glyph.copy()
    g.thumbnail((size, size), Image.LANCZOS)
    canvas.paste(g, (CENTER - g.width // 2 + dx, CENTER - g.height // 2 + dy), g)
    return canvas

def font(path, size):
    return ImageFont.truetype(path, size)

SANS_BOLD = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
MONO_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'

icons = {}

# ---------- glyph-on-badge icons ----------
# slug: (bg, glyph names, glyph color, glyph size)
simple = {
    'podcasts':           ('#7C3AED', ['podcast'], 'FFFFFF', 520),
    'stocks':             ('#111111', ['chart-line'], 'FFFFFF', 520),
    'news':               ('#EF3E56', ['newspaper'], 'FFFFFF', 500),
    'home':               ('#F5A623', ['home'], 'FFFFFF', 540),
    'find-my':            ('#2FB457', ['radar'], 'FFFFFF', 560),
    'journal':            ('#3B6FD4', ['notebook', 'book-open-page-variant'], 'FFFFFF', 500),
    'passwords':          ('#3A3A3C', ['key'], 'FFC531', 520),
    'image-playground':   ('#FFFFFF', ['magic-staff', 'auto-fix'], 'A259E6', 520),
    'phone':              ('#2FB457', ['phone'], 'FFFFFF', 500),
    'games':              ('#FFFFFF', ['gamepad-variant'], '3A3A3C', 560),
    'magnifier':          ('#FFFFFF', ['magnify'], '2F80ED', 560),
    'iphone-mirroring':   ('#1C1C1E', ['monitor-cellphone', 'cellphone-link'], 'FFFFFF', 500),
    'airport-utility':    ('#607D8B', ['router-wireless'], 'FFFFFF', 540),
    'audio-midi-setup':   ('#37474F', ['piano', 'tune-vertical'], 'FFFFFF', 520),
    'bluetooth-file-exchange': ('#147CE5', ['bluetooth'], 'FFFFFF', 520),
    'digital-color-meter': ('#FFFFFF', ['eyedropper'], '37474F', 520),
    'directory-utility':  ('#546E7A', ['account-group'], 'FFFFFF', 540),
    'image-capture':      ('#78909C', ['camera'], 'FFFFFF', 520),
    'print-center':       ('#7A8699', ['printer'], 'FFFFFF', 520),
    'screen-sharing':     ('#2F80ED', ['monitor-share', 'monitor'], 'FFFFFF', 520),
    'screenshot':         ('#8E8E93', ['crosshairs'], 'FFFFFF', 540),
    'script-editor':      ('#FFFFFF', ['script-text', 'file-document-edit-outline'], '5B7C99', 520),
    'tips':               ('#F5B921', ['lightbulb'], 'FFFFFF', 520),
    'voiceover-utility':  ('#7C4DBE', ['eye'], 'FFFFFF', 560),
    'migration-assistant': ('#5B7C99', ['file-swap', 'swap-horizontal'], 'FFFFFF', 540),
}
for slug, (bg, names, color, size) in simple.items():
    glyph = fetch_glyph(names, color)
    icons[slug] = paste_glyph(base(bg), glyph, size)

# ---------- weather: blue badge, yellow sun + white cloud ----------
c = base('#2F80ED')
d = ImageDraw.Draw(c)
d.ellipse([600, 250, 800, 450], fill='#FFC531')  # sun
glyph = fetch_glyph(['weather-cloudy'], 'FFFFFF')
icons['weather'] = paste_glyph(c, glyph, 560, dx=-40, dy=60)

# ---------- clock: drawn ----------
c = base('#111111')
d = ImageDraw.Draw(c)
d.ellipse([242, 242, 782, 782], fill='white')
def hand(angle_deg, length, width):
    a = math.radians(angle_deg - 90)
    x = CENTER + length * math.cos(a)
    y = CENTER + length * math.sin(a)
    d.line([CENTER, CENTER, x, y], fill='#111111', width=width)
    d.ellipse([x - width/2, y - width/2, x + width/2, y + width/2], fill='#111111')
hand(300, 165, 40)   # hour ~10
hand(54, 225, 34)    # minute ~2 (10:09 style)
d.ellipse([CENTER-26, CENTER-26, CENTER+26, CENTER+26], fill='#111111')
icons['clock'] = c

# ---------- colorsync: drawn color wheel ----------
c = base('#FFFFFF')
d = ImageDraw.Draw(c)
colors = ['#F44336', '#FF9800', '#FFEB3B', '#8BC34A', '#009688', '#2196F3', '#3F51B5', '#9C27B0', '#E91E63']
box = [222, 222, 802, 802]
for i, col in enumerate(colors):
    d.pieslice(box, start=i * 40 - 90, end=(i + 1) * 40 - 90, fill=col)
d.ellipse([402, 402, 622, 622], fill='white')
icons['colorsync-utility'] = c

# ---------- voice memos: drawn red waveform ----------
c = base('#FFFFFF')
d = ImageDraw.Draw(c)
heights = [60, 120, 210, 320, 430, 320, 210, 120, 60]
bw, gap = 40, 28
total = len(heights) * bw + (len(heights) - 1) * gap
x = CENTER - total // 2
for hgt in heights:
    d.rounded_rectangle([x, CENTER - hgt // 2, x + bw, CENTER + hgt // 2], radius=bw // 2, fill='#E8323C')
    x += bw + gap
icons['voice-memos'] = c

# ---------- shortcuts: drawn overlapping diamonds ----------
def diamond(color, cx, cy, s=390):
    layer = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([cx - s//2, cy - s//2, cx + s//2, cy + s//2], radius=80, fill=color)
    return layer.rotate(45, resample=Image.BICUBIC, center=(cx, cy))
c = base('#FFFFFF')
c = Image.alpha_composite(c, diamond('#F93A7C', 405, 405))
c = Image.alpha_composite(c, diamond('#4A6CF7', 619, 619))
icons['shortcuts'] = c

# ---------- boot camp: drawn 4 squares ----------
c = base('#FFFFFF')
d = ImageDraw.Draw(c)
sq, gap = 238, 20
x0 = CENTER - sq - gap // 2
y0 = CENTER - sq - gap // 2
for i, col in enumerate(['#F25022', '#7FBA00', '#00A4EF', '#FFB900']):
    x = x0 + (i % 2) * (sq + gap)
    y = y0 + (i // 2) * (sq + gap)
    d.rectangle([x, y, x + sq, y + sq], fill=col)
icons['boot-camp-assistant'] = c

# ---------- freeform: drawn lemniscate in 3 colors ----------
c = base('#FFFFFF')
d = ImageDraw.Draw(c)
pts = []
N = 400
a = 310
for i in range(N + 1):
    t = 2 * math.pi * i / N
    den = 1 + math.sin(t) ** 2
    x = CENTER + a * math.cos(t) / den
    y = CENTER + a * math.sin(t) * math.cos(t) / den * 1.15
    pts.append((x, y))
seg_colors = ['#FFB800', '#FF6A3D', '#B84BE0']
for i in range(N):
    col = seg_colors[min(2, int(3 * i / N))]
    d.line([pts[i], pts[i + 1]], fill=col, width=52)
    d.ellipse([pts[i][0] - 26, pts[i][1] - 26, pts[i][0] + 26, pts[i][1] + 26], fill=col)
icons['freeform'] = c

# ---------- system information: ring + i ----------
c = base('#6E7B8B')
d = ImageDraw.Draw(c)
d.ellipse([262, 262, 762, 762], outline='white', width=30)
f = font(SANS_BOLD, 330)
d.text((CENTER, CENTER + 8), 'i', font=f, fill='white', anchor='mm')
icons['system-information'] = c

# ---------- console: >_ text ----------
c = base('#202124')
d = ImageDraw.Draw(c)
f = font(MONO_BOLD, 300)
d.text((CENTER, CENTER), '>_', font=f, fill='white', anchor='mm')
icons['console'] = c

# ---------- tv: apple glyph + 'tv' text ----------
c = base('#111111')
glyph = fetch_glyph(['apple'], 'FFFFFF')
g = glyph.copy()
g.thumbnail((300, 300), Image.LANCZOS)
f = font(SANS_BOLD, 285)
d = ImageDraw.Draw(c)
tw = d.textlength('tv', font=f)
total = g.width + 18 + tw
x = CENTER - total / 2
c.paste(g, (int(x), CENTER - g.height // 2), g)
d.text((x + g.width + 18, CENTER + 12), 'tv', font=f, fill='white', anchor='lm')
icons['tv'] = c

# ---------- save ----------
for slug, im in sorted(icons.items()):
    im.save(os.path.join(SRC, slug + '.png'))
print('built', len(icons))
missing = set(simple) | {'weather', 'clock', 'colorsync-utility', 'voice-memos', 'shortcuts',
                         'boot-camp-assistant', 'freeform', 'system-information', 'console', 'tv'}
print('missing:', missing - set(icons))
