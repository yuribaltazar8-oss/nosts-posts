"""Vídeo curto (Reel) a partir de imagens 9:16 geradas por render.py.

Uso:  python3 engine/video.py video.json
Spec:
{
  "spec": "spec_imagens.json",        # spec do render.py com size "story" (cada página = 1 cena)
  "durations": [2.5, 3.5, 3.5, 3],    # segundos por cena (1ª cena = hook, curta)
  "out": "posts/AAAA-MM-DD/reel.mp4"
}
Cada cena tem zoom lento (1.00 -> 1.05) e transição suave. 1080x1920, 30 fps, H.264 + faixa de áudio silenciosa
(o Instagram não deixa juntar música por API).
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from render import render  # noqa: E402

FPS = 30
FADE = 0.4


def main(path):
    v = json.load(open(path, encoding="utf-8"))
    spec = json.load(open(os.path.join(ROOT, v["spec"]) if not os.path.isabs(v["spec"]) else v["spec"], encoding="utf-8"))
    spec["size"] = "story"
    files = render(spec, ROOT)
    durs = v["durations"]
    assert len(durs) == len(files), "uma duração por cena"
    inputs, filters = [], []
    for i, (f, d) in enumerate(zip(files, durs)):
        frames = int(d * FPS)
        inputs += ["-loop", "1", "-t", str(d), "-i", os.path.join(ROOT, f)]
        filters.append(
            f"[{i}:v]scale=2160:3840,zoompan=z='1+0.05*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={frames}:s=1080x1920:fps={FPS},format=yuv420p,setpts=PTS-STARTPTS[v{i}]")
    # encadear com xfade
    last, t = "v0", durs[0]
    for i in range(1, len(files)):
        off = t - FADE
        filters.append(f"[{last}][v{i}]xfade=transition=fade:duration={FADE}:offset={off:.2f}[x{i}]")
        last, t = f"x{i}", t + durs[i] - FADE
    total = t
    out = os.path.join(ROOT, v["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = (["ffmpeg", "-y", "-loglevel", "error"] + inputs +
           ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-filter_complex", ";".join(filters), "-map", f"[{last}]", "-map", f"{len(files)}:a",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out])
    subprocess.run(cmd, check=True)
    print(json.dumps({"video": os.path.relpath(out, ROOT), "seconds": round(total, 2), "frames": files}))


if __name__ == "__main__":
    main(sys.argv[1])
