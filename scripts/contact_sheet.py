import sys, glob, os
from PIL import Image, ImageDraw
ids = open(sys.argv[1]).read().split(); out = sys.argv[2]; view = sys.argv[3] if len(sys.argv) > 3 else '34'; cols = int(sys.argv[4]) if len(sys.argv) > 4 else 6; S = 200
rows = (len(ids) + cols - 1) // cols; im = Image.new('RGB', (cols * S, rows * (S + 16)), (52, 58, 72)); d = ImageDraw.Draw(im)
for i, n in enumerate(ids):
    f = f'renders/thumbs/{n}_{view}.png'
    if not os.path.exists(f): continue
    t = Image.open(f).convert('RGBA').resize((S, S)); x, y = (i % cols) * S, (i // cols) * (S + 16); im.paste(t, (x, y), t); d.text((x + 3, y + S + 2), n[:32], fill=(230, 230, 230))
im.save(out)
