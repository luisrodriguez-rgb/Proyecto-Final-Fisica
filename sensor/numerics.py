"""
Métodos numéricos programados a mano para el circuito RL del sensor.

EDO general (inductancia variable en el tiempo):
    d(L I)/dt = V(t) - R I     =>     dI/dt = [V(t) - (R + dL/dt) I] / L

Con L constante se recupera  dI/dt = [V(t) - R I] / L,  cuya solución exacta
para V(t) = V0 sin(wt) es

    I(t) = [I0 + (V0/|Z|) sin(phi)] e^{-t R/L} + (V0/|Z|) sin(wt - phi),
    |Z| = sqrt(R^2 + w^2 L^2),   phi = atan(wL / R).
"""
from __future__ import annotations

import math
from typing import Callable

import numpy as np
from scipy.integrate import solve_ivp


# ---------------------------------------------------------------------------
# Integradores genéricos (escalares)
# ---------------------------------------------------------------------------
def euler(f: Callable[[float, float], float], y0: float, h: float, n: int, t0: float = 0.0):
    """Euler explícito: y_{k+1} = y_k + h f(t_k, y_k).  Error global O(h)."""
    t = t0 + h * np.arange(n + 1)
    y = np.empty(n + 1)
    y[0] = yk = y0
    for k in range(n):
        yk = yk + h * f(t0 + k * h, yk)
        y[k + 1] = yk
    return t, y


def rk4(f: Callable[[float, float], float], y0: float, h: float, n: int, t0: float = 0.0):
    """Runge–Kutta clásico de 4.º orden.  Error global O(h^4)."""
    t = t0 + h * np.arange(n + 1)
    y = np.empty(n + 1)
    y[0] = yk = y0
    h2 = 0.5 * h
    for k in range(n):
        tk = t0 + k * h
        k1 = f(tk, yk)
        k2 = f(tk + h2, yk + h2 * k1)
        k3 = f(tk + h2, yk + h2 * k2)
        k4 = f(tk + h, yk + h * k3)
        yk = yk + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        y[k + 1] = yk
    return t, y


# ---------------------------------------------------------------------------
# Circuito RL con L constante
# ---------------------------------------------------------------------------
def rhs_rl(L: float, R: float, V0: float, f: float):
    w = 2 * math.pi * f

    def rhs(t, I):
        return (V0 * math.sin(w * t) - R * I) / L

    return rhs


def solucion_analitica(t, L: float, R: float, V0: float, f: float, I0: float = 0.0):
    w = 2 * np.pi * f
    Z = math.hypot(R, w * L)
    phi = math.atan2(w * L, R)
    A = V0 / Z
    return (I0 + A * math.sin(phi)) * np.exp(-R / L * t) + A * np.sin(w * t - phi)


def resolver_rl(L, R, V0, f, I0, pasos_por_ciclo, ciclos, fuente="ac"):
    """Resuelve con Euler, RK4, solve_ivp (RK45) y la fórmula exacta.

    fuente="ac": V(t) = V0 sin(wt); paso h = T/pasos_por_ciclo, duración ciclos*T.
    fuente="dc": interruptor como en el circuito RC de clase. Primera mitad en A
    (energizar, V = V0), segunda mitad en B (desenergizar, V = 0). Aquí
    pasos_por_ciclo son pasos por constante de tiempo tau y ciclos es la duración en tau.
    """
    if fuente == "dc":
        return _resolver_escalon(L, R, V0, I0, pasos_por_ciclo, ciclos)
    T = 1.0 / f
    n = int(pasos_por_ciclo * ciclos)
    h = T / pasos_por_ciclo
    rhs = rhs_rl(L, R, V0, f)
    t, Ie = euler(rhs, I0, h, n)
    _, Ir = rk4(rhs, I0, h, n)
    Ia = solucion_analitica(t, L, R, V0, f, I0)
    sol = solve_ivp(rhs, (0, t[-1]), [I0], t_eval=t, method="RK45", rtol=1e-9, atol=1e-12)
    return {"t": t, "h": h, "euler": Ie, "rk4": Ir, "exacta": Ia, "scipy": sol.y[0]}


