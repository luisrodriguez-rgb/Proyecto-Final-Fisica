"""
Modelo físico del sensor inductivo de proximidad.

Geometría (coordenadas cilíndricas, eje z = eje de la bobina):
    - El objeto metálico es un semiespacio conductor que ocupa z < 0.
    - La bobina es un solenoide delgado de radio a, longitud l y N espiras,
      ubicado entre z = d y z = d + l  (d = distancia cara-objeto).

Inductancia propia (bobina en aire):
    Fórmula de Wheeler para solenoide corto  L0 = mu0 N^2 pi a^2 / (l + 0.9 a)
    (el solenoide ideal mu0 N^2 A / l se reporta solo como referencia).

Efecto del objeto (corrientes de Foucault / Eddy):
    Solución de Dodd & Deeds (1968) para una bobina sobre un semiespacio
    conductor y permeable. Resolviendo las ecuaciones de Maxwell cuasi-estáticas
    (rot H = J = sigma E, rot E = -jw B) con condiciones de frontera en z = 0
    (continuidad de B_z y H_rho), el cambio de impedancia es

        dZ = j w pi mu0 a^2 N^2  ∫_0^∞  J1(αa)^2  Γ(α)  F(α)^2  dα

        F(α) = [exp(-α d) - exp(-α (d + l))] / (α l)       (suma sobre espiras)
        Γ(α) = (mu_r α - α1) / (mu_r α + α1)               (coef. de reflexión)
        α1   = sqrt(α^2 + j w mu0 mu_r sigma)

    Casos límite (método de las imágenes):
        conductor perfecto  (sigma -> ∞)        Γ -> -1   => L disminuye
        ferromagnético no conductor (sigma = 0)  Γ = (mu_r-1)/(mu_r+1) => L aumenta

    L_eff = L0 + Im(dZ)/w      R_eff = R0 + Re(dZ)
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.integrate import trapezoid
from scipy.special import ellipe, ellipk, j1

MU0 = 4e-7 * np.pi

# Conductividad sigma (S/m) y permeabilidad relativa efectiva mu_r.
MATERIALES: dict[str, dict] = {
    "Sin objeto (aire)": {"sigma": 0.0, "mu_r": 1.0, "color": "#9aa0a6"},
    "Cobre": {"sigma": 5.96e7, "mu_r": 1.0, "color": "#e07a3f"},
    "Aluminio": {"sigma": 3.77e7, "mu_r": 1.0, "color": "#7fb3d5"},
    "Latón": {"sigma": 1.5e7, "mu_r": 1.0, "color": "#d4ac0d"},
    "Acero inoxidable 304": {"sigma": 1.45e6, "mu_r": 1.02, "color": "#a569bd"},
    "Acero al carbono (ferromagnético)": {"sigma": 6.0e6, "mu_r": 100.0, "color": "#52be80"},
}


@dataclass(frozen=True)
class Bobina:
    N: int          # número de espiras
    a: float        # radio (m)
    l: float        # longitud (m)
    R0: float       # resistencia del devanado (ohm)

    @property
    def area(self) -> float:
        return np.pi * self.a**2

    @property
    def L_ideal(self) -> float:
        """Solenoide largo ideal: mu0 N^2 A / l."""
        return MU0 * self.N**2 * self.area / self.l

    @property
    def L0(self) -> float:
        """Wheeler (error ~1 % para l > 0.8 a)."""
        return MU0 * self.N**2 * self.area / (self.l + 0.9 * self.a)


def profundidad_penetracion(f: float, sigma: float, mu_r: float) -> float:
    """Skin depth delta = sqrt(2 / (w mu0 mu_r sigma)). inf si sigma = 0."""
    if sigma <= 0:
        return np.inf
    w = 2 * np.pi * f
    return np.sqrt(2.0 / (w * MU0 * mu_r * sigma))


# Malla en la variable adimensional x = α a (log-espaciada: el integrando
# decae como x^-3 para x grande y es suave cerca de 0).
_X = np.logspace(-4, np.log10(3000.0), 6000)
_J1SQ = j1(_X) ** 2


def delta_Z(bob: Bobina, d, f: float, sigma: float, mu_r: float) -> np.ndarray:
    """Cambio de impedancia complejo (ohm) por presencia del objeto. d escalar o arreglo (m)."""
    d = np.atleast_1d(np.asarray(d, dtype=float))
    if sigma <= 0 and mu_r == 1.0:
        return np.zeros_like(d, dtype=complex)
    w = 2 * np.pi * f
    alpha = _X / bob.a                                            # (M,)
    alpha1 = np.sqrt(alpha**2 + 1j * w * MU0 * mu_r * sigma)      # (M,)
    gamma = (mu_r * alpha - alpha1) / (mu_r * alpha + alpha1)     # (M,)
    dd = d[:, None]                                               # (K,1)
    F = (np.exp(-alpha * dd) - np.exp(-alpha * (dd + bob.l))) / (alpha * bob.l)
    integrando = _J1SQ * gamma * F**2                             # (K,M)
    integral = trapezoid(integrando, alpha, axis=1)
    return 1j * w * np.pi * MU0 * bob.a**2 * bob.N**2 * integral


def parametros_efectivos(bob: Bobina, d, f: float, material: str):
    """Devuelve (L_eff, R_eff) en H y ohm."""
    m = MATERIALES[material]
    dz = delta_Z(bob, d, f, m["sigma"], m["mu_r"])
    w = 2 * np.pi * f
    L = bob.L0 + dz.imag / w
    R = bob.R0 + dz.real
    if np.ndim(d) == 0:
        return float(L[0]), float(R[0])
    return L, R


def impedancia(L: float, R: float, f: float) -> complex:
    return R + 1j * 2 * np.pi * f * L


def amplitud_regimen(V0: float, L, R, f: float):
    """Amplitud de corriente en régimen permanente V0/|Z|."""
    w = 2 * np.pi * f
    return V0 / np.sqrt(R**2 + (w * L) ** 2)


def coef_imagen(bob: Bobina, d: float, f: float, material: str) -> float:
    """Coeficiente de imagen efectivo Γ_eff = ΔL / ΔL_ref, con ΔL_ref = M(bobina, imagen)
    (el valor que tendría un espejo magnético perfecto, Γ = +1). Se usa solo para
    dibujar el mapa de campo con el método de imágenes."""
    m = MATERIALES[material]
    if m["sigma"] <= 0 and m["mu_r"] == 1.0:
        return 0.0
    w = 2 * np.pi * f
    dz = delta_Z(bob, d, f, m["sigma"], m["mu_r"])[0]
    # referencia Γ = +1  <=>  sigma = 0, mu_r -> inf
    alpha = _X / bob.a
    F = (np.exp(-alpha * d) - np.exp(-alpha * (d + bob.l))) / (alpha * bob.l)
    ref = np.pi * MU0 * bob.a**2 * bob.N**2 * trapezoid(_J1SQ * F**2, alpha)
    return float((dz.imag / w) / ref)


# ---------------------------------------------------------------------------
# Campo magnético de espiras circulares (integrales elípticas, Biot–Savart)
# ---------------------------------------------------------------------------
def campo_espira(a: float, z0: float, I: float, rho: np.ndarray, z: np.ndarray):
    """(B_rho, B_z) de una espira de radio a en z = z0 con corriente I."""
    rho = np.maximum(np.abs(rho), 1e-9)
    dz = z - z0
    q = (a + rho) ** 2 + dz**2
    m = np.clip(4 * a * rho / q, 0, 1 - 1e-12)
    K, E = ellipk(m), ellipe(m)
    den = (a - rho) ** 2 + dz**2
    pref = MU0 * I / (2 * np.pi * np.sqrt(q))
    Bz = pref * (K + (a**2 - rho**2 - dz**2) / den * E)
    Br = pref * dz / rho * (-K + (a**2 + rho**2 + dz**2) / den * E)
    return Br, Bz


def campo_bobina(bob: Bobina, d: float, I: float, rho, z, gamma: float = 0.0, n_esp: int = 24):
    """Campo de la bobina (z en [d, d+l]) más su imagen con coeficiente gamma
    (espejo en z = 0). Cada espira representativa lleva N/n_esp vueltas."""
    zs = np.linspace(d, d + bob.l, n_esp)
    Ieq = I * bob.N / n_esp
    Br = np.zeros_like(rho, dtype=float)
    Bz = np.zeros_like(rho, dtype=float)
    for z0 in zs:
        br, bz = campo_espira(bob.a, z0, Ieq, rho, z)
        Br += br
        Bz += bz
        if gamma != 0.0:
            br, bz = campo_espira(bob.a, -z0, gamma * Ieq, rho, z)
            Br += br
            Bz += bz
    return Br, Bz
