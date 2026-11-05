"""Capa de presentación: temas claro/oscuro, plantilla de gráficas y componentes HTML."""
from __future__ import annotations

import html

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from matplotlib.colors import LinearSegmentedColormap

PALETAS = {
    "Claro": {
        "base": "light",
        "bg": "#fafaf9", "panel": "#f3f3f1", "sidebar": "#f3f3f1",
        "text": "#18181b", "muted": "#71717a", "faint": "#a1a1aa", "border": "#e4e4e7",
        "accent": "#2563eb", "ok": "#16a34a", "warn": "#b45309", "bad": "#dc2626",
        "series": {"exacta": "#18181b", "rk4": "#2563eb", "euler": "#dc2626", "scipy": "#a1a1aa",
                   "aux": "#b45309", "env": "#16a34a"},
        "materiales": {"Cobre": "#c2410c", "Aluminio": "#0284c7", "Latón": "#a16207",
                       "Acero inoxidable 304": "#7c3aed", "Acero al carbono (ferromagnético)": "#15803d",
                       "Sin objeto (aire)": "#a1a1aa"},
    },
    "Oscuro": {
        "base": "dark",
        "bg": "#0b0b0d", "panel": "#141417", "sidebar": "#111114",
        "text": "#ececef", "muted": "#8e8e98", "faint": "#5c5c66", "border": "#26262c",
        "accent": "#6ea8fe", "ok": "#4ade80", "warn": "#fbbf24", "bad": "#f87171",
        "series": {"exacta": "#ececef", "rk4": "#6ea8fe", "euler": "#f87171", "scipy": "#71717a",
                   "aux": "#fbbf24", "env": "#4ade80"},
        "materiales": {"Cobre": "#fb923c", "Aluminio": "#38bdf8", "Latón": "#facc15",
                       "Acero inoxidable 304": "#a78bfa", "Acero al carbono (ferromagnético)": "#4ade80",
                       "Sin objeto (aire)": "#71717a"},
    },
}

FUENTE = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, Menlo, monospace"


def aplicar_tema(nombre: str) -> dict:
    """Ajusta el tema nativo de Streamlit (widgets, tablas) y la CSS de los componentes propios."""
    global _ACTUAL
    p = _ACTUAL = PALETAS[nombre]
    opciones = {
        "base": p["base"], "primaryColor": p["accent"], "backgroundColor": p["bg"],
        "secondaryBackgroundColor": p["panel"], "textColor": p["text"], "borderColor": p["border"],
        "linkColor": p["accent"], "sidebar.backgroundColor": p["sidebar"],
        "sidebar.secondaryBackgroundColor": p["bg"],
    }
    cambio = False
    for k, v in opciones.items():
        if st._config.get_option(f"theme.{k}") != v:
            st._config.set_option(f"theme.{k}", v)
            cambio = True
    if cambio:
        st.rerun()
    _css(p)
    pio.templates["sensor"] = _plantilla(p)
    return p


def _css(p: dict) -> None:
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
:root {{
  --bg:{p['bg']}; --panel:{p['panel']}; --text:{p['text']}; --muted:{p['muted']};
  --faint:{p['faint']}; --border:{p['border']}; --accent:{p['accent']};
  --ok:{p['ok']}; --warn:{p['warn']}; --bad:{p['bad']};
}}
html, body, .stApp, .stApp p, .stApp label, .stApp li, .stApp input, .stApp textarea, .stApp button,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, [data-baseweb="popover"] li, [data-testid="stWidgetLabel"] {{
  font-family:{FUENTE} !important; }}
