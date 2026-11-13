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
│   ├── symbolic.py         Deducción con SymPy y verificación del residuo
│   ├── identificacion.py   Material y distancia en el plano de impedancia
│   ├── vehiculo.py         Espira de parqueadero, Spark y Kwid
│   └── escena.py           Datos y página de la escena 3D
├── assets/
│   ├── escena3d.html       Escena 3D (Three.js): parqueadero, carros, campo, talanquera
│   └── three/              Three.js r147 guardado en el repositorio (licencia MIT)
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

## 4.4 Flujo de datos

```
 Barra lateral (N, a, l, R₀, f, V₀, I₀, material, d, umbral, Δt)
        │
        ▼
 physics.py ── L₀ (Wheeler) ── ΔZ (Dodd–Deeds) ──► L_eff, R_eff, δ, Γ
        │                                              │
        │                                              ▼
        │                         numerics.py ── Euler, RK4, exacta, SciPy ──► i(t), errores, orden
        │                                              │
        ▼                                              ▼
 campo_bobina ──► mapa de B                  envolvente + comparador ──► salida ON/OFF
        │                                              │
        └──────────────────► app.py + ui.py ◄──────────┘
                                   │
                                   ▼
                     7 pestañas, tema claro u oscuro
```

Cada flecha es una llamada a función con números de entrada y de salida. Ningún módulo de `sensor/` importa
Streamlit, así que la física se puede probar y reutilizar sola.

## 4.5 Pruebas automáticas

| Prueba | Qué garantiza |
|---|---|
| `test_orden_convergencia` | Euler converge con orden 1 y RK4 con orden 4 en alterna |
| `test_orden_convergencia_dc` | Lo mismo en el escalón DC |
| `test_rk4_coincide_con_scipy` | RK4 y SciPy coinciden con la solución exacta |
| `test_escalon_dc_como_circuito_rc` | 63 % de $i_{max}$ en $t=\tau$ y descarga a cero |
| `test_limites_fisicos` | El cobre baja $L$ y sube $R$, el acero sube $L$ a baja frecuencia, el efecto decae con la distancia, $\Gamma\to-1$ en un conductor perfecto |
| `test_campo_espira_centro` | $B = \mu_0 I/2a$ en el centro de una espira |
| `test_balance_de_energia_al_energizar` | Energía entregada = calor + energía magnética |
| `test_campo_lejano_es_dipolo` | Lejos de la bobina el campo es el de un dipolo |

```bash
.venv/bin/python -m pytest -q tests
```

Si un cambio en el código rompe la física, alguna de estas pruebas falla.

## 4.6 Cómo extender el código

**Agregar un material.** Basta con una línea en el diccionario `MATERIALES` de
[`sensor/physics.py`](../sensor/physics.py):

```python
"Níquel": {"sigma": 1.43e7, "mu_r": 100.0, "color": "#64748b"},
```

y su color en las paletas de [`ui.py`](../ui.py). El simulador, las tablas y las figuras lo incluyen solos.

**Resolver otra EDO.** `euler(f, y0, h, n)` y `rk4(f, y0, h, n)` aceptan cualquier función `f(t, y)`. Así se
resolvió el ejercicio RC de clase sin escribir métodos nuevos.

## 4.7 Control de versiones

El proyecto está en GitHub con un historial de commits pequeños: cada commit hace una sola cosa (una función, una
figura, un documento) y su mensaje explica qué cambió y por qué. Así se puede revisar cómo evolucionó el proyecto y
volver atrás cualquier cambio sin afectar los demás.
