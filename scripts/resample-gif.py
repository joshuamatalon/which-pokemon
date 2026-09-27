# Scale a Showdown animated sprite 4x with a plain Lanczos resample onto the quiz's paper colour. This is
# the version Josh chose on 2026-09-27: less pixelated than the source, no edge-aware smoothing and no
# neural upscaling (both read as wrong on these sprites; see hqx-gif.py and upscale-gif.py).
#   python scripts/resample-gif.py <in.gif> <out.gif> [--scale 4] [--colors 255]
import os, argparse
from PIL import Image, ImageSequence

BG = (247, 245, 240)  # --paper
PAD = 24              # at output scale

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--scale", type=int, default=4)
ap.add_argument("--colors", type=int, default=255)
a = ap.parse_args()

src = Image.open(a.src)
W, H = src.size
frames, durs = [], []
for f in ImageSequence.Iterator(src):
    big = f.convert("RGBA").resize((W * a.scale, H * a.scale), Image.LANCZOS)
    canvas = Image.new("RGBA", (big.width + 2 * PAD, big.height + 2 * PAD), BG + (255,))
    canvas.alpha_composite(big, (PAD, PAD))
    frames.append(canvas.convert("RGB").quantize(colors=a.colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    durs.append(f.info.get("duration", 40))
frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=1)
chk = Image.open(a.out)
print(os.path.basename(a.out), chk.size, chk.n_frames, "frames", os.path.getsize(a.out) // 1024, "KB")
