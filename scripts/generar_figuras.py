"""Genera las figuras del informe en docs/figuras con los parámetros por defecto del simulador.

Uso:  .venv/bin/python scripts/generar_figuras.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from sensor import numerics as nm  # noqa: E402
from sensor import physics as ph   # noqa: E402

SALIDA = RAIZ / "docs" / "figuras"
SALIDA.mkdir(parents=True, exist_ok=True)

BOB = ph.Bobina(N=150, a=0.015, l=0.020, R0=5.0)
F, V0, D = 1000, 5.0, 0.005
COL = {"Cobre": "#c2410c", "Aluminio": "#0284c7", "Latón": "#a16207",
       "Acero inoxidable 304": "#7c3aed", "Acero al carbono (ferromagnético)": "#15803d"}

plt.rcParams.update({
    "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e4e4e7", "grid.linewidth": 0.6,
    "axes.edgecolor": "#a1a1aa", "axes.titlesize": 11, "axes.titlelocation": "left",
    "legend.frameon": False, "figure.dpi": 150, "savefig.bbox": "tight",
})


def guardar(fig, nombre):
    fig.savefig(SALIDA / nombre)
    plt.close(fig)
    print("  ", nombre)


def fig_distancia():
    dg = np.geomspace(0.5e-3, 50e-3, 200)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for mat, c in COL.items():
        L, R = ph.parametros_efectivos(BOB, dg, F, mat)
        ax[0].semilogx(dg * 1e3, (L / BOB.L0 - 1) * 100, color=c, label=mat)
        ax[1].semilogx(dg * 1e3, R - BOB.R0, color=c)
    ax[0].set(xlabel="d (mm)", ylabel="ΔL / L₀ (%)", title="Inductancia efectiva")
    ax[1].set(xlabel="d (mm)", ylabel="ΔR (Ω)", title="Resistencia efectiva")
    ax[0].legend(fontsize=8)
    guardar(fig, "parametros-vs-distancia.png")


def fig_frecuencia():
    fg = np.geomspace(50, 1e5, 150)
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for mat, c in COL.items():
        dl = [(ph.parametros_efectivos(BOB, D, f, mat)[0] / BOB.L0 - 1) * 100 for f in fg]
        ax.semilogx(fg, dl, color=c, label=mat)
    ax.axhline(0, color="#71717a", lw=0.8)
    ax.set(xlabel="f (Hz)", ylabel="ΔL / L₀ (%)", title=f"Efecto de la frecuencia (d = {D*1e3:.0f} mm)")
    ax.legend(fontsize=8)
    guardar(fig, "inductancia-vs-frecuencia.png")


def fig_respuestas():
    L, R = ph.parametros_efectivos(BOB, D, F, "Cobre")
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    r = nm.resolver_rl(L, R, V0, F, 0.0, 10, 10, fuente="dc")
    t = r["t"] * 1e3
    ax[0].plot(t, r["exacta"], color="#18181b", lw=2, label="Exacta")
    ax[0].plot(t, r["rk4"], "--o", color="#2563eb", ms=3, lw=1, label="RK4")
    ax[0].plot(t, r["euler"], ":s", color="#dc2626", ms=3, lw=1, label="Euler")
    ax[0].axhline(0.632 * r["i_max"], color="#a1a1aa", ls=":", lw=0.8)
    ax[0].axvline(r["tau"] * 1e3, color="#a1a1aa", ls=":", lw=0.8)
    ax[0].annotate("0.63 i_max en t = τ", (r["tau"] * 1e3, 0.632 * r["i_max"]), xytext=(8, -14),
                   textcoords="offset points", fontsize=8, color="#71717a")
    ax[0].set(xlabel="t (ms)", ylabel="i (A)", title="Escalón DC: energizar y desenergizar (Δt = τ/10)")
    ax[0].legend(fontsize=8)
    r = nm.resolver_rl(L, R, V0, F, 0.0, 40, 4)
    t = r["t"] * 1e3
    ax[1].plot(t, r["exacta"], color="#18181b", lw=2, label="Exacta")
    ax[1].plot(t, r["rk4"], "--", color="#2563eb", lw=1, label="RK4")
    ax[1].plot(t, r["euler"], ":", color="#dc2626", lw=1.2, label="Euler")
    ax[1].set(xlabel="t (ms)", ylabel="i (A)", title="Alterna 1 kHz con cobre a 5 mm (Δt = T/40)")
    ax[1].legend(fontsize=8)
    guardar(fig, "respuesta-temporal.png")


def fig_convergencia():
    L, R = ph.parametros_efectivos(BOB, D, F, "Cobre")
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    for k, (fuente, pasos, ciclos, titulo) in enumerate([
            ("ac", (10, 20, 40, 80, 160, 320, 640), 3, "Alterna"),
            ("dc", (2, 4, 8, 16, 32, 64, 128), 6, "Escalón DC")]):
        filas = nm.estudio_convergencia(L, R, V0, F, 0.0, ciclos=ciclos, pasos=pasos, fuente=fuente)
        h = np.array([f["h (µs)"] for f in filas])
        ee = np.array([f["Euler e_abs (A)"] for f in filas])
        er = np.array([f["RK4 e_abs (A)"] for f in filas])
        ax[k].loglog(h, ee, "o-", color="#dc2626", label="Euler")
        ax[k].loglog(h, er, "o-", color="#2563eb", label="RK4")
        ax[k].loglog(h, ee[-1] * h / h[-1], ":", color="#a1a1aa", label="pendiente 1")
        ax[k].loglog(h, er[2] * (h / h[2]) ** 4, "--", color="#a1a1aa", label="pendiente 4")
        ax[k].set(xlabel="Δt (µs)", ylabel="error global máx. (A)", title=titulo)
        ax[k].legend(fontsize=8)
    guardar(fig, "convergencia.png")


def fig_campo():
    gamma = ph.coef_imagen(BOB, D, F, "Cobre")
    a = BOB.a
    A_pk = ph.amplitud_regimen(V0, *ph.parametros_efectivos(BOB, D, F, "Cobre"), F)
    rr = np.linspace(-3 * a, 3 * a, 161)
    zz = np.linspace(0, D + BOB.l + 1.5 * a, 161)
    RR, ZZ = np.meshgrid(rr, zz)
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.4), sharey=True)
    for ax, g, tit in ((axs[0], 0.0, "Sin objeto"), (axs[1], gamma, f"Cobre a 5 mm (Γ = {gamma:+.2f})")):
        Br, Bz = ph.campo_bobina(BOB, D, A_pk, np.abs(RR), ZZ, g)
        Br = Br * np.sign(RR)
        logB = np.log10(np.hypot(Br, Bz) * 1e3 + 1e-6)
        ax.pcolormesh(RR * 1e3, ZZ * 1e3, logB, cmap="Blues", shading="auto",
                      vmin=np.percentile(logB, 2), vmax=np.percentile(logB, 97))
        ax.streamplot(rr * 1e3, zz * 1e3, Br, Bz, color="#3f3f46", density=1.3, linewidth=0.5, arrowsize=0.6)
        for s in (1, -1):
            ax.add_patch(plt.Rectangle((s * a * 1e3 - 0.6, D * 1e3), 1.2, BOB.l * 1e3, color="#18181b"))
        if g:
            ax.add_patch(plt.Rectangle((rr[0] * 1e3, -6), (rr[-1] - rr[0]) * 1e3, 6, color=COL["Cobre"], alpha=0.4))
        ax.set_ylim(-6, zz[-1] * 1e3)
        ax.set(xlabel="ρ (mm)", title=tit)
        ax.grid(False)
    axs[0].set_ylabel("z (mm)")
    guardar(fig, "campo-magnetico.png")


if __name__ == "__main__":
    print("Generando figuras en", SALIDA)
    fig_distancia()
    fig_frecuencia()
    fig_respuestas()
    fig_convergencia()
    fig_campo()
