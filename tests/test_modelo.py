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


def test_escalon_dc_como_circuito_rc():
    L, R, V0 = 0.6e-3, 5.0, 5.0
    r = nm.resolver_rl(L, R, V0, 1000, 0.0, 200, 10, fuente="dc")
    tau, i_max = L / R, V0 / R
    # en t = tau la corriente alcanza el 63 % de i_max (igual que q(tau) = 0.63 q_max)
    k = int(round(tau / r["h"]))
    assert r["exacta"][k] == pytest.approx(i_max * (1 - np.exp(-1)), rel=1e-9)
    assert np.max(np.abs(r["rk4"] - r["exacta"])) < 1e-8
    # al desenergizar la corriente decae a cero
    assert abs(r["exacta"][-1]) < 0.01 * i_max


def test_orden_convergencia_dc():
    filas = nm.estudio_convergencia(0.6e-3, 5.0, 5.0, 1000, 0.0, ciclos=6, pasos=(10, 20, 40, 80), fuente="dc")
    assert filas[-1]["orden Euler"] == pytest.approx(1.0, abs=0.08)
    assert filas[2]["orden RK4"] == pytest.approx(4.0, abs=0.2)


def test_balance_de_energia_al_energizar():
    from scipy.integrate import trapezoid
    L, R, V0 = 0.6e-3, 5.0, 5.0
    r = nm.resolver_rl(L, R, V0, 1000, 0.0, 200, 10, fuente="dc")
    m = r["t"] <= r["t_s"]
    t, i = r["t"][m], r["rk4"][m]
    entregada = trapezoid(V0 * i, t)
    calor = trapezoid(R * i**2, t)
    magnetica = 0.5 * L * i[-1] ** 2
    assert entregada == pytest.approx(calor + magnetica, rel=1e-5)


def test_campo_lejano_es_dipolo():
    I = 1.0
    m = BOB.N * I * np.pi * BOB.a**2
    z = 0.3
    _, Bz = ph.campo_bobina(BOB, 0.0, I, np.array([0.0]), np.array([BOB.l / 2 + z]), 0.0, n_esp=150)
    assert Bz[0] == pytest.approx(ph.MU0 * 2 * m / (4 * np.pi * z**3), rel=0.01)


def test_identifica_material_y_distancia_sin_ruido():
    from sensor import identificacion as idf
    refs = idf.curvas_referencia(BOB, (1000,))
    for m in idf.SOLIDOS:
        s, mu = ph.MATERIALES[m]["sigma"], ph.MATERIALES[m]["mu_r"]
        z = idf.medir(BOB, (1000,), 5.0, s, mu, 0.006)
        m_est, d_est, _, _ = idf.identificar(z, refs)
        assert m_est == m
        assert d_est == pytest.approx(0.006, abs=0.2e-3)


def test_impureza_aumenta_el_residuo():
    from sensor import identificacion as idf
    refs = idf.curvas_referencia(BOB, (1000,))
    puro = idf.medir(BOB, (1000,), 5.0, 5.96e7, 1.0, 0.005)
    impuro = idf.medir(BOB, (1000,), 5.0, 0.8 * 5.96e7, 1.0, 0.005)
    r_puro = idf.residuo_relativo(puro, idf.identificar(puro, refs)[2])
    r_impuro = idf.residuo_relativo(impuro, idf.identificar(impuro, refs)[2])
    assert r_impuro > 4 * r_puro


def test_espira_y_carros():
    from sensor import vehiculo as vh
    e = vh.Espira()
    # inductancia de una espira de 6 x 6 pies con 3 vueltas: del orden de 70 – 90 µH
    assert 60e-6 < e.L0 < 100e-6
    spark = vh.respuesta(e, vh.VEHICULOS["Chevrolet Spark GT"])
    kwid = vh.respuesta(e, vh.VEHICULOS["Renault Kwid"])
    # el chasis de acero baja la inductancia y sube la frecuencia del oscilador
    assert spark["dL_rel"] < 0 and spark["df_rel"] > 0
    # el Kwid es más alto: menor cambio
    assert abs(kwid["dL_rel"]) < abs(spark["dL_rel"])
    for nombre, v in vh.VEHICULOS.items():
        r = vh.respuesta(e, v)
        assert vh.identificar_vehiculo(e, e.f0, r["dL_rel"])[0] == nombre


def test_datos_de_la_escena_3d():
    import json
    from sensor import escena, vehiculo as vh
    e = vh.Espira()
    d = escena.escena_datos(e, 1.0, "Renault Kwid", "Claro")
    json.dumps(d)
    for nombre, c in d["carros"].items():
        # la señal de la escena coincide con el modelo: máximo con el carro centrado
        assert min(c["dL_rel"]) == pytest.approx(vh.respuesta(e, vh.VEHICULOS[nombre])["dL_rel"], rel=1e-3)
        assert c["reconocido"] == nombre
        # las líneas de campo con el carro no pasan del chasis
        assert max(y for perfil in c["lineas"]["perfiles"] for _, y in perfil) <= c["altura_piso"] + 1e-3
    assert "/*__DATOS__*/" not in escena.html_escena(d)
