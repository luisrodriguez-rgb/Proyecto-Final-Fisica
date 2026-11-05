"""
Simulador de sensor electromagnético (inductivo) de proximidad.
Ejecutar:  streamlit run app.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ui
from sensor import numerics as nm
from sensor import physics as ph
from sensor.symbolic import derivar

st.set_page_config(page_title="Sensor inductivo de proximidad", page_icon=":material/sensors:", layout="wide")

# ============================================================================
# TEMA
# ============================================================================
if "tema" not in st.session_state:
    try:
        st.session_state.tema = "Oscuro" if st.context.theme.type == "dark" else "Claro"
    except Exception:
        st.session_state.tema = "Claro"
tema = st.sidebar.segmented_control("Tema", ["Claro", "Oscuro"], key="tema", label_visibility="collapsed")
P = ui.aplicar_tema(tema or "Claro")       # el control permite deseleccionar: se toma Claro
S = P["series"]
MC = P["materiales"]

# ============================================================================
# PARÁMETROS
# ============================================================================
sb = st.sidebar
ui.grupo("Bobina")
N = sb.slider("Número de espiras N", 10, 500, 150, 10)
radio_mm = sb.slider("Radio a (mm)", 5.0, 50.0, 15.0, 0.5)
long_mm = sb.slider("Longitud l (mm)", 5.0, 100.0, 20.0, 1.0)
R0 = sb.number_input("Resistencia del devanado R₀ (Ω)", 0.5, 100.0, 5.0, 0.5)

ui.grupo("Fuente")
FRECS = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
frec = sb.select_slider("Frecuencia f (Hz)", FRECS, value=1000)
V0 = sb.slider("Amplitud V₀ (V)", 1.0, 24.0, 5.0, 0.5)
I0 = sb.number_input("Corriente inicial I(0) (A)", -2.0, 2.0, 0.0, 0.05)

ui.grupo("Objeto")
material = sb.selectbox("Material", list(ph.MATERIALES), index=1)
d_mm = sb.slider("Distancia d (mm)", 0.5, 40.0, 5.0, 0.5)
umbral_pct = sb.slider("Umbral de activación |ΔI|/I (%)", 0.2, 20.0, 2.0, 0.1)
hist_pct = sb.slider("Histéresis (%)", 0, 30, 10, 1)

ui.grupo("Integración numérica")
ppc = sb.slider("Pasos por ciclo  (Δt = T/n)", 8, 400, 40, 2)
ciclos = sb.slider("Ciclos simulados", 1, 20, 6)

m_sel = ph.MATERIALES[material]
bob = ph.Bobina(N=N, a=radio_mm / 1000, l=long_mm / 1000, R0=R0)
d = d_mm / 1000
w = 2 * np.pi * frec
T = 1 / frec
umbral = umbral_pct / 100
SOLIDOS = [m for m in ph.MATERIALES if not m.startswith("Sin")]


# ============================================================================
# CÁLCULOS
# ============================================================================
@st.cache_data(show_spinner=False)
def curvas_distancia(N, a, l, R0, f):
    b = ph.Bobina(N, a, l, R0)
    dg = np.geomspace(0.2e-3, 80e-3, 260)
    out = {"d": dg}
    for mat in ph.MATERIALES:
        out[mat] = ph.parametros_efectivos(b, dg, f, mat)
    return out


@st.cache_data(show_spinner=False)
def curvas_frecuencia(N, a, l, R0, d, material):
    b = ph.Bobina(N, a, l, R0)
    fg = np.geomspace(50, 1e5, 120)
    L = np.empty_like(fg)
    R = np.empty_like(fg)
    for i, f in enumerate(fg):
        L[i], R[i] = ph.parametros_efectivos(b, d, f, material)
    return fg, L, R


@st.cache_data(show_spinner=False)
def sympy_cache():
    return derivar()


L0 = bob.L0
L_eff, R_eff = ph.parametros_efectivos(bob, d, frec, material)
tau = L_eff / R_eff
Z_eff = ph.impedancia(L_eff, R_eff, frec)
phi = math.atan2(w * L_eff, R_eff)
A_libre = ph.amplitud_regimen(V0, L0, R0, frec)
A_obj = ph.amplitud_regimen(V0, L_eff, R_eff, frec)
senal = abs(A_obj - A_libre) / A_libre
detectado = senal >= umbral
delta = ph.profundidad_penetracion(frec, m_sel["sigma"], m_sel["mu_r"])
I_rms = A_obj / math.sqrt(2)
P_tot = I_rms**2 * R_eff
P_obj = I_rms**2 * (R_eff - R0)
E_max = 0.5 * L_eff * A_obj**2

curv = curvas_distancia(N, bob.a, bob.l, R0, frec)


def senal_vs_d(mat):
    Lm, Rm = curv[mat]
    return np.abs(ph.amplitud_regimen(V0, Lm, Rm, frec) - A_libre) / A_libre


def distancia_conmutacion(mat):
    idx = np.where(senal_vs_d(mat) >= umbral)[0]
    return curv["d"][idx.max()] if idx.size else 0.0


Sn = distancia_conmutacion(material)


def fmt_delta(x: float) -> str:
    return "∞" if np.isinf(x) else f"{x*1e3:.3f} mm"


# ============================================================================
# ENCABEZADO
# ============================================================================
ui.encabezado(
    "Electromagnetismo · Proyecto final",
    "Sensor inductivo de proximidad",
    "Circuito RL equivalente con corrientes de Foucault (modelo de Dodd–Deeds). "
    "Integración por Euler y Runge–Kutta 4 implementados a mano, contrastados con la solución exacta y SciPy.",
)
ui.stats(
    [
        ("L₀ en aire", f"{L0*1e3:.3f} mH", "Wheeler"),
        ("L efectiva", f"{L_eff*1e3:.3f} mH", f"{(L_eff/L0-1)*100:+.2f} %"),
        ("R efectiva", f"{R_eff:.3f} Ω", f"{R_eff-R0:+.3f} Ω"),
        ("|Z|", f"{abs(Z_eff):.2f} Ω", f"φ = {math.degrees(phi):.1f}°"),
        ("Señal |ΔI|/I", f"{senal*100:.2f} %", f"umbral {umbral_pct:.1f} %"),
    ],
    estado=(detectado, "Detectado" if detectado else "Sin detección", f"Sₙ ≈ {Sn*1e3:.1f} mm"),
)

tabs = st.tabs(["Modelo", "Respuesta temporal", "Paso del objeto", "Campo", "Validación", "Derivación", "Análisis"])

# ============================================================================
# 1. MODELO
# ============================================================================
with tabs[0]:
    dg = curv["d"] * 1e3
    col1, col2 = st.columns(2, gap="large")
    with col1:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=("ΔL / L₀ (%)", "ΔR (Ω)"))
        for mat in SOLIDOS:
            Lm, Rm = curv[mat]
            ancho = 2.6 if mat == material else 1.1
            op = 1 if mat == material else 0.55
            fig.add_trace(go.Scatter(x=dg, y=(Lm / L0 - 1) * 100, name=mat, legendgroup=mat, opacity=op,
                                     line=dict(color=MC[mat], width=ancho)), 1, 1)
            fig.add_trace(go.Scatter(x=dg, y=Rm - R0, name=mat, legendgroup=mat, showlegend=False, opacity=op,
                                     line=dict(color=MC[mat], width=ancho)), 2, 1)
        fig.add_vline(x=d_mm, line_dash="dot", line_color=P["faint"], line_width=1)
        fig.update_xaxes(type="log")
        fig.update_xaxes(title_text="distancia d (mm)", row=2, col=1)
        ui.grafica(fig, height=560, title="Parámetros efectivos frente a la distancia",
                   legend=dict(y=-0.16, yanchor="top"), margin=dict(t=60, b=90))
    with col2:
        fig = go.Figure()
        for mat in SOLIDOS:
            fig.add_trace(go.Scatter(x=dg, y=senal_vs_d(mat) * 100,
                                     name=f"{mat}  Sₙ = {distancia_conmutacion(mat)*1e3:.1f} mm",
                                     opacity=1 if mat == material else 0.55,
                                     line=dict(color=MC[mat], width=2.6 if mat == material else 1.1)))
        fig.add_hline(y=umbral_pct, line_dash="dash", line_color=P["text"], line_width=1,
                      annotation_text="umbral", annotation_position="top right")
        fig.add_vline(x=d_mm, line_dash="dot", line_color=P["faint"], line_width=1)
        ui.grafica(fig, height=420, title="Curva de detección",
                   xaxis=dict(type="log", title="distancia d (mm)"),
                   yaxis=dict(type="log", title="|ΔI|/I (%)"),
                   legend=dict(orientation="v", x=0, y=-0.22, yanchor="top", font=dict(size=11)),
                   margin=dict(t=56, b=130))

        fg, Lf, Rf = curvas_frecuencia(N, bob.a, bob.l, R0, d, material)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=fg, y=(Lf / L0 - 1) * 100, name="ΔL / L₀ (%)", line=dict(color=S["rk4"], width=2)))
        fig.add_trace(go.Scatter(x=fg, y=Rf - R0, name="ΔR (Ω)", line=dict(color=S["aux"], width=2)), secondary_y=True)
        fig.add_vline(x=frec, line_dash="dot", line_color=P["faint"], line_width=1)
        fig.update_xaxes(type="log", title_text="frecuencia f (Hz)")
        fig.update_yaxes(title_text="ΔL / L₀ (%)", secondary_y=False)
        fig.update_yaxes(title_text="ΔR (Ω)", secondary_y=True, showgrid=False)
        ui.grafica(fig, height=300, title=f"Dependencia en frecuencia · {material}, d = {d_mm} mm")

    ui.seccion("Ecuaciones del modelo", "Solución cuasi-estática de Maxwell para una bobina sobre un semiespacio conductor")
    e1, e2 = st.columns(2, gap="large")
    with e1:
        st.latex(r"L_0=\frac{\mu_0N^2\pi a^2}{l+0.9a}")
        st.latex(r"\Delta Z = j\omega\pi\mu_0a^2N^2\!\int_0^\infty\! J_1^2(\alpha a)\,\Gamma(\alpha)\,F^2(\alpha)\,d\alpha")
        st.latex(r"F(\alpha)=\frac{e^{-\alpha d}-e^{-\alpha(d+l)}}{\alpha l},\quad "
                 r"\Gamma=\frac{\mu_r\alpha-\alpha_1}{\mu_r\alpha+\alpha_1},\quad \alpha_1=\sqrt{\alpha^2+j\omega\mu_0\mu_r\sigma}")
    with e2:
        st.latex(r"L_{\text{eff}}=L_0+\frac{\operatorname{Im}\Delta Z}{\omega},\qquad R_{\text{eff}}=R_0+\operatorname{Re}\Delta Z")
        st.latex(r"\delta=\sqrt{\frac{2}{\omega\mu_0\mu_r\sigma}},\qquad I_p=\frac{V_0}{\sqrt{R_{\text{eff}}^2+\omega^2L_{\text{eff}}^2}}")
        st.latex(r"\text{detección:}\quad \frac{|I_p-I_{p,0}|}{I_{p,0}}\ \ge\ \text{umbral}")
    ui.kv([
        ("Material", material),
        ("σ", f"{m_sel['sigma']:.3g} S/m"),
        ("μᵣ", f"{m_sel['mu_r']:g}"),
        ("Profundidad de penetración δ", fmt_delta(delta)),
        ("L ideal  μ₀N²A/l", f"{bob.L_ideal*1e3:.3f} mH"),
        ("L Wheeler", f"{L0*1e3:.3f} mH"),
    ])
    ui.nota(f"La fórmula del solenoide ideal sobreestima la inductancia en un "
            f"<b>{100*(bob.L_ideal/L0-1):.0f} %</b> para esta bobina corta (l/a = {bob.l/bob.a:.2f}).")

# ============================================================================
# 2. RESPUESTA TEMPORAL
# ============================================================================
with tabs[1]:
    r = nm.resolver_rl(L_eff, R_eff, V0, frec, I0, ppc, ciclos)
    t_ms = r["t"] * 1e3
    fig = go.Figure()
    for y0, y1 in ((A_libre * (1 - umbral), A_libre * (1 + umbral)), (-A_libre * (1 + umbral), -A_libre * (1 - umbral))):
        fig.add_hrect(y0=y0, y1=y1, fillcolor=P["accent"], opacity=0.08, line_width=0)
    for s_ in (1, -1):
        fig.add_hline(y=s_ * A_libre, line_dash="dot", line_color=P["faint"], line_width=1)
    fig.add_trace(go.Scatter(x=t_ms, y=r["exacta"], name="Exacta", line=dict(color=S["exacta"], width=2.2)))
    fig.add_trace(go.Scatter(x=t_ms, y=r["scipy"], name="SciPy RK45", line=dict(color=S["scipy"], width=1)))
    fig.add_trace(go.Scatter(x=t_ms, y=r["rk4"], name="RK4", mode="lines+markers",
                             marker=dict(size=3.5), line=dict(color=S["rk4"], width=1.2, dash="dash")))
    fig.add_trace(go.Scatter(x=t_ms, y=r["euler"], name="Euler", mode="lines+markers",
                             marker=dict(size=3.5), line=dict(color=S["euler"], width=1.2, dash="dot")))
    ui.grafica(fig, height=460, title=f"Corriente I(t) con el objeto a {d_mm} mm",
               xaxis_title="t (ms)", yaxis_title="I (A)")
    ui.nota(f"La banda sombreada es la zona muerta de ±{umbral_pct:.1f} % alrededor de la amplitud sin objeto "
            f"(línea punteada, {A_libre:.4f} A). El sensor se activa cuando la amplitud sale de ella.")
    ui.kv([
        ("τ = L/R", f"{tau*1e6:.1f} µs"),
        ("Δt", f"{r['h']*1e6:.2f} µs"),
        ("Δt / τ", f"{r['h']/tau:.3f}"),
        ("Error máx. Euler", f"{np.max(np.abs(r['euler']-r['exacta'])):.2e} A"),
        ("Error máx. RK4", f"{np.max(np.abs(r['rk4']-r['exacta'])):.2e} A"),
        ("Energía máx. ½LI²", f"{E_max*1e6:.2f} µJ"),
        ("Potencia media", f"{P_tot*1e3:.2f} mW"),
        ("Disipada en el objeto", f"{P_obj*1e3:.3f} mW ({100*P_obj/P_tot:.2f} %)" if P_tot > 0 else "0"),
    ])
    if r["h"] > 2 * tau:
        ui.nota(f"Δt = {r['h']*1e6:.1f} µs supera 2τ = {2*tau*1e6:.1f} µs: <b>Euler explícito es inestable</b> "
                "(|1 − Δt/τ| &gt; 1). Aumente los pasos por ciclo.", "error")
    elif r["h"] > 2.785 * tau:
        ui.nota("Δt fuera de la región de estabilidad de RK4 (Δt/τ &gt; 2.785).", "aviso")

# ============================================================================
# 3. PASO DEL OBJETO
# ============================================================================
with tabs[2]:
    ui.seccion("Objeto en movimiento sobre una banda transportadora",
               "La pieza se acerca hasta d y se aleja hasta d_max; la inductancia varía en el tiempo.")
    st.latex(r"\frac{dI}{dt}=\frac{V(t)-\left[R(t)+\dot L(t)\right]I}{L(t)}")
    p1, p2, p3 = st.columns(3, gap="large")
    d_max_mm = p1.slider("d_max (mm)", float(d_mm) + 1, 80.0, max(40.0, float(d_mm) + 1), 1.0)
    ciclos_paso = p2.slider("Duración del paso (ciclos)", 20, 400, 80, 10)
    mat_paso = p3.selectbox("Material de la pieza", SOLIDOS,
                            index=SOLIDOS.index(material) if material in SOLIDOS else 0)
    if ppc * ciclos_paso > 300_000:
        ui.nota("Demasiados pasos de integración; reduzca los pasos por ciclo o la duración.", "aviso")
    else:
        Lm, Rm = curv[mat_paso]
        dgr = curv["d"]
        dLdd = np.gradient(Lm, dgr)
        with st.spinner("Integrando"):
            ps = nm.simular_paso(lambda x: np.interp(x, dgr, Lm), lambda x: np.interp(x, dgr, Rm),
                                 lambda x: np.interp(x, dgr, dLdd), V0, frec, I0, ppc, ciclos_paso,
                                 d, d_max_mm / 1000)
        env = nm.envolvente(ps["rk4"], ppc)
        A_qs = ph.amplitud_regimen(V0, ps["L"], ps["R"], frec)
        s_t = np.abs(env - A_libre) / A_libre
        s_t[ps["t"] < 5 * tau + T] = 0          # descarta el transitorio de encendido
        s_qs = np.abs(A_qs - A_libre) / A_libre
        salida = nm.comparador_histeresis(s_t, umbral, hist_pct / 100)
        tm = ps["t"] * 1e3

        fig = make_subplots(rows=5, cols=1, shared_xaxes=True, vertical_spacing=0.045,
                            row_heights=[0.13, 0.13, 0.34, 0.26, 0.14],
                            subplot_titles=("d(t)  mm", "L(t)  mH", "I(t)  A", "Señal demodulada |ΔI|/I  %", "Salida"))
        fig.add_trace(go.Scatter(x=tm, y=ps["d"] * 1e3, name="d", showlegend=False, line=dict(color=P["text"], width=1.5)), 1, 1)
        fig.add_trace(go.Scatter(x=tm, y=ps["L"] * 1e3, name="L", showlegend=False, line=dict(color=MC[mat_paso], width=1.5)), 2, 1)
        fig.add_trace(go.Scatter(x=tm, y=ps["scipy"], name="SciPy", line=dict(color=S["scipy"], width=1)), 3, 1)
        fig.add_trace(go.Scatter(x=tm, y=ps["rk4"], name="RK4", line=dict(color=S["rk4"], width=1)), 3, 1)
        fig.add_trace(go.Scatter(x=tm, y=ps["euler"], name="Euler", line=dict(color=S["euler"], width=1, dash="dot")), 3, 1)
        fig.add_trace(go.Scatter(x=tm, y=env, name="Envolvente", line=dict(color=S["exacta"], width=2)), 3, 1)
        fig.add_trace(go.Scatter(x=tm, y=s_t * 100, name="Señal RK4", showlegend=False, line=dict(color=S["exacta"], width=2)), 4, 1)
        fig.add_trace(go.Scatter(x=tm, y=s_qs * 100, name="Cuasi-estática", line=dict(color=S["aux"], width=1.2, dash="dash")), 4, 1)
        fig.add_hline(y=umbral_pct, line_dash="dash", line_color=P["text"], line_width=1, row=4, col=1,
                      annotation_text="ON", annotation_position="top right")
        fig.add_hline(y=umbral_pct * (1 - hist_pct / 100), line_dash="dot", line_color=P["muted"], line_width=1,
                      row=4, col=1, annotation_text="OFF", annotation_position="bottom right")
        fig.add_trace(go.Scatter(x=tm, y=salida, name="Salida", showlegend=False, fill="tozeroy",
                                 fillcolor=f"rgba({int(P['ok'][1:3],16)},{int(P['ok'][3:5],16)},{int(P['ok'][5:7],16)},0.18)",
                                 line=dict(color=P["ok"], shape="hv", width=2)), 5, 1)
        fig.update_yaxes(range=[-0.1, 1.25], tickvals=[0, 1], ticktext=["OFF", "ON"], row=5, col=1)
        fig.update_xaxes(title_text="t (ms)", row=5, col=1)
        ui.grafica(fig, height=900, margin=dict(t=40, b=44))

        on = np.where(np.diff(salida) == 1)[0]
        off = np.where(np.diff(salida) == -1)[0]
        err_e = np.max(np.abs(ps["euler"] - ps["scipy"]))
        err_r = np.max(np.abs(ps["rk4"] - ps["scipy"]))
        if on.size:
            t_on = (ps["t"][off[0]] if off.size else ps["t"][-1]) - ps["t"][on[0]]
            ui.kv([
                ("Activación en", f"{ps['d'][on[0]]*1e3:.2f} mm"),
                ("Desactivación en", f"{ps['d'][off[0]]*1e3:.2f} mm" if off.size else "—"),
                ("Tiempo en ON", f"{t_on*1e3:.2f} ms"),
                ("Euler − SciPy", f"{err_e:.2e} A"),
                ("RK4 − SciPy", f"{err_r:.2e} A"),
            ])
        else:
            ui.nota("La pieza no supera el umbral en este paso: acérquela, baje el umbral o cambie la frecuencia.", "aviso")
        ui.nota("El término L̇·I es despreciable cuando la pieza se mueve despacio frente al período: "
                "la envolvente coincide con la curva cuasi-estática V₀/|Z(d(t))|.")

# ============================================================================
# 4. CAMPO
# ============================================================================
with tabs[3]:
    gamma = ph.coef_imagen(bob, d, frec, material)
    a_ = bob.a
    z_top = d + bob.l + 1.5 * a_
    col1, col2 = st.columns([1.2, 1], gap="large")
    with col1:
        rr = np.linspace(-3 * a_, 3 * a_, 161)
        zz = np.linspace(0, z_top, 161)
        RR, ZZ = np.meshgrid(rr, zz)
        Br, Bz = ph.campo_bobina(bob, d, A_obj, np.abs(RR), ZZ, gamma)
        Br = Br * np.sign(RR)
        Bm = np.hypot(Br, Bz)
        plt.rcParams.update({
            "figure.facecolor": P["bg"], "axes.facecolor": P["bg"], "savefig.facecolor": P["bg"],
            "text.color": P["text"], "axes.labelcolor": P["muted"], "axes.edgecolor": P["border"],
            "xtick.color": P["muted"], "ytick.color": P["muted"], "font.size": 9,
            "font.family": "sans-serif", "axes.titlesize": 10, "axes.titlelocation": "left",
        })
        figm, ax = plt.subplots(figsize=(7, 6))
        logB = np.log10(Bm * 1e3 + 1e-6)
        pc = ax.pcolormesh(RR * 1e3, ZZ * 1e3, logB, cmap=ui.mapa_color(P), shading="auto",
                           vmin=np.percentile(logB, 2), vmax=np.percentile(logB, 97))
        ax.streamplot(rr * 1e3, zz * 1e3, Br, Bz, color=P["muted"], density=1.5, linewidth=0.6, arrowsize=0.7)
        if not material.startswith("Sin"):
            ax.add_patch(Rectangle((rr[0] * 1e3, -0.6 * a_ * 1e3), (rr[-1] - rr[0]) * 1e3, 0.6 * a_ * 1e3,
                                   color=MC[material], alpha=0.35, lw=0))
            if np.isfinite(delta):
                yd = -min(delta, 0.6 * a_) * 1e3
                ax.axhline(yd, color=P["text"], ls=(0, (3, 3)), lw=0.7)
                ax.text(rr[0] * 1e3 + 1, yd - 0.08 * a_ * 1e3, "δ", color=P["text"])
        for s_ in (1, -1):
            ax.add_patch(Rectangle((s_ * a_ * 1e3 - 0.6, d * 1e3), 1.2, bob.l * 1e3, color=P["text"], lw=0))
        ax.set_xlim(rr[0] * 1e3, rr[-1] * 1e3)
        ax.set_ylim(-0.6 * a_ * 1e3, z_top * 1e3)
        ax.set_xlabel("ρ (mm)")
        ax.set_ylabel("z (mm)")
        for sp_ in ("top", "right"):
            ax.spines[sp_].set_visible(False)
        ax.set_title(f"Líneas de B y log₁₀|B| (mT)   ·   Γ_eff = {gamma:+.2f}")
        cb = figm.colorbar(pc, ax=ax, fraction=0.04, pad=0.02)
        cb.outline.set_visible(False)
        cb.set_label("log₁₀ |B| (mT)", color=P["muted"])
        st.pyplot(figm, clear_figure=True)
    with col2:
        z_ax = np.linspace(0, z_top, 300)
        _, Bz0 = ph.campo_bobina(bob, d, A_obj, np.zeros_like(z_ax), z_ax, 0.0)
        _, Bz1 = ph.campo_bobina(bob, d, A_obj, np.zeros_like(z_ax), z_ax, gamma)
        fig = go.Figure()
        fig.add_vrect(x0=d * 1e3, x1=(d + bob.l) * 1e3, fillcolor=P["text"], opacity=0.05, line_width=0,
                      annotation_text="bobina", annotation_position="top left")
        fig.add_trace(go.Scatter(x=z_ax * 1e3, y=Bz0 * 1e3, name="sin objeto", line=dict(color=S["scipy"], dash="dot", width=1.5)))
        fig.add_trace(go.Scatter(x=z_ax * 1e3, y=Bz1 * 1e3, name="con objeto", line=dict(color=S["rk4"], width=2.4)))
        fig.add_vline(x=0, line_color=MC[material], line_width=3)
        ui.grafica(fig, height=400, title="B_z sobre el eje, en el pico de corriente",
                   xaxis_title="z (mm)", yaxis_title="B_z (mT)")
        ui.lista([
            "El campo se calcula sumando espiras circulares (Biot–Savart con integrales elípticas) "
            "y una <b>bobina imagen</b> reflejada en z = 0 con coeficiente Γ_eff = ΔL / ΔL_ref.",
            "<b>Γ ≈ −1</b>, buen conductor con δ ≪ a: las corrientes de Foucault anulan la componente normal de B "
            "en la superficie (ley de Lenz) y L disminuye.",
            "<b>Γ &gt; 0</b>, ferromagnético a baja frecuencia: el material concentra el flujo y L aumenta.",
            "La imagen es una aproximación visual; L y R se calculan con la integral exacta de Dodd–Deeds.",
        ])

# ============================================================================
# 5. VALIDACIÓN
# ============================================================================
with tabs[4]:
    conv = nm.estudio_convergencia(L_eff, R_eff, V0, frec, I0, ciclos=3)
    df = pd.DataFrame(conv)
    p_e = np.nanmean(df["orden Euler"].values[-4:])
    p_r = np.nanmean(df["orden RK4"].values[1:4])
    col1, col2 = st.columns([1.15, 1], gap="large")
    with col1:
        h = df["h (µs)"].values
        fig = go.Figure()
        e0, r0 = df["Euler e_abs (A)"].iloc[-1], df["RK4 e_abs (A)"].iloc[2]
        fig.add_trace(go.Scatter(x=h, y=e0 * (h / h[-1]), name="pendiente 1", line=dict(color=P["faint"], dash="dot", width=1)))
        fig.add_trace(go.Scatter(x=h, y=r0 * (h / h[2]) ** 4, name="pendiente 4", line=dict(color=P["faint"], dash="dash", width=1)))
        fig.add_trace(go.Scatter(x=h, y=df["Euler e_abs (A)"], name="Euler", mode="lines+markers",
                                 line=dict(color=S["euler"], width=2), marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=h, y=df["RK4 e_abs (A)"].clip(lower=1e-16), name="RK4", mode="lines+markers",
                                 line=dict(color=S["rk4"], width=2), marker=dict(size=6)))
        fig.add_vline(x=T / ppc * 1e6, line_dash="dot", line_color=P["muted"], line_width=1,
                      annotation_text="Δt actual", annotation_position="top left")
        ui.grafica(fig, height=440, title="Error global máximo frente al paso",
                   xaxis=dict(type="log", title="Δt (µs)"), yaxis=dict(type="log", title="max |I_num − I_exacta| (A)"))
    with col2:
        ui.kv([("Orden observado Euler", f"{p_e:.3f}"), ("Teórico", "1"),
               ("Orden observado RK4", f"{p_r:.3f}"), ("Teórico", "4"),
               ("Estabilidad Euler  Δt < 2τ", f"{2*tau*1e6:.1f} µs"),
               ("Estabilidad RK4  Δt < 2.785τ", f"{2.785*tau*1e6:.1f} µs")])
        st.latex(r"p=\frac{\ln(e_k/e_{k+1})}{\ln(h_k/h_{k+1})}")
        ui.nota("Para y′ = −y/τ, Euler amplifica el error por |1 − Δt/τ| en cada paso, por eso exige Δt &lt; 2τ. "
                "Con Δt muy pequeño el error de RK4 llega al redondeo de máquina (~1e-15) y el orden deja de ser medible.")
    st.dataframe(df.style.format({
        "h (µs)": "{:.3f}", "Euler e_abs (A)": "{:.3e}", "Euler e_rel (%)": "{:.3e}",
        "RK4 e_abs (A)": "{:.3e}", "RK4 e_rel (%)": "{:.3e}", "orden Euler": "{:.3f}", "orden RK4": "{:.3f}",
    }, na_rep="—"), width="stretch", hide_index=True)
    ui.nota("Error relativo = error absoluto máximo / max|I_exacta|. El cociente punto a punto diverge en los cruces por cero.")
    r = nm.resolver_rl(L_eff, R_eff, V0, frec, I0, ppc, ciclos)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r["t"] * 1e3, y=np.abs(r["euler"] - r["exacta"]) + 1e-18, name="Euler", line=dict(color=S["euler"], width=1.4)))
    fig.add_trace(go.Scatter(x=r["t"] * 1e3, y=np.abs(r["rk4"] - r["exacta"]) + 1e-18, name="RK4", line=dict(color=S["rk4"], width=1.4)))
    fig.add_trace(go.Scatter(x=r["t"] * 1e3, y=np.abs(r["scipy"] - r["exacta"]) + 1e-18, name="SciPy", line=dict(color=S["scipy"], width=1.4)))
    ui.grafica(fig, height=320, title=f"Error absoluto en el tiempo · Δt = {r['h']*1e6:.2f} µs",
               xaxis_title="t (ms)", yaxis=dict(type="log", title="A"))
    st.download_button("Descargar tabla de convergencia (CSV)", df.to_csv(index=False).encode(), "convergencia.csv", "text/csv")

# ============================================================================
# 6. DERIVACIÓN
# ============================================================================
with tabs[5]:
    s = sympy_cache()
    ui.seccion("Ley de Faraday y Kirchhoff", "La fem inducida en la bobina es −dΦ/dt = −L dI/dt")
    st.latex(s["edo"])
    ui.seccion("Solución con sympy.dsolve", "Condición inicial I(0) = I₀")
    st.latex(s["solucion"])
    ui.seccion("Verificación", "Residuo al sustituir la solución en la EDO")
    st.latex(s["residuo"])
    ui.seccion("Régimen permanente", "Coeficientes indeterminados")
    st.latex(s["regimen"])
    c1, c2 = st.columns(2, gap="large")
    with c1:
        for k in ("Z", "modZ", "phi", "tau"):
            st.latex(s[k])
    with c2:
        for k in ("E", "P", "sensL", "sensR"):
            st.latex(s[k])
    ui.seccion("Inductancia variable", "Pieza en movimiento")
    st.latex(s["edo_var"])
    sL = -L_eff * V0 * w**2 / (R_eff**2 + (w * L_eff) ** 2) ** 1.5
    sR = -R_eff * V0 / (R_eff**2 + (w * L_eff) ** 2) ** 1.5
    ui.nota(f"Con los parámetros actuales ∂Iₚ/∂L = {sL:.3e} A/H y ∂Iₚ/∂R = {sR:.3e} A/Ω. "
            f"Un cambio de 1 % en L mueve Iₚ un {abs(sL*0.01*L_eff)/A_obj*100:.3f} % y uno de 1 % en R un "
            f"{abs(sR*0.01*R_eff)/A_obj*100:.3f} %. Con ωL/R = {w*L_eff/R_eff:.2f} domina "
            f"<b>{'la inductancia' if abs(sL*L_eff) > abs(sR*R_eff) else 'la resistencia'}</b>.")

# ============================================================================
# 7. ANÁLISIS
# ============================================================================
with tabs[6]:
    ui.seccion("Interpretación del caso actual")
    dL = (L_eff / L0 - 1) * 100
    if material.startswith("Sin"):
        texto = "Sin objeto la bobina conserva L₀ y R₀: es la referencia contra la que se mide la señal."
    elif dL < 0:
        texto = (f"El {material.lower()} reduce L en <b>{abs(dL):.2f} %</b>. Las corrientes de Foucault inducidas "
                 f"(ley de Faraday) circulan en una capa de espesor δ ≈ {delta*1e3:.2f} mm y crean un campo opuesto "
                 f"(ley de Lenz) que expulsa flujo de la bobina. Su resistencia óhmica aparece como "
                 f"ΔR = {R_eff-R0:+.3f} Ω: energía disipada como calor en la pieza ({P_obj*1e3:.3f} mW).")
    else:
        texto = (f"El {material.lower()} aumenta L en <b>{dL:.2f} %</b>: a {frec} Hz domina la magnetización "
                 f"(μᵣ = {m_sel['mu_r']:g}) sobre el apantallamiento por corrientes de Foucault. A frecuencias "
                 "mayores δ disminuye y el efecto se invierte (gráfica ΔL frente a f en la pestaña Modelo).")
    ui.nota(texto)
    ui.nota(f"Con la amplitud de corriente como señal, la pieza se detecta hasta <b>Sₙ ≈ {Sn*1e3:.1f} mm</b> "
            f"con un umbral de {umbral_pct:.1f} % (Sₙ/a = {Sn/bob.a:.2f}). El campo de una bobina decae en "
            "distancias del orden de su radio; por eso los sensores reales alcanzan ≈ 0.3–1 diámetro.")

    ui.seccion("Comparación entre materiales", f"d = {d_mm} mm, f = {frec} Hz")
    sn_acero = max(distancia_conmutacion("Acero al carbono (ferromagnético)"), 1e-9)
    filas = []
    for mat in SOLIDOS:
        info = ph.MATERIALES[mat]
        Lm, Rm = ph.parametros_efectivos(bob, d, frec, mat)
        Am = ph.amplitud_regimen(V0, Lm, Rm, frec)
        filas.append({"Material": mat, "σ (S/m)": f"{info['sigma']:.2e}", "μᵣ": info["mu_r"],
                      "δ (mm)": ph.profundidad_penetracion(frec, info["sigma"], info["mu_r"]) * 1e3,
                      "ΔL/L₀ (%)": (Lm / L0 - 1) * 100, "ΔR (Ω)": Rm - R0,
                      "|ΔI|/I (%)": abs(Am - A_libre) / A_libre * 100,
                      "Sₙ (mm)": distancia_conmutacion(mat) * 1e3,
                      "Factor": distancia_conmutacion(mat) / sn_acero})
    st.dataframe(pd.DataFrame(filas).style.format({"δ (mm)": "{:.3f}", "ΔL/L₀ (%)": "{:+.2f}", "ΔR (Ω)": "{:+.4f}",
                                                    "|ΔI|/I (%)": "{:.2f}", "Sₙ (mm)": "{:.1f}", "Factor": "{:.2f}"}),
                 width="stretch", hide_index=True)
    ui.nota("Factor = Sₙ(material) / Sₙ(acero al carbono), análogo al factor de corrección de los fabricantes "
            "(en sensores comerciales con oscilador LC: acero 1.0, inoxidable ≈ 0.7, aluminio ≈ 0.4, cobre ≈ 0.3). "
            "Este modelo RL alimentado en voltaje puede dar un orden distinto, lo cual es parte de la discusión.")

    ui.seccion("Rendimiento en una línea de producción")
    l1, l2 = st.columns(2, gap="large")
    long_obj = l1.number_input("Longitud de la pieza en la banda (mm)", 2.0, 500.0, 30.0, 1.0)
    n_demod = l2.number_input("Ciclos necesarios para demodular", 1, 50, 3)
    t_resp = 5 * tau + n_demod * T
    f_sw = 1 / (2 * t_resp)
    v_max = (long_obj / 1000) / t_resp
    ui.kv([
        ("Tiempo de respuesta 5τ + nT", f"{t_resp*1e3:.3f} ms"),
        ("Frecuencia de conmutación máx.", f"{f_sw:.0f} Hz"),
        ("Velocidad máx. de banda", f"{v_max:.2f} m/s"),
        ("Piezas por minuto", f"{60*f_sw:,.0f}"),
    ])
    ui.nota("Subir <b>f</b> acorta el tiempo de respuesta pero reduce δ: el sensor deja de distinguir entre metales "
            "no ferrosos y el acero pierde su ventaja magnética. Subir <b>N</b> aumenta L ∝ N² y la sensibilidad, "
            f"pero también τ y la resistencia del devanado. El consumo es de <b>{P_tot*1e3:.1f} mW</b>, del cual "
            f"{100*P_obj/P_tot if P_tot else 0:.2f} % se disipa en la pieza.")

    ui.seccion("Limitaciones frente a un análisis por elementos finitos")
    ui.lista([
        "<b>Objeto infinito.</b> Dodd–Deeds supone un semiespacio; piezas pequeñas, delgadas (espesor &lt; 3δ) "
        "o con bordes acoplan menos. FEM (COMSOL, FEMM, Elmer) modela la geometría real.",
        "<b>Solenoide de capa delgada</b> sin núcleo de ferrita ni blindaje; los sensores comerciales usan un núcleo "
        "en copa que concentra el campo en la cara activa.",
        "<b>Materiales lineales.</b> μᵣ constante, sin saturación, histéresis magnética ni dependencia térmica.",
        "<b>Régimen cuasi-estático.</b> Se desprecian la corriente de desplazamiento (válido si f ≪ σ/ε) y la "
        "capacitancia parásita entre espiras.",
        "<b>Movimiento axial y lento.</b> La pieza real pasa lateralmente; L(t) se toma de la curva estática L(d).",
        "<b>Electrónica idealizada.</b> Fuente de voltaje ideal y detector de pico; el sensor real usa un oscilador "
        "LC cuya amplitud se amortigua con ΔR.",
        "<b>Ventaja.</b> El modelo es semi-analítico, se evalúa en milisegundos y permite barridos interactivos que "
        "con FEM tomarían minutos por punto.",
    ])
