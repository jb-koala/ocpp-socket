"""Preview renders of the enclosure (matplotlib, no GPU). Run: python render.py -> renders/*.png"""
from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from build123d import Location  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

import enclosure as E  # noqa: E402
import params as P  # noqa: E402

OUT = pathlib.Path(__file__).parent / "renders"
LIGHT = np.array([-0.4, -0.8, 0.6])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

C = {  # colours (RGB 0-1)
    "base": (0.86, 0.87, 0.88), "cover": (0.93, 0.94, 0.95), "lid": (0.42, 0.36, 0.32),
    "bracket": (0.75, 0.76, 0.78), "housing": (0.80, 0.81, 0.83), "insert": (0.30, 0.31, 0.33),
    "pcb": (0.12, 0.45, 0.25), "tall": (0.20, 0.55, 0.35), "low": (0.30, 0.65, 0.45),
    "socket": (0.20, 0.20, 0.22), "plug": (0.10, 0.10, 0.11), "estop": (0.80, 0.12, 0.10),
    "pb1": (0.25, 0.45, 0.95), "solenoid": (0.70, 0.55, 0.20),
}


def tris(part, tol=0.4):
    verts, faces = part.tessellate(tol, 0.3)
    v = np.array([[p.X, p.Y, p.Z] for p in verts])
    # wall frame -> plot frame: x stays, depth (z) goes to -y (front faces the viewer), height (y) goes up
    v = np.column_stack([v[:, 0], -v[:, 2], v[:, 1]])
    return v[np.array(faces)]


def shaded(part, color, alpha=1.0, tol=0.4):
    t = tris(part, tol)
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    shade = 0.40 + 0.60 * np.abs(n @ LIGHT)
    cols = np.clip(np.array(color)[None, :] * shade[:, None], 0, 1)
    rgba = np.column_stack([cols, np.full(len(cols), alpha)])
    return t, rgba


def render(name, items, title, elev=18, azim=-58, size=(7, 8)):
    """All parts go into ONE collection so matplotlib depth-sorts per triangle, not per part."""
    fig = plt.figure(figsize=size, dpi=150)
    ax = fig.add_subplot(111, projection="3d", proj_type="ortho")
    data = [shaded(part, col, a) for part, col, a in items]
    t = np.concatenate([d[0] for d in data])
    rgba = np.concatenate([d[1] for d in data])
    ax.add_collection3d(Poly3DCollection(t, facecolors=rgba, edgecolors=rgba, linewidths=0.25))
    lo, hi = t.reshape(-1, 3).min(0), t.reshape(-1, 3).max(0)
    ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1]); ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(hi - lo)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title, fontsize=11)
    fig.tight_layout()
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", OUT / f"{name}.png")


def main():
    pp = E.printed_parts()
    br = E.make_hinge_bracket(1) + E.make_hinge_bracket(-1)
    closed = [
        (pp["base"], C["base"], 1), (pp["cover"], C["cover"], 1), (E.lid_at(0), C["lid"], 0.9),
        (br, C["bracket"], 1), (pp["lock_housing"], C["housing"], 1),
        (E.estop_head(), C["estop"], 1), (E.pb1_body(), C["pb1"], 1),
    ]
    render("01_cerrada", closed, "OCPP Socket — caja cerrada (130 × 190 × 70 mm)")

    opened = [
        (pp["base"], C["base"], 1), (pp["cover"], C["cover"], 1), (E.lid_at(95), C["lid"], 0.85),
        (br, C["bracket"], 1), (pp["lock_housing"], C["housing"], 1),
        (E.estop_head(), C["estop"], 1), (pp["socket_insert"], C["insert"], 1),
        (E.plug(), C["plug"], 1),
    ]
    render("02_tapa_abierta_con_ficha", opened, "Tapa abierta 95°, ficha enchufada")

    gap = 70
    exploded = [
        (pp["base"], C["base"], 1),
        (E.pcb_board(), C["pcb"], 1), (E.pcb_tall_zone(), C["tall"], 0.5), (E.pcb_low_zone(), C["low"], 0.5),
        (E.socket_body().moved(Location((0, 0, gap * 0.6))), C["socket"], 1),
        (pp["socket_insert"].moved(Location((0, 0, gap * 0.8))), C["insert"], 1),
        (pp["cover"].moved(Location((0, 0, gap))), C["cover"], 1),
        (pp["lock_housing"].moved(Location((0, 0, gap * 1.6))), C["housing"], 1),
        (E.solenoid().moved(Location((0, 0, gap * 1.35))), C["solenoid"], 1),
        (br.moved(Location((0, 0, gap * 1.6))), C["bracket"], 1),
        (E.lid_at(0).moved(Location((0, 0, gap * 2.1))), C["lid"], 0.9),
    ]
    render("03_explosion", exploded, "Despiece: base, PCB (zonas de altura), toma, frente, traba, tapa",
           elev=22, azim=-50, size=(9, 8))

    # section through the socket centre: everything with x < WELL_CX removed
    from build123d import Align, Box, Pos
    keep = Pos(P.WELL_CX, -100, -100) * Box(200, 400, 400, align=(Align.MIN, Align.MIN, Align.MIN))
    sec = [(pp["base"] & keep, C["base"], 1), (pp["cover"] & keep, C["cover"], 1),
           (E.lid_at(0) & keep, C["lid"], 1), (pp["socket_insert"] & keep, C["insert"], 1),
           (E.socket_body() & keep, C["socket"], 1), (E.plug() & keep, C["plug"], 1),
           (E.pcb_board() & keep, C["pcb"], 1), (E.pcb_tall_zone() & keep, C["tall"], 0.6),
           (E.pcb_low_zone() & keep, C["low"], 0.6)]
    render("04_corte", sec, "Corte por el centro de la toma: PCB abajo, toma arriba, tapa con ficha",
           elev=6, azim=172, size=(8, 8))


if __name__ == "__main__":
    main()
