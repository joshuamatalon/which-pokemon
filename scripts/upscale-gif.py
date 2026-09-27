# REJECTED 2026-09-27: on these sprites RealESRGAN (photo and anime models alike) erased one-pixel fur marks and
# redrew the tail star and mouth, so the result read as a different drawing. scripts/hqx-gif.py is the one in use.
# Kept for the record.
# Upscale a Showdown animated sprite with RealESRGAN on the GPU, frame by frame, and write a clean GIF on
# the quiz's paper background. Colour and alpha are upscaled as two separate passes, then composited
# onto a flat background, so the background stays clean and the edges come from the upscaled mask.
# Run with ComfyUI's embedded Python (torch + spandrel), user site disabled:
#   PYTHONNOUSERSITE=1 D:/ComfyUI_windows_portable/python_embeded/python.exe -s scripts/upscale-gif.py
#       <in.gif> <out.gif> [--model anime|photo] [--height N] [--colors N]
# --height caps the output (Lanczos from the 4x result); --colors sets the GIF palette size.
import sys, os, argparse
import numpy as np
import torch
from PIL import Image, ImageSequence
from spandrel import ModelLoader

MODELS = {
    "photo": r"D:\ComfyUI_windows_portable\ComfyUI\models\upscale_models\RealESRGAN_x4plus.pth",
    "anime": r"D:\ComfyUI_windows_portable\ComfyUI\models\upscale_models\RealESRGAN_x4plus_anime_6B.pth",
}
BG = (247, 245, 240)  # --paper
PAD = 8               # padding at source scale

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--model", default="anime", choices=MODELS)
ap.add_argument("--height", type=int, default=None)
ap.add_argument("--colors", type=int, default=255)
a = ap.parse_args()

model = ModelLoader().load_from_file(MODELS[a.model]).eval().cuda()

def up(img_rgb):
    arr = np.asarray(img_rgb).astype(np.float32) / 255.0
    t = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).cuda()
    out = model(t).clamp(0, 1)[0].permute(1, 2, 0).cpu().numpy()
    return Image.fromarray((out * 255.0 + 0.5).astype(np.uint8))

src = Image.open(a.src)
W, H = src.size
frames, durs = [], []
with torch.no_grad():
    for f in ImageSequence.Iterator(src):
        rgba = f.convert("RGBA")
        pad = Image.new("RGBA", (W + 2 * PAD, H + 2 * PAD), (0, 0, 0, 0))
        pad.alpha_composite(rgba, (PAD, PAD))
        # colour pass: sprite over the paper colour, so edge pixels blend toward the final background
        colour = Image.new("RGBA", pad.size, BG + (255,)); colour.alpha_composite(pad)
        colour_up = up(colour.convert("RGB"))
        # alpha pass: the mask as a grey image
        alpha = pad.getchannel("A")
        alpha_up = up(Image.merge("RGB", (alpha, alpha, alpha))).convert("L")
        canvas = Image.new("RGB", colour_up.size, BG)
        canvas.paste(colour_up, (0, 0), alpha_up)
        if a.height and canvas.height > a.height:
            w = round(canvas.width * a.height / canvas.height)
            canvas = canvas.resize((w, a.height), Image.LANCZOS)
        frames.append(canvas.quantize(colors=a.colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
        durs.append(f.info.get("duration", 40))
frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=1)
chk = Image.open(a.out)
print(os.path.basename(a.out), chk.size, chk.n_frames, "frames", os.path.getsize(a.out) // 1024, "KB", "model", a.model)
