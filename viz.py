# backend/app/viz.py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Dict, Any
from tempfile import NamedTemporaryFile
import subprocess
from sympy import lambdify
from sympy.parsing.sympy_parser import parse_expr
from sympy import symbols

def plot_function(expr_str: str, var='x', outpath: str = None) -> Dict[str, Any]:
    x = symbols(var)
    expr = parse_expr(expr_str)
    f = lambdify(x, expr, "numpy")
    xs = np.linspace(-6, 6, 400)
    ys = f(xs)
    fig, ax = plt.subplots(figsize=(6,4))
    ax.plot(xs, ys)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    ax.set_title(f"y = {expr_str}")
    if outpath is None:
        tmp = NamedTemporaryFile(delete=False, suffix=".png")
        outpath = tmp.name
    fig.savefig(outpath, bbox_inches='tight')
    plt.close(fig)
    return {"path": outpath}

# Simple animation: animate f(x,t) = f(x+shift)
def animate_transform(expr_str: str, var='x', frames=30, out_mp4="/tmp/lamda_anim.mp4"):
    # create frames and call ffmpeg to assemble
    tmpdir = "/tmp/lamda_frames"
    os.makedirs(tmpdir, exist_ok=True)
    x = symbols(var)
    expr = parse_expr(expr_str)
    f = lambdify(x, expr, "numpy")
    xs = np.linspace(-6,6,400)
    for i in range(frames):
        shift = np.sin(2*np.pi*i/frames)
        ys = f(xs + shift)
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(xs, ys)
        ax.set_title(f"frame {i}")
        fname = os.path.join(tmpdir, f"frame_{i:03d}.png")
        fig.savefig(fname, bbox_inches='tight')
        plt.close(fig)
    # assemble using ffmpeg (must be present)
    cmd = [
        "ffmpeg","-y","-framerate","12","-i", f"{tmpdir}/frame_%03d.png",
        "-c:v","libx264","-pix_fmt","yuv420p", out_mp4
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {"path": out_mp4}
    except Exception as e:
        return {"error": str(e)}