def solucion_escalon(t, L: float, R: float, V0: float, I0: float, t_s: float):
    """Kirchhoff  V0 - iR - L di/dt = 0  resuelta por separación de variables:
    energizar   i(t) = i_max + (I0 - i_max) e^{-t/tau},  i_max = V0/R,  tau = L/R
    desenergizar (V0 = 0 desde t_s)  i(t) = i(t_s) e^{-(t - t_s)/tau}."""
    tau = L / R
    i_max = V0 / R
    i_s = i_max + (I0 - i_max) * math.exp(-t_s / tau)
    return np.where(t <= t_s, i_max + (I0 - i_max) * np.exp(-t / tau),
                    i_s * np.exp(-(t - t_s) / tau))


def _resolver_escalon(L, R, V0, I0, pasos_por_tau, duracion_tau):
    tau = L / R
    h = tau / pasos_por_tau
    n = 2 * max(1, int(round(pasos_por_tau * duracion_tau / 2)))
    m = n // 2
    t_s = m * h

    def carga(t, I):
        return (V0 - R * I) / L

    def descarga(t, I):
        return -R * I / L

    # Se integra por tramos para no evaluar la discontinuidad de V dentro de un paso.
    t1, e1 = euler(carga, I0, h, m)
    _, r1 = rk4(carga, I0, h, m)
    t2, e2 = euler(descarga, e1[-1], h, m, t0=t_s)
    _, r2 = rk4(descarga, r1[-1], h, m, t0=t_s)
    t = np.concatenate([t1, t2[1:]])
    s1 = solve_ivp(carga, (0, t_s), [I0], t_eval=t1, method="RK45", rtol=1e-9, atol=1e-12)
    s2 = solve_ivp(descarga, (t_s, t[-1]), [s1.y[0][-1]], t_eval=t2, method="RK45", rtol=1e-9, atol=1e-12)
    return {"t": t, "h": h, "t_s": t_s, "tau": tau, "i_max": V0 / R,
            "euler": np.concatenate([e1, e2[1:]]), "rk4": np.concatenate([r1, r2[1:]]),
            "exacta": solucion_escalon(t, L, R, V0, I0, t_s),
            "scipy": np.concatenate([s1.y[0], s2.y[0][1:]])}


def estudio_convergencia(L, R, V0, f, I0, ciclos=3, pasos=(10, 20, 40, 80, 160, 320, 640, 1280), fuente="ac"):
    """Error global máximo vs. paso h, y orden observado p = log(e1/e2)/log(h1/h2)."""
    filas = []
    for p in pasos:
        r = resolver_rl(L, R, V0, f, I0, p, ciclos, fuente)
        escala = np.max(np.abs(r["exacta"]))
        ee = np.max(np.abs(r["euler"] - r["exacta"]))
        er = np.max(np.abs(r["rk4"] - r["exacta"]))
        filas.append({
            ("pasos/τ" if fuente == "dc" else "pasos/ciclo"): p,
            "h (µs)": r["h"] * 1e6,
            "Euler e_abs (A)": ee,
            "Euler e_rel (%)": 100 * ee / escala,
            "RK4 e_abs (A)": er,
            "RK4 e_rel (%)": 100 * er / escala,
        })
    for i in range(1, len(filas)):
        a, b = filas[i - 1], filas[i]
        rh = math.log(a["h (µs)"] / b["h (µs)"])
        for m in ("Euler", "RK4"):
            e1, e2 = a[f"{m} e_abs (A)"], b[f"{m} e_abs (A)"]
            b[f"orden {m}"] = math.log(e1 / e2) / rh if e1 > 0 and e2 > 0 and e2 > 1e-14 else float("nan")
    filas[0]["orden Euler"] = filas[0]["orden RK4"] = float("nan")
    return filas


