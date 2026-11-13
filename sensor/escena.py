"""
Datos para la escena 3D del parqueadero (assets/escena3d.html).

Toda la física se calcula aquí, en Python, con los mismos modelos del resto del proyecto. La escena en el
navegador solo interpola y dibuja estos números.

Coordenadas de la escena (metros): el pavimento es y = 0, la espira está en y = -profundidad, el carro avanza por
el eje x y el centro de la espira es el origen.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from . import physics as ph
from . import vehiculo as vh

CORRIENTE_ESPIRA = 0.05  # A de amplitud en la espira (orden de magnitud de un detector comercial)


def _trazar(fuente, rho0, z0, a, z_min, z_max, paso, max_pasos=900):
    """Línea de campo en el plano (rho, z) con RK2, en los dos sentidos desde la semilla."""
    def campo(r, z):
        br, bz = fuente(np.array([abs(r)]), np.array([z]))
        br = br[0] * np.sign(r) if r != 0 else 0.0
        n = np.hypot(br, bz[0])
        return (br / n, bz[0] / n) if n > 0 else (0.0, 0.0)

    lineas = []
    for sentido in (1, -1):
        r, z = rho0, z0
        pts = [(r, z)]
        for _ in range(max_pasos):
            k1 = campo(r, z)
            k2 = campo(r + sentido * paso * k1[0] / 2, z + sentido * paso * k1[1] / 2)
            r, z = r + sentido * paso * k2[0], z + sentido * paso * k2[1]
            if not (z_min < z < z_max) or abs(r) > 3.2 * a:
                break
            pts.append((r, z))
            if len(pts) > 20 and np.hypot(r - rho0, z - z0) < paso:
                break
        lineas.append(pts)
    ida, vuelta = lineas
    return vuelta[::-1] + ida[1:]


def lineas_de_campo(esp: vh.Espira, f: float, altura_chasis: float | None, fraccion: float = 1.0,
                    n_planos: int = 8, semillas=(0.25, 0.45, 0.62, 0.76, 0.87, 0.94)):
    """Líneas de B en coordenadas de la escena. Sin carro (altura_chasis=None) el campo es el de la espira
    sola; con carro se agrega la espira imagen con el coeficiente efectivo del chasis (método de imágenes)."""
    bob = esp.bobina
    if altura_chasis is None:
        d = 1.0  # irrelevante: sin imagen
        gamma = 0.0
        y_techo = 2.2
    else:
        d = altura_chasis + esp.profundidad
        gamma = ph.coef_imagen(bob, d, f, "Acero al carbono (ferromagnético)") * fraccion
        y_techo = altura_chasis
    # coordenadas físicas: placa en z = 0, espira en z = d.  escena: y = altura_chasis - z  (o y = -prof - (z - d))
    def a_escena(z):
        return -esp.profundidad - (z - d)

    def fuente(rho, z):
        return ph.campo_bobina(bob, d - bob.l / 2, 1.0, rho, z, gamma, n_esp=2)

    z_min = d - (y_techo + esp.profundidad) + 1e-3   # techo de la escena (chasis o 2.2 m)
    z_max = d + 1.4                                   # 1.4 m bajo la espira
    planos = []
    for s in semillas:
        pts = _trazar(fuente, s * esp.a, d, esp.a, z_min, z_max, paso=0.025)
        if len(pts) < 4:
            continue
        planos.append([(round(r, 4), round(a_escena(z), 4)) for r, z in pts[::2]])
    angulos = [round(2 * np.pi * k / n_planos, 4) for k in range(n_planos)]
    return {"perfiles": planos, "angulos": angulos}


def escena_datos(esp: vh.Espira, umbral_pct: float, carro_inicial: str, tema: str, n_x: int = 400) -> dict:
    """Todo lo que la escena necesita, listo para json.dumps."""
    f = esp.f0
    w = 2 * np.pi * f
    carros = {}
    for nombre, v in vh.VEHICULOS.items():
        recorrido = 9.0
        x = np.linspace(-recorrido, recorrido, n_x)
        eta = vh.cobertura(esp, v, x)
        dz = vh.delta_Z_vehiculo(esp, v["altura_piso"], f, 1.0)[0]
        dL_rel = eta * dz.imag / w / esp.L0
        potencia_uW = 0.5 * eta * dz.real * CORRIENTE_ESPIRA**2 * 1e6
        r = vh.respuesta(esp, v, f)
        reconocido, h_est = vh.identificar_vehiculo(esp, f, r["dL_rel"])
        carros[nombre] = {
            "corto": nombre.split(" ")[1],
            "largo": v["largo"], "ancho": v["ancho"], "alto": v["alto"], "altura_piso": v["altura_piso"],
            "entre_ejes": v["entre_ejes"], "peso": v["peso"], "color": v["color"],
            "x": np.round(x, 3).tolist(),
            "dL_rel": np.round(dL_rel, 6).tolist(),
            "potencia_uW": np.round(potencia_uW, 3).tolist(),
            "dL_max": r["dL_rel"], "df_max_kHz": r["df_rel"] * f / 1e3,
            "reconocido": reconocido, "altura_estimada": h_est,
            "lineas": lineas_de_campo(esp, f, v["altura_piso"], r["cobertura"]),
        }
    return {
        "tema": tema,
        "carro_inicial": carro_inicial,
        "umbral_pct": umbral_pct,
        "espira": {"lado": esp.lado, "vueltas": esp.N, "profundidad": esp.profundidad, "L0_uH": esp.L0 * 1e6,
                   "f0_kHz": f / 1e3, "a_equivalente": esp.a, "corriente_A": CORRIENTE_ESPIRA,
                   "delta_acero_mm": ph.profundidad_penetracion(f, vh.ACERO["sigma"], vh.ACERO["mu_r"]) * 1e3},
        "lineas_vacio": lineas_de_campo(esp, f, None),
        "carros": carros,
    }


ASSETS = Path(__file__).resolve().parents[1] / "assets"


def html_escena(datos: dict) -> str:
    """Página completa de la escena, con Three.js y los datos incrustados (funciona sin internet)."""
    plantilla = (ASSETS / "escena3d.html").read_text(encoding="utf-8")
    three = (ASSETS / "three" / "three.min.js").read_text(encoding="utf-8")
    orbit = (ASSETS / "three" / "OrbitControls.js").read_text(encoding="utf-8")
    room = (ASSETS / "three" / "RoomEnvironment.js").read_text(encoding="utf-8")
    return (plantilla.replace("/*__THREE__*/", three)
            .replace("/*__ORBIT__*/", orbit)
            .replace("/*__ROOM__*/", room)
            .replace("/*__DATOS__*/", json.dumps(datos)))
