"""
Identificación del material y estimación de la distancia (etapas Detección y Emisiones del esquema D.E.P.A.).

Lo que el sensor mide de la "emisión" de la pieza es la corriente de la bobina: su amplitud I_p y su desfase
phi respecto al voltaje. Con ellas se reconstruye la impedancia Z = (V0 / I_p) e^{j phi} y el cambio que produce
la pieza, dZ = Z - Z0.

En el plano de impedancia normalizado,  z = dZ / (w L0),
    - la FASE de z depende sobre todo del material (sigma, mu_r) y de la frecuencia,
    - la MAGNITUD de z depende sobre todo de la distancia.
Cada material traza una curva z(d) al variar la distancia. La pieza se identifica buscando la curva de
referencia más cercana al punto medido, y la posición sobre esa curva da la distancia.
"""
from __future__ import annotations

import numpy as np

from . import physics as ph

D_REF = np.geomspace(0.5e-3, 40e-3, 400)
SOLIDOS = [m for m in ph.MATERIALES if not m.startswith("Sin")]
FERROSOS = {m for m in SOLIDOS if ph.MATERIALES[m]["mu_r"] > 10}


def residuo_relativo(z_med: np.ndarray, residuo: float) -> float:
    """Distancia a la curva más cercana dividida por el tamaño de la firma. Un valor alto indica que la pieza
    no se parece a ningún material del catálogo (aleación distinta o impurezas)."""
    return residuo / max(float(np.sqrt(np.sum(np.abs(z_med) ** 2))), 1e-12)


def firma(bob: ph.Bobina, d, f: float, sigma: float, mu_r: float) -> np.ndarray:
    """Cambio de impedancia normalizado dZ / (w L0) (adimensional)."""
    return ph.delta_Z(bob, d, f, sigma, mu_r) / (2 * np.pi * f * bob.L0)


def curvas_referencia(bob: ph.Bobina, frecs: tuple[float, ...], materiales=SOLIDOS, d=D_REF) -> dict:
    """Para cada material, matriz (len(d), len(frecs)) de firmas complejas."""
    return {m: np.stack([firma(bob, d, f, ph.MATERIALES[m]["sigma"], ph.MATERIALES[m]["mu_r"]) for f in frecs], axis=1)
            for m in materiales}


def medir(bob: ph.Bobina, frecs, V0: float, sigma: float, mu_r: float, d: float,
          ruido_amp: float = 0.0, ruido_fase_deg: float = 0.0, rng=None) -> np.ndarray:
    """Simula la medición: corriente con ruido en amplitud (relativo) y fase (grados) en cada frecuencia,
    y devuelve la firma reconstruida dZ/(w L0) para cada frecuencia."""
    rng = rng or np.random.default_rng()
    out = []
    for f in frecs:
        w = 2 * np.pi * f
        Z0 = bob.R0 + 1j * w * bob.L0
        Z = Z0 + ph.delta_Z(bob, d, f, sigma, mu_r)[0]
        I = V0 / Z
        I_med = abs(I) * (1 + ruido_amp * rng.standard_normal()) * \
            np.exp(1j * (np.angle(I) + np.radians(ruido_fase_deg) * rng.standard_normal()))
        Z_med = V0 / I_med
        out.append((Z_med - Z0) / (w * bob.L0))
    return np.array(out)


def identificar(z_med: np.ndarray, refs: dict, d=D_REF):
    """Curva de referencia más cercana. Devuelve (material, distancia estimada, residuo, ranking)."""
    ranking = []
    for m, curva in refs.items():
        dist = np.sqrt(np.sum(np.abs(curva - z_med[None, :]) ** 2, axis=1))
        k = int(np.argmin(dist))
        ranking.append((float(dist[k]), m, float(d[k])))
    ranking.sort()
    residuo, material, d_est = ranking[0]
    return material, d_est, residuo, ranking


def evaluar(bob: ph.Bobina, frecs, V0: float, ruido_amp: float, ruido_fase_deg: float,
            d_min=1e-3, d_max=15e-3, n_por_material=60, semilla=0):
    """Monte Carlo: piezas de cada material a distancias aleatorias entre d_min y d_max.
    Devuelve la exactitud por material, la exactitud ferroso / no ferroso, la matriz de confusión y el error
    medio de distancia de las piezas bien identificadas."""
    rng = np.random.default_rng(semilla)
    refs = curvas_referencia(bob, tuple(frecs))
    idx = {m: i for i, m in enumerate(SOLIDOS)}
    conf = np.zeros((len(SOLIDOS), len(SOLIDOS)), dtype=int)
    err_d = []
    aciertos_grupo = 0
    for m in SOLIDOS:
        s, mu = ph.MATERIALES[m]["sigma"], ph.MATERIALES[m]["mu_r"]
        for d in rng.uniform(d_min, d_max, n_por_material):
            z = medir(bob, frecs, V0, s, mu, d, ruido_amp, ruido_fase_deg, rng)
            m_est, d_est, _, _ = identificar(z, refs)
            conf[idx[m], idx[m_est]] += 1
            aciertos_grupo += (m in FERROSOS) == (m_est in FERROSOS)
            if m_est == m:
                err_d.append(abs(d_est - d))
    exactitud = np.trace(conf) / conf.sum()
    return {"exactitud": float(exactitud), "exactitud_ferroso": aciertos_grupo / conf.sum(), "confusion": conf,
            "error_distancia_mm": float(np.mean(err_d) * 1e3) if err_d else float("nan")}
