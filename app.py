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
from sensor import identificacion as idf
from sensor import numerics as nm
from sensor import physics as ph
from sensor import vehiculo as vh
from sensor import escena as esc
import streamlit.components.v1 as components
from sensor.symbolic import derivar

st.set_page_config(page_title="SEMP · Sensor de proximidad", page_icon=":material/sensors:", layout="wide")

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
fuente_lbl = sb.radio("Alimentación en la pestaña Respuesta temporal",
                      ["Alterna  V₀ sin ωt", "Escalón DC  (energizar y desenergizar)"])
fuente = "dc" if fuente_lbl.startswith("Escalón") else "ac"
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
if fuente == "dc":
    ppc = sb.slider("Pasos por constante de tiempo  (Δt = τ/n)", 2, 200, 10, 1)
    ciclos = sb.slider("Duración total (en τ)", 2, 20, 10, 2)
else:
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
    "SEMP · Electromagnetismo · Proyecto final",
    "Sensor electromagnético de proximidad",
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

tabs = st.tabs(["Caso: vehículo", "Modelo", "Respuesta temporal", "Paso del objeto", "Identificación", "Campo",
                "Validación", "Derivación", "Análisis"])

@st.cache_data(show_spinner=False)
def figura_anatomy(tema):
    carpeta = Path(__file__).resolve().parent / "figuras-anatomy" / "corte-espira"
    archivo = "corte-espira.html" if tema == "Oscuro" else "corte-espira-light.html"
    return (carpeta / archivo).read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def escena_cache(lado, vueltas, prof_cm, sens_pct, carro, tema):
    espira = vh.Espira(lado=lado, N=vueltas, profundidad=prof_cm / 100)
    return esc.html_escena(esc.escena_datos(espira, sens_pct, carro, tema))


