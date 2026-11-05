import numpy as np
import pytest

from sensor import numerics as nm
from sensor import physics as ph

BOB = ph.Bobina(N=150, a=0.015, l=0.02, R0=5.0)


def test_orden_convergencia():
    filas = nm.estudio_convergencia(0.6e-3, 5.0, 5.0, 1000, 0.0, pasos=(20, 40, 80, 160))
    assert filas[-1]["orden Euler"] == pytest.approx(1.0, abs=0.05)
    assert filas[2]["orden RK4"] == pytest.approx(4.0, abs=0.15)


def test_rk4_coincide_con_scipy():
    r = nm.resolver_rl(0.6e-3, 5.0, 5.0, 1000, 0.1, 200, 3)
    assert np.max(np.abs(r["rk4"] - r["exacta"])) < 1e-7
    assert np.max(np.abs(r["scipy"] - r["exacta"])) < 1e-6


def test_limites_fisicos():
    w = 2 * np.pi * 1000
    # conductor no magnético: L disminuye y R aumenta
    L, R = ph.parametros_efectivos(BOB, 0.005, 1000, "Cobre")
    assert L < BOB.L0 and R > BOB.R0
    # ferromagnético a baja frecuencia: L aumenta
    L, _ = ph.parametros_efectivos(BOB, 0.005, 100, "Acero al carbono (ferromagnético)")
    assert L > BOB.L0
    # el efecto decae con la distancia
    Lc, _ = ph.parametros_efectivos(BOB, 0.002, 1000, "Cobre")
    Ll, _ = ph.parametros_efectivos(BOB, 0.030, 1000, "Cobre")
    assert abs(Lc - BOB.L0) > abs(Ll - BOB.L0)
    # conductor perfecto: coeficiente de imagen -> -1
    dz = ph.delta_Z(BOB, 0.005, 1e6, 1e12, 1.0)[0]
    assert ph.coef_imagen(BOB, 0.005, 1e6, "Cobre") < -0.99
    assert dz.imag / (2 * np.pi * 1e6) < 0


def test_campo_espira_centro():
    # B en el centro de una espira: mu0 I / (2a)
    _, Bz = ph.campo_espira(0.01, 0.0, 1.0, np.array([0.0]), np.array([0.0]))
    assert Bz[0] == pytest.approx(ph.MU0 / (2 * 0.01), rel=1e-6)
