"""
Caso de estudio: detector de vehículos con espira inductiva en el piso (parqueadero o semáforo).

Una espira cuadrada de cable, enterrada unos centímetros en el pavimento, forma parte de un oscilador LC. Cuando
un carro se detiene o pasa encima, el chasis de acero (conductor y ferromagnético) se comporta como la placa del
modelo de Dodd–Deeds: a la frecuencia de trabajo (decenas de kHz) la profundidad de penetración en el acero es de
centésimas de milímetro, así que domina el apantallamiento por corrientes de Foucault y la inductancia de la
espira BAJA. El oscilador sube su frecuencia,  f = 1 / (2 pi sqrt(L C))  =>  f/f0 = (1 + dL/L0)^(-1/2)
(para cambios pequeños, df/f ~ -dL/(2 L0); con un carro el cambio es grande y se usa la fórmula exacta).

Modelo:
    - Espira cuadrada de lado s con N vueltas, representada por una espira circular de igual área,
      a = s / sqrt(pi).  Inductancia de una espira circular de alambre de radio r_w:
          L0 = mu0 N^2 a [ln(8a / r_w) - 2].
    - Chasis: semiespacio de acero a una altura  d = altura libre al piso + profundidad de la espira.
    - Tamaño finito del carro: el cambio de impedancia se multiplica por la fracción de área de la espira que
      el carro tapa (factor de cobertura, entre 0 y 1). Es una aproximación: el chasis real no es plano.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import physics as ph

ACERO = ph.MATERIALES["Acero al carbono (ferromagnético)"]

# Datos de fichas técnicas (ver docs/00-modelo-teorico-depa.md, sección de fuentes). Las fuentes no coinciden
# del todo; se usa el valor central y se reporta el rango.
VEHICULOS: dict[str, dict] = {
    "Chevrolet Spark GT": {
        "largo": 3.635, "ancho": 1.597, "alto": 1.522, "altura_piso": 0.150, "rango_altura": (0.150, 0.170),
        "entre_ejes": 2.375, "peso": 966, "color": "#c62a2a",
    },
    "Renault Kwid": {
        "largo": 3.680, "ancho": 1.586, "alto": 1.474, "altura_piso": 0.180, "rango_altura": (0.172, 0.185),
        "entre_ejes": 2.423, "peso": 785, "color": "#2f6fd6",
    },
}


@dataclass(frozen=True)
class Espira:
    lado: float = 1.8          # m (espira cuadrada de 6 x 6 pies, la más común)
    N: int = 3                 # vueltas
    r_alambre: float = 0.8e-3  # m (alambre calibre 14 AWG)
    R0: float = 0.6            # ohm (espira más cable de conexión)
    profundidad: float = 0.05  # m (ranura en el pavimento)
    C: float = 0.10e-6         # F (capacitor del oscilador)

    @property
    def a(self) -> float:
        return self.lado / np.sqrt(np.pi)

    @property
    def L0(self) -> float:
        return ph.MU0 * self.N**2 * self.a * (np.log(8 * self.a / self.r_alambre) - 2)

    @property
    def bobina(self) -> ph.Bobina:
        """Bobina equivalente para la integral de Dodd–Deeds (devanado plano de 1 cm de alto)."""
        return ph.Bobina(N=self.N, a=self.a, l=0.01, R0=self.R0)

    @property
    def f0(self) -> float:
        """Frecuencia del oscilador LC sin carro."""
        return 1 / (2 * np.pi * np.sqrt(self.L0 * self.C))


def cobertura_maxima(esp: Espira, veh: dict) -> float:
    """Fracción de la espira tapada con el carro centrado (el carro es más largo que la espira)."""
    return min(1.0, veh["ancho"] / esp.lado) * min(1.0, veh["largo"] / esp.lado)


def cobertura(esp: Espira, veh: dict, x) -> np.ndarray:
    """Fracción tapada cuando el centro del carro está en x (m) respecto al centro de la espira."""
    x = np.asarray(x, dtype=float)
    medio_l, medio_s = veh["largo"] / 2, esp.lado / 2
    solape = np.clip(np.minimum(x + medio_l, medio_s) - np.maximum(x - medio_l, -medio_s), 0, None)
    return (solape / esp.lado) * min(1.0, veh["ancho"] / esp.lado)


def delta_Z_vehiculo(esp: Espira, altura_piso, f: float, fraccion=1.0) -> np.ndarray:
    """Cambio de impedancia de la espira por un chasis de acero a la altura dada."""
    d = np.asarray(altura_piso, dtype=float) + esp.profundidad
    dz = ph.delta_Z(esp.bobina, d, f, ACERO["sigma"], ACERO["mu_r"])
    return dz * fraccion


def respuesta(esp: Espira, veh: dict, f: float | None = None) -> dict:
    """Respuesta con el carro detenido y centrado sobre la espira."""
    f = f or esp.f0
    w = 2 * np.pi * f
    eta = cobertura_maxima(esp, veh)
    dz = delta_Z_vehiculo(esp, veh["altura_piso"], f, eta)[0]
    dL = dz.imag / w
    return {"f": f, "cobertura": eta, "dL": dL, "dL_rel": dL / esp.L0, "dR": dz.real,
            "df_rel": 1 / np.sqrt(1 + dL / esp.L0) - 1, "d": veh["altura_piso"] + esp.profundidad,
            "delta_acero_mm": ph.profundidad_penetracion(f, ACERO["sigma"], ACERO["mu_r"]) * 1e3}


def curva_altura(esp: Espira, f: float, ancho: float = 1.59, largo: float = 3.65,
                 alturas=np.linspace(0.08, 0.45, 300)):
    """dL/L0 con el carro centrado en función de la altura libre al piso (para estimar la altura)."""
    eta = min(1.0, ancho / esp.lado) * min(1.0, largo / esp.lado)
    dz = delta_Z_vehiculo(esp, alturas, f, eta)
    return alturas, dz.imag / (2 * np.pi * f) / esp.L0


def paso(esp: Espira, veh: dict, velocidad: float, f: float | None = None, n: int = 600) -> dict:
    """El carro cruza la espira a velocidad constante (m/s). Devuelve la serie temporal de la señal."""
    f = f or esp.f0
    recorrido = veh["largo"] + esp.lado + 2.0
    x = np.linspace(-recorrido / 2, recorrido / 2, n)
    t = (x - x[0]) / velocidad
    eta = cobertura(esp, veh, x)
    dz_full = delta_Z_vehiculo(esp, veh["altura_piso"], f, 1.0)[0]
    dL_rel = eta * dz_full.imag / (2 * np.pi * f) / esp.L0
    df_rel = 1 / np.sqrt(1 + dL_rel) - 1
    return {"t": t, "x": x, "cobertura": eta, "dL_rel": dL_rel, "df_rel": df_rel, "f_osc": esp.f0 * (1 + df_rel)}


def identificar_vehiculo(esp: Espira, f: float, dL_rel_medido: float):
    """Estima la altura libre al piso desde el cambio de inductancia y elige el vehículo más parecido."""
    alturas, curva = curva_altura(esp, f)
    k = int(np.argmin(np.abs(curva - dL_rel_medido)))
    h_est = float(alturas[k])
    nombre = min(VEHICULOS, key=lambda v: abs(VEHICULOS[v]["altura_piso"] - h_est))
    return nombre, h_est


def oscilador(esp: Espira, dL_rel: float = 0.0, dR: float = 0.0, pasos_por_periodo: int = 40, periodos: int = 30,
              metodo: str = "rk4", q0: float = 1e-7):
    """Oscilador LC del detector (espira + capacitor), resuelto como sistema de primer orden.

    Kirchhoff en la malla LC con la resistencia de la espira:
        L di/dt + R i + q/C = 0,   i = dq/dt
    =>  d/dt [q, i] = [i, -(R i + q/C) / L]

    Se arranca con el capacitor cargado (q0) y se mide la frecuencia contando cruces por cero de q(t).
    Devuelve t, q, i, la frecuencia medida, la frecuencia teórica amortiguada y la energía total en el tiempo.
    """
    from . import numerics as nm

    L = esp.L0 * (1 + dL_rel)
    R = esp.R0 + dR
    C = esp.C

    def f(t, y):
        q, i = y
        return np.array([i, -(R * i + q / C) / L])

    w0 = 1 / np.sqrt(L * C)
    wd = np.sqrt(max(w0**2 - (R / (2 * L)) ** 2, 0.0))
    T = 2 * np.pi / wd
    h = T / pasos_por_periodo
    n = pasos_por_periodo * periodos
    integrador = nm.rk4_sistema if metodo == "rk4" else nm.euler_sistema
    t, y = integrador(f, [q0, 0.0], h, n)
    q, i = y[:, 0], y[:, 1]
    # cruces por cero de bajada, interpolados linealmente
    idx = np.where((q[:-1] > 0) & (q[1:] <= 0))[0]
    cruces = t[idx] + h * q[idx] / (q[idx] - q[idx + 1])
    f_med = (len(cruces) - 1) / (cruces[-1] - cruces[0]) if len(cruces) > 2 else float("nan")
    energia = 0.5 * L * i**2 + 0.5 * q**2 / C
    return {"t": t, "q": q, "i": i, "f_medida": f_med, "f_teorica": wd / (2 * np.pi), "f0": w0 / (2 * np.pi),
            "energia": energia, "h": h, "L": L, "R": R}
