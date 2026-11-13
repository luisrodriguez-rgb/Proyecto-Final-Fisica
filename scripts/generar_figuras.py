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


def fig_rc_clase():
    """Ejercicio del apunte de clase: carga y descarga de un RC, R = 60 kΩ, C = 200 µF, ε = 9 V, dos ciclos,
    resuelto con los mismos euler y rk4 del simulador."""
    Rc, C, eps = 60e3, 200e-6, 9.0
    tau = Rc * C
    h = tau / 10
    n = 50
    tt, qq_e, qq_r, qq_x, ii = [], [], [], [], []
    q0, t0 = 0.0, 0.0
    for ciclo in range(2):
        for fem in (eps, 0.0):
            g = lambda t, q, fem=fem: (fem - q / C) / Rc
            t, qe = nm.euler(g, q0, h, n, t0=t0)
            _, qr = nm.rk4(g, q0, h, n, t0=t0)
            qinf = fem * C
            qx = qinf + (q0 - qinf) * np.exp(-(t - t0) / tau)
            ii.append((qinf - q0) / (Rc * C) * np.exp(-(t - t0) / tau))
            tt.append(t); qq_e.append(qe); qq_r.append(qr); qq_x.append(qx)
            q0, t0 = qx[-1], t[-1]
    t = np.concatenate(tt); qx = np.concatenate(qq_x)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    ax[0].plot(t, qx * 1e3, color="#18181b", lw=2, label="Exacta")
    ax[0].plot(t, np.concatenate(qq_r) * 1e3, "--", color="#2563eb", lw=1.2, label="RK4")
    ax[0].plot(t, np.concatenate(qq_e) * 1e3, ":", color="#dc2626", lw=1.4, label="Euler")
    ax[0].set(xlabel="t (s)", ylabel="q (mC)", title="Ejercicio de clase: RC, dos ciclos (Δt = τ/10)")
    ax[0].legend(fontsize=8)
    ax[1].plot(t, np.concatenate(ii) * 1e6, color="#18181b", lw=1.6)
    ax[1].set(xlabel="t (s)", ylabel="i (µA)", title="Corriente i = dq/dt (exacta)")
    guardar(fig, "rc-clase-dos-ciclos.png")


def fig_dipolo():
    """Campo sobre el eje frente al campo de un dipolo magnético m = N I π a²."""
    I = ph.amplitud_regimen(V0, BOB.L0, BOB.R0, F)
    m = BOB.N * I * np.pi * BOB.a**2
    z = np.geomspace(2e-3, 0.3, 120)
    _, Bz = ph.campo_bobina(BOB, 0.0, I, np.zeros_like(z), BOB.l / 2 + z, 0.0, n_esp=150)
    Bd = ph.MU0 * 2 * m / (4 * np.pi * z**3)
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.loglog(z * 1e3, Bz * 1e3, color="#18181b", lw=2, label="Bobina (Biot–Savart)")
    ax.loglog(z * 1e3, Bd * 1e3, "--", color="#2563eb", lw=1.4, label="Dipolo  μ₀·2m / 4πz³")
    ax.axvline(BOB.a * 1e3, color="#a1a1aa", ls=":", lw=0.8)
    ax.annotate("z = a", (BOB.a * 1e3, Bz.min() * 1e3 * 3), fontsize=8, color="#71717a")
    ax.set(xlabel="distancia desde el borde de la bobina z (mm)", ylabel="B_z (mT)",
           title="Lejos de la bobina el campo cae como 1/z³")
    ax.legend(fontsize=8)
    guardar(fig, "campo-dipolo.png")


def fig_energia():
    """Balance de energía al energizar: energía entregada = calor en R + energía magnética."""
    from scipy.integrate import cumulative_trapezoid
    L, R = ph.parametros_efectivos(BOB, D, F, "Cobre")
    r = nm.resolver_rl(L, R, V0, F, 0.0, 200, 10, fuente="dc")
    m = r["t"] <= r["t_s"]
    t, i = r["t"][m], r["rk4"][m]
    Ein = cumulative_trapezoid(V0 * i, t, initial=0)
    Ej = cumulative_trapezoid(R * i**2, t, initial=0)
    Em = 0.5 * L * i**2
    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.plot(t * 1e3, Ein * 1e3, color="#18181b", lw=2, label="Entregada por la fuente ∫ε i dt")
    ax.plot(t * 1e3, Ej * 1e3, color="#dc2626", lw=1.4, label="Calor en la resistencia ∫i²R dt")
    ax.plot(t * 1e3, Em * 1e3, color="#2563eb", lw=1.4, label="Magnética ½Li²")
    ax.plot(t * 1e3, (Ej + Em) * 1e3, ":", color="#a1a1aa", lw=1.4, label="Calor + magnética")
    ax.set(xlabel="t (ms)", ylabel="energía (mJ)", title="Balance de energía al energizar la bobina")
    ax.legend(fontsize=8)
    guardar(fig, "balance-energia.png")