[data-testid="stAppDeployButton"], #MainMenu, footer {{ display:none; }}
[data-testid="stHeader"] {{ background:transparent; }}
.block-container {{ padding-top:2.2rem; padding-bottom:4rem; max-width:1320px; }}
h1, h2, h3, h4 {{ letter-spacing:-0.015em; font-weight:600; }}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{ font-size:0.82rem; color:var(--muted); }}
[data-testid="stSidebarUserContent"] {{ padding-top:1.2rem; }}
.stTabs [data-baseweb="tab-list"] {{ gap:1.6rem; border-bottom:1px solid var(--border); }}
.stTabs [data-baseweb="tab"] {{ padding:0.6rem 0; font-size:0.9rem; }}
.stTabs [data-baseweb="tab"] p {{ font-size:0.9rem; }}
.stTabs [data-baseweb="tab-highlight"] {{ height:1.5px; }}
.stTabs [data-baseweb="tab-border"] {{ display:none; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top:1.6rem; }}
.katex {{ font-size:1.05em; }}

.eyebrow {{ font-size:0.72rem; letter-spacing:0.14em; text-transform:uppercase; color:var(--muted); margin-bottom:0.4rem; }}
.titulo {{ font-size:2rem; font-weight:600; letter-spacing:-0.025em; line-height:1.15; color:var(--text); margin:0; }}
.lede {{ color:var(--muted); font-size:0.95rem; margin:0.5rem 0 1.8rem; max-width:720px; }}
.grupo {{ font-size:0.7rem; letter-spacing:0.14em; text-transform:uppercase; color:var(--faint);
          margin:1.6rem 0 0.4rem; padding-top:1rem; border-top:1px solid var(--border); }}
.grupo.primero {{ border-top:none; padding-top:0; margin-top:0.4rem; }}

.stats {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr));
          border:1px solid var(--border); border-radius:6px; margin-bottom:2rem; }}
.stat {{ padding:0.9rem 1.1rem; border-right:1px solid var(--border); }}
.stat:last-child {{ border-right:none; }}
.stat .lab {{ font-size:0.72rem; color:var(--muted); letter-spacing:0.04em; }}
.stat .val {{ font-family:{MONO}; font-size:1.25rem; color:var(--text); margin-top:0.25rem; white-space:nowrap; }}
.stat .sub {{ font-family:{MONO}; font-size:0.74rem; color:var(--faint); margin-top:0.15rem; }}
.estado {{ display:flex; align-items:center; gap:0.55rem; font-size:0.95rem; color:var(--text); margin-top:0.3rem; }}
.punto {{ width:9px; height:9px; border-radius:50%; background:var(--faint); flex:none; }}
.punto.on {{ background:var(--ok); box-shadow:0 0 0 4px color-mix(in srgb, var(--ok) 20%, transparent); }}

.seccion {{ margin:0.4rem 0 0.8rem; }}
.seccion .t {{ font-size:1rem; font-weight:600; color:var(--text); }}
.seccion .d {{ font-size:0.85rem; color:var(--muted); margin-top:0.15rem; }}
.nota {{ border-left:2px solid var(--border); padding:0.35rem 0 0.35rem 0.9rem; color:var(--muted);
         font-size:0.88rem; margin:0.6rem 0 1rem; line-height:1.55; }}
.nota b {{ color:var(--text); font-weight:600; }}
.nota.aviso {{ border-left-color:var(--warn); }}
.nota.error {{ border-left-color:var(--bad); }}
.nota.ok {{ border-left-color:var(--ok); }}
.kv {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(170px, 1fr)); gap:0;
       border-top:1px solid var(--border); margin:0.6rem 0 1.2rem; }}
