import sys
from PIL import Image
ref = Image.open('blender/reference/starlight_kitsune_ref.png').convert('RGB'); W, H = ref.size
rf = ref.crop((0, int(H * 0.17), int(W * 0.47), int(H * 0.86))); rs = ref.crop((int(W * 0.47), int(H * 0.17), W, int(H * 0.86)))
f = Image.open('renders/kitsune/front.png').convert('RGB'); s = Image.open('renders/kitsune/side.png').convert('RGB')
h = 420; row = lambda ims: [im.resize((int(im.width * h / im.height), h)) for im in ims]
ims = row([rf, f, rs, s]); out = Image.new('RGB', (sum(i.width for i in ims), h)); x = 0
for i in ims: out.paste(i, (x, 0)); x += i.width
out.save(sys.argv[1])
