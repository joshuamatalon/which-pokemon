# Scale a Showdown animated sprite 4x with hq4x, an edge-aware pixel scaler that smooths staircase edges
# without adding or removing any detail (the neural upscaler in upscale-gif.py erased one-pixel fur marks).
# Each frame is composited onto the quiz's paper colour first, then scaled, then quantized for GIF.
#   python scripts/hqx-gif.py <in.gif> <out.gif> [--height N] [--colors N]
import sys, os, types, argparse
import PIL
# The hqx package imports PIL.PyAccess for type hints only; Pillow 10 removed that module.
_stub = types.ModuleType("PIL.PyAccess"); _stub.PyAccess = object
sys.modules["PIL.PyAccess"] = _stub; PIL.PyAccess = _stub
import hqx
from PIL import Image, ImageSequence

BG = (247, 245, 240)  # --paper
PAD = 8               # at source scale

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--height", type=int, default=None)
ap.add_argument("--colors", type=int, default=255)
a = ap.parse_args()

src = Image.open(a.src)
W, H = src.size
frames, durs = [], []
for f in ImageSequence.Iterator(src):
    canvas = Image.new("RGBA", (W + 2 * PAD, H + 2 * PAD), BG + (255,))
    canvas.alpha_composite(f.convert("RGBA"), (PAD, PAD))
    big = hqx.hq4x(canvas.convert("RGB"))
    if a.height and big.height > a.height:
        big = big.resize((round(big.width * a.height / big.height), a.height), Image.LANCZOS)
    frames.append(big.quantize(colors=a.colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    durs.append(f.info.get("duration", 40))
frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=1)
chk = Image.open(a.out)
print(os.path.basename(a.out), chk.size, chk.n_frames, "frames", os.path.getsize(a.out) // 1024, "KB")