def _alcance(bob, f, mat, umbral=0.02):
    dg = np.geomspace(0.2e-3, 80e-3, 260)
    A0 = ph.amplitud_regimen(V0, bob.L0, bob.R0, f)
    L, R = ph.parametros_efectivos(bob, dg, f, mat)
    s = np.abs(ph.amplitud_regimen(V0, L, R, f) - A0) / A0
    idx = np.where(s >= umbral)[0]
    return dg[idx.max()] * 1e3 if idx.size else 0.0


def fig_escenarios():
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.6))
    Ns = np.arange(50, 501, 25)
    ax[0].plot(Ns, [_alcance(ph.Bobina(int(n), BOB.a, BOB.l, BOB.R0), F, "Cobre") for n in Ns], "o-",
               color=COL["Cobre"], ms=3)
    ax[0].set(xlabel="N (espiras)", ylabel="alcance Sₙ (mm)", title="Número de espiras")
    radios = np.linspace(0.005, 0.04, 15)
    ax[1].plot(radios * 1e3, [_alcance(ph.Bobina(BOB.N, a, BOB.l, BOB.R0), F, "Cobre") for a in radios], "o-",
               color=COL["Cobre"], ms=3)
    ax[1].set(xlabel="radio a (mm)", title="Radio de la bobina")
    fs = np.geomspace(200, 1e5, 30)
    for mat in ("Cobre", "Acero al carbono (ferromagnético)"):
        ax[2].semilogx(fs, [_alcance(BOB, f, mat) for f in fs], "o-", color=COL[mat], ms=3,
                       label=mat.split(" (")[0])
    ax[2].set(xlabel="f (Hz)", title="Frecuencia")
    ax[2].legend(fontsize=8, loc="center right")
    guardar(fig, "escenarios-alcance.png")



def fig_oscilador():
    """Oscilador LC del detector: Euler frente a RK4 y el cambio de frecuencia con el Spark."""
    from sensor import vehiculo as vh
    e = vh.Espira()
    r = vh.respuesta(e, vh.VEHICULOS["Chevrolet Spark GT"])
    libre = vh.oscilador(e, pasos_por_periodo=40, periodos=30)
    spark = vh.oscilador(e, r["dL_rel"], r["dR"], 40, 30)
    euler = vh.oscilador(e, pasos_por_periodo=40, periodos=30, metodo="euler")
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    k = 4 * 40 + 1
    ax[0].plot(libre["t"][:k] * 1e6, libre["q"][:k] / libre["q"][0], color="#18181b", lw=1.8, label="RK4, sin carro (55.24 kHz)")
    ax[0].plot(spark["t"][:k] * 1e6, spark["q"][:k] / spark["q"][0], color="#c62a2a", lw=1.8, label="RK4, con el Spark (59.18 kHz)")
    ax[0].plot(euler["t"][:k] * 1e6, euler["q"][:k] / euler["q"][0], ":", color="#dc2626", lw=1.2, label="Euler, sin carro")
    ax[0].set(xlabel="t (µs)", ylabel="q / q₀", title="Carga del capacitor del oscilador (Δt = T/40)")
    ax[0].legend(fontsize=8, loc="lower left")
    per = libre["t"] * libre["f_teorica"]
    ax[1].semilogy(per, libre["energia"] / libre["energia"][0], color="#2563eb", lw=2, label="RK4")
    ax[1].semilogy(per, euler["energia"] / euler["energia"][0], color="#dc2626", lw=2, label="Euler")
    ax[1].semilogy(per, np.exp(-e.R0 / e.L0 * libre["t"]), "--", color="#a1a1aa", lw=1, label="exacta e^(−Rt/L)")
    ax[1].set(xlabel="períodos", ylabel="energía / energía inicial", title="Energía del oscilador")
    ax[1].legend(fontsize=8)
    guardar(fig, "oscilador-lc.png")


if __name__ == "__main__":
    print("Generando figuras en", SALIDA)
    fig_distancia()
    fig_frecuencia()
    fig_respuestas()
    fig_convergencia()
    fig_campo()
    fig_rc_clase()
    fig_dipolo()
    fig_energia()
    fig_escenarios()
    fig_oscilador()
