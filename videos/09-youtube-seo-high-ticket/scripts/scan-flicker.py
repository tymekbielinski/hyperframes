#!/usr/bin/env python3
"""Detect render flicker: an ISOLATED jump against its local neighbourhood.

Real motion (a camera move, a mark landing) has a smooth envelope: neighbouring
frame-steps are of similar size. Render flicker — parallel workers rendering
blocks of frames from different seek states — shows a single frame-pair whose
step dwarfs its neighbours, repeating every worker-block (~20 frames).
"""
import sys, subprocess, os
import numpy as np

f = sys.argv[1]; W, H = 320, 180
p = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vf", "scale=%d:%d" % (W, H),
                    "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
buf = np.frombuffer(p.stdout, dtype=np.uint8)
n = len(buf) // (W * H * 3)
a = buf[:n * W * H * 3].reshape(n, H, W, 3).astype(np.float32)
d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2, 3))
hits = []
for i in range(len(d)):
    lo, hi = max(0, i - 4), min(len(d), i + 5)
    ctx = np.concatenate([d[lo:i], d[i + 1:hi]])
    if len(ctx) == 0:
        continue
    local = float(np.median(ctx))
    if d[i] > 2.5 and d[i] > max(4.0 * local, local + 2.0):
        hits.append((i + 1, round(float(d[i]), 1), round(local, 2)))
print("%-30s frames=%3d median=%.2f  FLICKER=%d %s" %
      (os.path.basename(f), n, float(np.median(d)), len(hits), hits[:10]))