# ============================================================================
# 0. CASO DE ESTUDIO: VEHÍCULO SOBRE UNA ESPIRA EN EL PISO
# ============================================================================
with tabs[0]:
    ui.seccion("Caso de estudio: detector de vehículos con espira en el piso",
               "Entrada de un parqueadero: una espira enterrada en el pavimento detecta el carro, reconoce el modelo "
               "y abre la talanquera.")
    ui.pasos([
        ("D", "Detección", "¿Hay un carro sobre la espira? ¿Cuál es: Spark o Kwid? Su altura al piso es la distancia "
                           "que importa."),
        ("E", "Emisiones", "El chasis de acero responde al campo de la espira con corrientes de Foucault que bajan "
                           "la inductancia de la espira."),
        ("P", "Propiedades", "A la frecuencia del oscilador (decenas de kHz) el campo entra apenas una fracción de "
                             "milímetro en el acero; la magnitud del cambio depende de la altura del chasis."),
        ("A", "Alerta", "El oscilador cambia de frecuencia; si supera el umbral se abre la talanquera y se registra "
                        "el modelo del carro."),
    ])
    v1, v2, v3 = st.columns(3, gap="large")
    carro = v1.selectbox("Carro", list(vh.VEHICULOS), key="carro")
    vel_kmh = v1.slider("Velocidad al cruzar (km/h)", 3, 40, 10, 1)
    lado = v2.slider("Lado de la espira cuadrada (m)", 0.8, 2.5, 1.8, 0.1)
    vueltas = v2.slider("Vueltas de la espira", 1, 6, 3, 1)
    prof_cm = v3.slider("Profundidad de la espira en el pavimento (cm)", 2, 10, 5, 1)
    sens_pct = v3.slider("Sensibilidad del detector |ΔL/L| (%)", 0.1, 5.0, 1.0, 0.1)
    esp = vh.Espira(lado=lado, N=vueltas, profundidad=prof_cm / 100)
    veh = vh.VEHICULOS[carro]
    res = vh.respuesta(esp, veh)
    pasa = vh.paso(esp, veh, vel_kmh / 3.6)
    detecta = abs(res["dL_rel"]) * 100 >= sens_pct
    est, h_est = vh.identificar_vehiculo(esp, res["f"], res["dL_rel"])
    ui.stats(
        [("Inductancia de la espira", f"{esp.L0*1e6:.1f} µH", f"{vueltas} vueltas, {lado:.1f} m"),
         ("Oscilador sin carro", f"{esp.f0/1e3:.1f} kHz", f"δ en el acero {res['delta_acero_mm']:.3f} mm"),
         ("ΔL/L con el carro", f"{res['dL_rel']*100:.2f} %", f"cobertura {res['cobertura']*100:.0f} %"),
         ("Δf del oscilador", f"{res['df_rel']*esp.f0/1e3:+.2f} kHz", f"{res['df_rel']*100:+.2f} %")],
        estado=(detecta, f"Talanquera abierta: {est.split(' ')[1] if ' ' in est else est}" if detecta
                else "Sin vehículo", f"altura estimada {h_est*100:.1f} cm" if detecta else f"umbral {sens_pct:.1f} %"),
    )
    ui.seccion("Escena 3D", "El carro llega, se detiene sobre la espira, el detector lo reconoce y la talanquera se "
               "abre. Todos los números de la escena salen del modelo de Python.")
    components.html(escena_cache(lado, vueltas, prof_cm, sens_pct, carro, tema or "Claro"), height=640)
    ui.seccion("Corte del detector", "Figura ilustrada (Anatomy): el pavimento cortado por el centro de la espira, "
               "las 3 vueltas de alambre en la ranura, el cable al detector y el chasis a la altura de cada carro. "
               "Pasa el cursor a la izquierda (Spark) o a la derecha (Kwid) para cambiar de carro.")
    components.html(figura_anatomy(tema or "Claro"), height=780, scrolling=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        fig = go.Figure()
        for nombre, v in vh.VEHICULOS.items():
            p_ = vh.paso(esp, v, vel_kmh / 3.6)
            fig.add_trace(go.Scatter(x=p_["t"], y=-p_["dL_rel"] * 100, name=nombre,
                                     line=dict(color=v["color"], width=2.6 if nombre == carro else 1.3)))
        fig.add_hline(y=sens_pct, line_dash="dash", line_color=P["text"], line_width=1,
                      annotation_text="umbral", annotation_position="top right")
        ui.grafica(fig, height=380, title=f"Señal mientras el carro cruza a {vel_kmh} km/h",
                   xaxis_title="t (s)", yaxis_title="−ΔL/L (%)")
    with c2:
        alt, curva = vh.curva_altura(esp, res["f"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=alt * 100, y=-curva * 100, name="cualquier carro compacto",
                                 line=dict(color=P["muted"], width=1.6)))
        for nombre, v in vh.VEHICULOS.items():
            r_ = vh.respuesta(esp, v)
            lo, hi = v["rango_altura"]
            fig.add_vrect(x0=lo * 100, x1=hi * 100, fillcolor=v["color"], opacity=0.10, line_width=0)
            fig.add_trace(go.Scatter(x=[v["altura_piso"] * 100], y=[-r_["dL_rel"] * 100], name=nombre,
                                     mode="markers", marker=dict(size=11, color=v["color"])))
        ui.grafica(fig, height=380, title="Cambio de inductancia frente a la altura libre al piso",
                   xaxis_title="altura libre al piso (cm)", yaxis_title="−ΔL/L (%)")
    filas = []
    for nombre, v in vh.VEHICULOS.items():
        r_ = vh.respuesta(esp, v)
        filas.append({"Carro": nombre, "Largo (m)": v["largo"], "Ancho (m)": v["ancho"],
                      "Altura al piso (cm)": f"{v['altura_piso']*100:.0f} ({v['rango_altura'][0]*100:.0f}–{v['rango_altura'][1]*100:.0f})",
                      "Peso (kg)": v["peso"], "Distancia chasis–espira (cm)": f"{r_['d']*100:.0f}",
                      "ΔL/L (%)": f"{r_['dL_rel']*100:.2f}", "Δf (kHz)": f"{r_['df_rel']*esp.f0/1e3:+.2f}"})
    st.dataframe(pd.DataFrame(filas), width="stretch", hide_index=True)
    ui.nota("La espira se modela como una espira circular de igual área y el chasis como una placa de acero a la "
            "altura libre al piso; el resultado se multiplica por la fracción de la espira que tapa el carro. Como el "
            "chasis real no es plano y tiene huecos, estos cambios son una <b>cota superior</b>: los detectores "
            "comerciales reportan cambios de pocos por ciento. Los dos carros se distinguen por la altura, pero la "
            "diferencia es pequeña: la carga (pasajeros, baúl) baja el carro y puede confundirlos.")

# ============================================================================
# 1. MODELO
# ============================================================================
with tabs[1]:
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
with tabs[2]:
    r = nm.resolver_rl(L_eff, R_eff, V0, frec, I0, ppc, ciclos, fuente)
    t_ms = r["t"] * 1e3
    fig = go.Figure()
    for y0, y1 in (() if fuente == "dc" else
                   ((A_libre * (1 - umbral), A_libre * (1 + umbral)), (-A_libre * (1 + umbral), -A_libre * (1 - umbral)))):
        fig.add_hrect(y0=y0, y1=y1, fillcolor=P["accent"], opacity=0.08, line_width=0)
    if fuente == "dc":
        i_max = r["i_max"]
        fig.add_hline(y=i_max, line_dash="dot", line_color=P["faint"], line_width=1,
                      annotation_text="i_max = V₀/R", annotation_position="top left")
        fig.add_hline(y=0.632 * i_max, line_dash="dot", line_color=P["faint"], line_width=1,
                      annotation_text="0.63 i_max", annotation_position="bottom left")
        fig.add_vline(x=tau * 1e3, line_dash="dot", line_color=P["faint"], line_width=1,
                      annotation_text="t = τ", annotation_position="top right")
        fig.add_vline(x=r["t_s"] * 1e3, line_dash="dash", line_color=P["muted"], line_width=1,
                      annotation_text="interruptor A → B", annotation_position="top right")
    for s_ in (() if fuente == "dc" else (1, -1)):
        fig.add_hline(y=s_ * A_libre, line_dash="dot", line_color=P["faint"], line_width=1)
    fig.add_trace(go.Scatter(x=t_ms, y=r["exacta"], name="Exacta", line=dict(color=S["exacta"], width=2.2)))
    fig.add_trace(go.Scatter(x=t_ms, y=r["scipy"], name="SciPy RK45", line=dict(color=S["scipy"], width=1)))
    fig.add_trace(go.Scatter(x=t_ms, y=r["rk4"], name="RK4", mode="lines+markers",
                             marker=dict(size=3.5), line=dict(color=S["rk4"], width=1.2, dash="dash")))
    fig.add_trace(go.Scatter(x=t_ms, y=r["euler"], name="Euler", mode="lines+markers",
                             marker=dict(size=3.5), line=dict(color=S["euler"], width=1.2, dash="dot")))
    ui.grafica(fig, height=460, title=(f"Energizar y desenergizar la bobina con el objeto a {d_mm} mm"
                                       if fuente == "dc" else f"Corriente I(t) con el objeto a {d_mm} mm"),
               xaxis_title="t (ms)", yaxis_title="I (A)")
    if fuente == "dc":
        st.latex(r"\varepsilon - iR - L\frac{di}{dt}=0\;\Rightarrow\;"
                 r"\int_0^t\frac{dt}{\tau}=\int_0^{i(t)}\frac{di}{i_{max}-i}\;\Rightarrow\;"
                 r"i(t)=i_{max}\left(1-e^{-t/\tau}\right),\quad \tau=\frac{L}{R}")
        ui.nota("Es el mismo procedimiento del circuito RC visto en clase (ley de mallas de Kirchhoff y separación "
                "de variables), con la bobina en lugar del capacitor: en t = τ la corriente llega al 63 % de "
                f"i_max = {r['i_max']:.3f} A. Al pasar el interruptor a B la fem se anula y la corriente decae como "
                "i(t_s)·e^(−(t−t_s)/τ). La bobina se opone a cambios de corriente como el capacitor a cambios de voltaje.")
    else:
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
with tabs[3]:
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
# 4. IDENTIFICACIÓN (esquema D.E.P.A.)
# ============================================================================
@st.cache_data(show_spinner=False)
def refs_cache(N, a, l, R0, frecs):
    return idf.curvas_referencia(ph.Bobina(N, a, l, R0), frecs)


@st.cache_data(show_spinner=False)
def eficiencia_cache(N, a, l, R0, frecs, V0, ra, rf, dmax):
    return idf.evaluar(ph.Bobina(N, a, l, R0), frecs, V0, ra, rf, d_max=dmax, n_por_material=40)


with tabs[4]:
    ui.seccion("Caso de estudio: línea de autopartes con piezas de distintos metales",
               "El sensor no solo avisa que hay una pieza: identifica de qué metal es y a qué distancia está.")
    ui.pasos([
        ("D", "Detección", "Qué hay que detectar: el tipo de material y la distancia de la pieza."),
        ("E", "Emisiones", "La respuesta de la pieza al campo: las corrientes de Foucault cambian la corriente "
                           "de la bobina, que se mide en amplitud y fase."),
        ("P", "Propiedades", "La frecuencia fija la profundidad δ y separa los materiales; la potencia "
                             "intercambiada indica qué tan cerca está la pieza."),
        ("A", "Alerta", "Salida del sensor: material, distancia y aviso cuando la pieza no coincide con "
                        "ningún material conocido."),
    ])
    c1, c2, c3 = st.columns(3, gap="large")
    pieza = c1.selectbox("Pieza que pasa por la línea", SOLIDOS, key="pieza_id")
    pureza = c1.slider("Conductividad de la pieza (% del valor nominal)", 50, 120, 100, 5,
                       help="Valores distintos de 100 % simulan una aleación diferente o impurezas.")
    d_id_mm = c2.slider("Distancia real de la pieza (mm)", 1.0, 20.0, 6.0, 0.5, key="d_id")
    dos_f = c2.toggle(f"Medir con dos frecuencias ({frec} Hz y {5*frec} Hz)", value=True)
    ruido_a = c3.slider("Ruido en la amplitud medida (%)", 0.0, 2.0, 0.2, 0.1) / 100
    ruido_f = c3.slider("Ruido en la fase medida (°)", 0.0, 2.0, 0.1, 0.1)
    n_prom = c3.select_slider("Mediciones promediadas", [1, 4, 16, 64, 256], value=16,
                              help="Promediar n mediciones divide el ruido entre √n, pero alarga el tiempo de medida.")
    ruido_a, ruido_f = ruido_a / np.sqrt(n_prom), ruido_f / np.sqrt(n_prom)
    if c3.button("Nueva medición"):
        st.session_state.semilla_id = st.session_state.get("semilla_id", 0) + 1
    frecs = (frec, 5 * frec) if dos_f else (frec,)
    refs = refs_cache(N, bob.a, bob.l, R0, frecs)
    mp = ph.MATERIALES[pieza]
    rng = np.random.default_rng(st.session_state.get("semilla_id", 0))
    z_med = idf.medir(bob, frecs, V0, mp["sigma"] * pureza / 100, mp["mu_r"], d_id_mm / 1000, ruido_a, ruido_f, rng)
    m_est, d_est, residuo, ranking = idf.identificar(z_med, refs)
    r_rel = idf.residuo_relativo(z_med, residuo)
    # ¿la pieza supera el umbral de detección? (cambio de amplitud en la frecuencia principal)
    Lp, Rp = ph.parametros_efectivos(bob, d_id_mm / 1000, frec, pieza)
    s_pieza = abs(ph.amplitud_regimen(V0, Lp, Rp, frec) - A_libre) / A_libre
    # Límite del residuo: 1 % de la firma, o tres veces el error que produce el ruido de medida en ΔZ/ωL₀
    tam_firma = float(np.sqrt(np.sum(np.abs(z_med) ** 2)))
    ruido_z = abs(R0 + 1j * w * L0) * (ruido_a + np.radians(ruido_f)) / (w * L0) * np.sqrt(len(frecs))
    umbral_res = max(0.01, 3 * ruido_z / max(tam_firma, 1e-12))
    en_rango = s_pieza >= umbral
    acierto = m_est == pieza

    if not en_rango:
        estado, sub = "Sin pieza en rango", f"señal {s_pieza*100:.2f} % < umbral {umbral_pct:.1f} %"
    else:
        estado = f"{m_est} a {d_est*1e3:.1f} mm"
        sub = ("posible impureza o aleación fuera de catálogo" if r_rel > umbral_res
               else ("ferroso" if m_est in idf.FERROSOS else "no ferroso"))
    ui.stats(
        [("Pieza real", pieza.split(" (")[0], f"{d_id_mm:.1f} mm · σ {pureza} %"),
         ("Material estimado", m_est.split(" (")[0], "correcto" if acierto else "error de identificación"),
         ("Distancia estimada", f"{d_est*1e3:.2f} mm", f"error {abs(d_est*1e3-d_id_mm):.2f} mm"),
         ("Residuo relativo", f"{r_rel*100:.2f} %", f"límite {umbral_res*100:.1f} %")],
        estado=(en_rango, estado, sub),
    )

    col1, col2 = st.columns([1.2, 1], gap="large")
    with col1:
        fig = go.Figure()
        for m, curva in refs.items():
            z0 = curva[:, 0]
            sel = idf.D_REF <= 25e-3
            fig.add_trace(go.Scatter(x=z0.real[sel], y=z0.imag[sel], name=m.split(" (")[0], mode="lines",
                                     line=dict(color=MC[m], width=2.4 if m == pieza else 1.3)))
            for dm in (2, 5, 10, 20):
                k = int(np.argmin(abs(idf.D_REF - dm / 1000)))
                fig.add_trace(go.Scatter(x=[z0.real[k]], y=[z0.imag[k]], mode="markers+text", showlegend=False,
                                         text=[f"{dm}"] if m == SOLIDOS[0] else None, textposition="top center",
                                         marker=dict(size=4, color=MC[m]), hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=[z_med[0].real], y=[z_med[0].imag], name="Medición", mode="markers",
                                 marker=dict(size=12, color=P["text"], symbol="x")))
        fig.add_hline(y=0, line_color=P["faint"], line_width=1)
        ui.grafica(fig, height=460, title=f"Plano de impedancia a {frec} Hz  ·  ΔZ / ωL₀",
                   xaxis_title="Re ΔZ / ωL₀  (pérdidas)", yaxis_title="Im ΔZ / ωL₀  (cambio de inductancia)")
        ui.nota("Cada curva es la firma de un material al variar la distancia (los puntos marcan 2, 5, 10 y 20 mm). "
                "La <b>dirección</b> de la curva depende del material y de la frecuencia; la <b>distancia al origen</b> "
                "depende de qué tan cerca está la pieza. La medición (×) se asigna a la curva más cercana.")
    with col2:
        ui.seccion("Ranking de materiales", "Distancia de la medición a cada curva de referencia")
        st.dataframe(pd.DataFrame([{"Material": m.split(" (")[0], "Distancia a la curva": f"{r:.2e}",
                                    "Distancia estimada (mm)": f"{dd*1e3:.2f}"} for r, m, dd in ranking]),
                     width="stretch", hide_index=True)
        fase = np.degrees(np.angle(z_med))
        ui.kv([(f"Fase de ΔZ a {f_} Hz", f"{fa:.1f}°") for f_, fa in zip(frecs, fase)] +
              [(f"|ΔZ|/ωL₀ a {f_} Hz", f"{abs(zz):.4f}") for f_, zz in zip(frecs, z_med)])

    t_medida = n_prom * len(frecs) * 3 * T
    ui.nota(f"Ruido efectivo después de promediar {n_prom} mediciones: {ruido_a*100:.3f} % en amplitud y "
            f"{ruido_f:.3f}° en fase. Tiempo de medida ≈ {t_medida*1e3:.1f} ms (3 ciclos por medición y frecuencia): "
            f"a 1 m/s la pieza avanza {t_medida*1e3:.0f} mm mientras se mide.")
    ui.seccion("Eficiencia de la solución",
               "Simulación Monte Carlo: 40 piezas de cada material a distancias aleatorias entre 1 mm y la distancia máxima")
    e1, e2 = st.columns([1, 2], gap="large")
    d_max_ef = e1.slider("Distancia máxima de las piezas (mm)", 4, 20, 8, 1)
    ef = eficiencia_cache(N, bob.a, bob.l, R0, frecs, V0, ruido_a, ruido_f, d_max_ef / 1000)
    with e1:
        ui.kv([("Material correcto", f"{ef['exactitud']*100:.0f} %"),
               ("Ferroso / no ferroso correcto", f"{ef['exactitud_ferroso']*100:.0f} %"),
               ("Error medio de distancia", f"{ef['error_distancia_mm']:.2f} mm")])
    with e2:
        nombres = [m.split(" (")[0] for m in SOLIDOS]
        conf = ef["confusion"]
        fig = go.Figure(go.Heatmap(z=conf, x=nombres, y=nombres, colorscale=[[0, P["bg"]], [1, P["accent"]]],
                                   showscale=False, text=conf, texttemplate="%{text}"))
        fig.update_yaxes(autorange="reversed", title_text="real")
        fig.update_xaxes(title_text="estimado")
        ui.grafica(fig, height=340, title="Matriz de confusión", margin=dict(l=170, r=16, t=56, b=60))
    ui.nota("Separar ferrosos de no ferrosos es robusto aun con ruido, porque la fase cambia de signo. Distinguir "
            "cobre, aluminio y latón exige poco ruido: sus curvas están cerca. Medir con dos frecuencias separa mejor "
            "las curvas y mejora la exactitud. Detectar impurezas es lo más exigente: un cambio del 20 % en la "
            "conductividad desplaza la firma apenas un 1.5 %, y una pieza de cobre con el 60 % de su conductividad "
            "es indistinguible del aluminio, porque el sensor solo ve σ y μᵣ. Por eso se necesitan muchos promedios "
            "o, en equipos reales, una medición diferencial que anule Z₀.")

# ============================================================================
# 5. CAMPO
# ============================================================================
with tabs[5]:
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
# 6. VALIDACIÓN
# ============================================================================
with tabs[6]:
    conv = nm.estudio_convergencia(L_eff, R_eff, V0, frec, I0, ciclos=6 if fuente == "dc" else 3, fuente=fuente,
                                   pasos=(2, 4, 8, 16, 32, 64, 128, 256) if fuente == "dc" else
                                   (10, 20, 40, 80, 160, 320, 640, 1280))
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
        fig.add_vline(x=(tau if fuente == "dc" else T) / ppc * 1e6, line_dash="dot", line_color=P["muted"], line_width=1,
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
    r = nm.resolver_rl(L_eff, R_eff, V0, frec, I0, ppc, ciclos, fuente)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r["t"] * 1e3, y=np.abs(r["euler"] - r["exacta"]) + 1e-18, name="Euler", line=dict(color=S["euler"], width=1.4)))
    fig.add_trace(go.Scatter(x=r["t"] * 1e3, y=np.abs(r["rk4"] - r["exacta"]) + 1e-18, name="RK4", line=dict(color=S["rk4"], width=1.4)))
    fig.add_trace(go.Scatter(x=r["t"] * 1e3, y=np.abs(r["scipy"] - r["exacta"]) + 1e-18, name="SciPy", line=dict(color=S["scipy"], width=1.4)))
    ui.grafica(fig, height=320, title=f"Error absoluto en el tiempo · Δt = {r['h']*1e6:.2f} µs",
               xaxis_title="t (ms)", yaxis=dict(type="log", title="A"))
    st.download_button("Descargar tabla de convergencia (CSV)", df.to_csv(index=False).encode(), "convergencia.csv", "text/csv")

# ============================================================================
# 7. DERIVACIÓN
# ============================================================================
with tabs[7]:
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
# 8. ANÁLISIS
# ============================================================================
with tabs[8]:
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