.kv div {{ padding:0.7rem 0; border-bottom:1px solid var(--border); }}
.kv .lab {{ font-size:0.72rem; color:var(--muted); }}
.kv .val {{ font-family:{MONO}; font-size:1rem; color:var(--text); margin-top:0.2rem; }}
.lista {{ color:var(--muted); font-size:0.9rem; line-height:1.6; padding-left:1.1rem; }}
.lista li {{ margin-bottom:0.45rem; }}
.lista b {{ color:var(--text); font-weight:600; }}
</style>""", unsafe_allow_html=True)


def _plantilla(p: dict) -> go.layout.Template:
    eje = dict(gridcolor=p["border"], linecolor=p["border"], zeroline=False, ticks="outside",
               tickcolor=p["border"], ticklen=4, title=dict(font=dict(size=12, color=p["muted"])),
               tickfont=dict(size=11, color=p["muted"]))
    return go.layout.Template(layout=dict(
        font=dict(family=FUENTE, size=12, color=p["text"]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        colorway=list(p["series"].values()),
        xaxis=eje, yaxis=eje,
        title=dict(font=dict(size=13, color=p["text"]), x=0, xanchor="left", y=0.98),
        legend=dict(orientation="h", x=0, y=1.02, yanchor="bottom", font=dict(size=11, color=p["muted"]),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=56, r=16, t=56, b=44),
        hoverlabel=dict(font=dict(family=MONO, size=11), bgcolor=p["panel"], bordercolor=p["border"]),
        annotationdefaults=dict(font=dict(size=11, color=p["muted"])),
    ))


def grafica(fig: go.Figure, **layout) -> None:
    fig.update_layout(template="sensor", paper_bgcolor=_ACTUAL["bg"], plot_bgcolor=_ACTUAL["bg"])
    fig.update_layout(**layout)
    for a in fig.layout.annotations:  # títulos de subgráficas
        a.font = dict(size=12, color=PALETA_ACTUAL()["muted"])
        if a.xanchor == "center" and a.yanchor == "bottom":
            a.x, a.xanchor = 0, "left"
    st.plotly_chart(fig, theme=None, config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})


_ACTUAL = PALETAS["Claro"]


def PALETA_ACTUAL() -> dict:
    return _ACTUAL


def mapa_color(p: dict) -> LinearSegmentedColormap:
    return LinearSegmentedColormap.from_list("sensor", [p["bg"], p["panel"], p["accent"]])


# ---------------------------------------------------------------- componentes
def encabezado(eyebrow: str, titulo: str, lede: str) -> None:
    st.markdown(f'<div class="eyebrow">{eyebrow}</div><h1 class="titulo">{titulo}</h1>'
                f'<p class="lede">{lede}</p>', unsafe_allow_html=True)


def grupo(texto: str, primero: bool = False) -> None:
    st.sidebar.markdown(f'<div class="grupo{" primero" if primero else ""}">{texto}</div>', unsafe_allow_html=True)


def stats(items: list[tuple[str, str, str]], estado: tuple[bool, str, str] | None = None) -> None:
    celdas = "".join(f'<div class="stat"><div class="lab">{l}</div><div class="val">{v}</div>'
                     f'<div class="sub">{s}</div></div>' for l, v, s in items)
    if estado:
        on, txt, sub = estado
        celdas += (f'<div class="stat"><div class="lab">Estado</div><div class="estado">'
                   f'<span class="punto{" on" if on else ""}"></span>{txt}</div><div class="sub">{sub}</div></div>')
    st.markdown(f'<div class="stats">{celdas}</div>', unsafe_allow_html=True)


def seccion(titulo: str, desc: str = "") -> None:
    st.markdown(f'<div class="seccion"><div class="t">{titulo}</div>'
                + (f'<div class="d">{desc}</div>' if desc else "") + "</div>", unsafe_allow_html=True)


def nota(texto_html: str, tipo: str = "") -> None:
    st.markdown(f'<div class="nota {tipo}">{texto_html}</div>', unsafe_allow_html=True)


def kv(items: list[tuple[str, str]]) -> None:
    st.markdown('<div class="kv">' + "".join(f'<div><div class="lab">{l}</div><div class="val">{v}</div></div>'
                                              for l, v in items) + "</div>", unsafe_allow_html=True)


def lista(items_html: list[str]) -> None:
    st.markdown('<ul class="lista">' + "".join(f"<li>{i}</li>" for i in items_html) + "</ul>", unsafe_allow_html=True)


esc = html.escape
