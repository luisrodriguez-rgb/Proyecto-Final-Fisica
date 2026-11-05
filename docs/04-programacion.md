# 4. Programación

> Criterio de la rúbrica: **Programación (10 %)**, código organizado y funcional.

## 4.1 Estructura

```
.
├── app.py                  Interfaz Streamlit: parámetros, pestañas y gráficas
├── ui.py                   Tema claro/oscuro, plantilla de gráficas, componentes visuales
├── sensor/
│   ├── physics.py          Modelo físico: L₀, Dodd–Deeds (ΔZ), δ, campo B (Biot–Savart)
│   ├── numerics.py         Euler y RK4 a mano, soluciones exactas, convergencia, L(t) variable
│   └── symbolic.py         Deducción con SymPy y verificación del residuo
├── scripts/
│   └── generar_figuras.py  Figuras del informe en docs/figuras
├── tests/
│   └── test_modelo.py      Pruebas automáticas (pytest)
└── docs/                   Informe organizado según la rúbrica
```

La física, los métodos numéricos y la interfaz están en módulos separados. Por eso las funciones de
`sensor/` se pueden usar sin Streamlit: las pruebas y el script de figuras las importan directamente.

| Módulo | Funciones principales |
|---|---|
| `physics.py` | `Bobina` (L₀ de Wheeler e ideal), `delta_Z`, `parametros_efectivos`, `profundidad_penetracion`, `amplitud_regimen`, `campo_espira`, `campo_bobina` |
| `numerics.py` | `euler`, `rk4`, `solucion_analitica`, `solucion_escalon`, `resolver_rl`, `estudio_convergencia`, `simular_paso`, `envolvente`, `comparador_histeresis` |
| `symbolic.py` | `derivar`: EDO, `dsolve`, régimen permanente, Z, φ, τ, energía, potencia, sensibilidades |

## 4.2 Ejecutar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

Pruebas y figuras:

```bash
.venv/bin/python -m pytest -q tests
.venv/bin/python scripts/generar_figuras.py
```

## 4.3 Decisiones de implementación

- **Euler y RK4 genéricos.** Reciben cualquier `f(t, y)`, así que los mismos métodos resuelven el escalón, la
  alterna y la inductancia variable.
- **Integral de Dodd–Deeds vectorizada.** Se evalúa a la vez para 260 distancias con NumPy, sin bucles en
  Python. Las curvas completas se calculan en milisegundos.
- **Caché.** `st.cache_data` guarda las curvas frente a la distancia y la frecuencia y la deducción de SymPy,
  que solo se recalculan cuando cambia un parámetro del que dependen.
- **Pruebas automáticas.** Verifican los órdenes de convergencia (1 y 4), la coincidencia de RK4 con la
  solución exacta, el 63 % en $t=\tau$, los límites físicos del modelo de la pieza y el campo de una espira.
- **Herramientas de la guía.** NumPy, SciPy, Matplotlib, Plotly, Streamlit y SymPy. VPython no se usó porque
  Plotly y Matplotlib cubren las visualizaciones dentro de la misma app web.
