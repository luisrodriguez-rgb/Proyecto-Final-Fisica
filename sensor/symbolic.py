"""Deducción simbólica con SymPy de la respuesta del circuito RL del sensor."""
from __future__ import annotations

import sympy as sp


def derivar():
    t = sp.symbols("t", nonnegative=True)
    L, R, V0, w = sp.symbols("L R V_0 omega", positive=True)
    I0 = sp.symbols("I_0", real=True)
    I = sp.Function("I")

    # Ley de Kirchhoff (Faraday): V(t) = R I + L dI/dt
    edo = sp.Eq(L * I(t).diff(t) + R * I(t), V0 * sp.sin(w * t))
    sol = sp.dsolve(edo, I(t), ics={I(0): I0})
    I_sol = sp.simplify(sol.rhs)

    # Impedancia compleja y fasor de corriente
    j = sp.I
    Z = R + j * w * L
    modZ = sp.sqrt(R**2 + (w * L) ** 2)
    phi = sp.atan(w * L / R)

    # Régimen permanente por coeficientes indeterminados: I_ss = A sin(wt) + B cos(wt)
    A, B = sp.symbols("A B")
    prueba = A * sp.sin(w * t) + B * sp.cos(w * t)
    res = sp.expand(L * prueba.diff(t) + R * prueba - V0 * sp.sin(w * t))
    coefs = sp.solve([res.coeff(sp.sin(w * t)), res.coeff(sp.cos(w * t))], [A, B])
    I_ss = prueba.subs(coefs)

    # Verificación: la solución satisface la EDO
    residuo = sp.simplify(L * I_sol.diff(t) + R * I_sol - V0 * sp.sin(w * t))

    # Energía magnética media y potencia media disipada
    Ipk = V0 / modZ
    E_mag = sp.Rational(1, 2) * L * Ipk**2
    P_med = sp.Rational(1, 2) * R * Ipk**2

    # Sensibilidad de la amplitud a la inductancia: d|I|/dL
    sens_L = sp.simplify(sp.diff(Ipk, L))
    sens_R = sp.simplify(sp.diff(Ipk, R))

    return {
        "edo": sp.latex(edo),
        "solucion": sp.latex(sp.Eq(I(t), I_sol)),
        "regimen": sp.latex(sp.Eq(sp.Symbol("I_{ss}(t)"), I_ss)),
        "Z": sp.latex(sp.Eq(sp.Symbol("Z"), Z)),
        "modZ": sp.latex(sp.Eq(sp.Symbol("|Z|"), modZ)),
        "phi": sp.latex(sp.Eq(sp.Symbol(r"\varphi"), phi)),
        "tau": sp.latex(sp.Eq(sp.Symbol(r"\tau"), L / R)),
        "residuo": sp.latex(residuo),
        "E": sp.latex(sp.Eq(sp.Symbol(r"\langle E_{mag}\rangle_{max}"), E_mag)),
        "P": sp.latex(sp.Eq(sp.Symbol(r"\langle P \rangle"), P_med)),
        "sensL": sp.latex(sp.Eq(sp.Symbol(r"\frac{\partial I_p}{\partial L}"), sens_L)),
        "sensR": sp.latex(sp.Eq(sp.Symbol(r"\frac{\partial I_p}{\partial R}"), sens_R)),
        "edo_var": r"\frac{d}{dt}\big[L(t)\,I\big] = V(t) - R(t)\,I"
                   r"\;\;\Rightarrow\;\; \frac{dI}{dt} = \frac{V(t) - \left[R(t) + \dot L(t)\right] I}{L(t)}",
    }