# ---------------------------------------------------------------------------
# Paso del objeto: L(t), R(t) variables
# ---------------------------------------------------------------------------
def perfil_distancia(t, t_c: float, ancho: float, d_min: float, d_max: float):
    """Objeto que se acerca y se aleja (paso por una banda transportadora).
    d(t) = d_max - (d_max - d_min) exp(-((t - t_c)/ancho)^2)."""
    g = np.exp(-(((t - t_c) / ancho) ** 2))
    d = d_max - (d_max - d_min) * g
    dd = (d_max - d_min) * g * 2 * (t - t_c) / ancho**2
    return d, dd


def simular_paso(L_de_d, R_de_d, dLdd_de_d, V0, f, I0, pasos_por_ciclo, ciclos,
                 d_min, d_max, frac_ancho=0.18):
    """Integra dI/dt = [V - (R + dL/dt) I]/L con Euler y RK4 (malla a medio paso)
    y con solve_ivp como referencia. L_de_d, R_de_d, dLdd_de_d: callables vectorizados."""
    T = 1.0 / f
    h = T / pasos_por_ciclo
    n = int(pasos_por_ciclo * ciclos)
    t_fin = n * h
    t_c, ancho = 0.5 * t_fin, frac_ancho * t_fin

    # Parámetros precalculados en la malla de medio paso (t_k, t_k + h/2, t_k + h)
    th = 0.5 * h * np.arange(2 * n + 1)
    d_h, dd_h = perfil_distancia(th, t_c, ancho, d_min, d_max)
    Lh = L_de_d(d_h)
    Rh = R_de_d(d_h)
    Ldot = dLdd_de_d(d_h) * dd_h
    w = 2 * math.pi * f
    inv2h = 2.0 / h
    Lh_l, Reff_l = Lh.tolist(), (Rh + Ldot).tolist()

    def rhs_malla(t, I):
        k = int(round(t * inv2h))
        return (V0 * math.sin(w * t) - Reff_l[k] * I) / Lh_l[k]

    t, Ie = euler(rhs_malla, I0, h, n)
    _, Ir = rk4(rhs_malla, I0, h, n)

    def rhs_cont(tt, I):
        d, dd = perfil_distancia(tt, t_c, ancho, d_min, d_max)
        return (V0 * math.sin(w * tt) - (R_de_d(d) + dLdd_de_d(d) * dd) * I) / L_de_d(d)

    sol = solve_ivp(rhs_cont, (0, t_fin), [I0], t_eval=t, method="RK45", rtol=1e-8, atol=1e-11,
                    max_step=T / 20)
    d_t, _ = perfil_distancia(t, t_c, ancho, d_min, d_max)
    return {"t": t, "h": h, "d": d_t, "L": L_de_d(d_t), "R": R_de_d(d_t),
            "euler": Ie, "rk4": Ir, "scipy": sol.y[0]}


def envolvente(I: np.ndarray, muestras_por_ciclo: int) -> np.ndarray:
    """Demodulador de pico: máximo de |I| en una ventana de un período."""
    from scipy.ndimage import maximum_filter1d
    return maximum_filter1d(np.abs(I), size=max(int(muestras_por_ciclo), 1), mode="nearest")


def comparador_histeresis(senal: np.ndarray, umbral_on: float, histeresis: float) -> np.ndarray:
    """Salida digital del sensor con histéresis (activa si senal >= umbral_on,
    se desactiva cuando cae por debajo de umbral_on*(1 - histeresis))."""
    umbral_off = umbral_on * (1.0 - histeresis)
    out = np.zeros(senal.size, dtype=int)
    estado = 0
    for i, s in enumerate(senal):
        if estado == 0 and s >= umbral_on:
            estado = 1
        elif estado == 1 and s < umbral_off:
            estado = 0
        out[i] = estado
    return out
