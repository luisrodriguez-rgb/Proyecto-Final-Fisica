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
│   ├── vehiculo.py         Espira de parqueadero, Spark y Kwid, paso del carro, oscilador LC
│   └── escena.py           Datos de la escena 3D y armado de la página
├── assets/
│   ├── escena3d.html       Interfaz de la escena 3D (paneles, botones, estilos)
│   ├── escena3d.js         Escena 3D con Three.js: carros, parqueadero, campo, talanquera
│   └── three/              Three.js r147 guardado en el repositorio (licencia MIT)
├── figuras-anatomy/
│   ├── corte-espira/       Figura del corte del detector (build.mjs, modelo.mjs, campo.mjs, páginas HTML)
│   └── kit/                Kit de Anatomy copiado para reconstruir la figura
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
| `identificacion.py` | `firma`, `curvas_referencia`, `medir`, `identificar`, `residuo_relativo`, `evaluar` |
| `vehiculo.py` | `Espira` (L₀, f₀), `VEHICULOS`, `cobertura`, `delta_Z_vehiculo`, `respuesta`, `curva_altura`, `paso`, `identificar_vehiculo`, `oscilador` |
| `escena.py` | `lineas_de_campo` (Biot–Savart con espira imagen), `escena_datos`, `html_escena` |
| `numerics.py` (sistemas) | `euler_sistema`, `rk4_sistema`: los mismos métodos con estado vectorial, para el oscilador LC |

## 4.2 Ejecutar

Además del simulador, la figura de Anatomy se reconstruye con Node 20.10 o superior:

```bash
cd figuras-anatomy/corte-espira && node build.mjs && node build.mjs --light && node build.mjs --audit
```


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
- **La física queda en Python, la escena 3D solo dibuja.** `sensor/escena.py` calcula las señales de los dos carros,
  la potencia en el chasis y las líneas de campo, y las manda a la página como JSON. El JavaScript solo interpola
  esos números en función de la posición del carro, así que la escena y las gráficas siempre coinciden.
- **Funciona sin internet.** Three.js y la figura de Anatomy van incrustados en la página, sin cargar nada de
  servidores externos, para que la demostración no dependa de la red del salón.
- **Capturas reproducibles.** La escena acepta opciones en la URL (`?x=0&cam=ras&lab=0`) para fijar la posición del
  carro, la cámara y las etiquetas, y así sacar capturas con Chrome sin interfaz.
- **Herramientas de la guía.** NumPy, SciPy, Matplotlib, Plotly, Streamlit y SymPy. VPython no se usó porque
  Plotly y Matplotlib cubren las visualizaciones dentro de la misma app web.

## 4.4 Flujo de datos

```
 Pestaña Caso: vehículo (carro, velocidad, espira, sensibilidad)
        │
        ▼
 vehiculo.py ── L₀ de la espira ── ΔZ del chasis (Dodd–Deeds) × cobertura ──► ΔL/L, Δf, altura estimada
        │                                  │                                      │
        │                                  ▼                                      ▼
        │                       oscilador LC (Euler, RK4)              escena.py ── JSON ──► escena3d.js (Three.js)
        │                                                                  (señal, potencia,      carros, talanquera,
        │                                                                   líneas de campo)      etiquetas, gráfica
        ▼
 Barra lateral (N, a, l, R₀, f, V₀, I₀, material, d, umbral, Δt)
        │
        ▼
 physics.py ── L₀ (Wheeler) ── ΔZ (Dodd–Deeds) ──► L_eff, R_eff, δ, Γ ──► identificacion.py (material y distancia)
        │                                              │
        │                                              ▼
        │                         numerics.py ── Euler, RK4, exacta, SciPy ──► i(t), errores, orden
        ▼                                              │
 campo_bobina ──► mapa de B                  envolvente + comparador ──► salida ON/OFF
        │                                              │
        └──────────────────► app.py + ui.py ◄──────────┘
                                   │
                                   ▼
                     9 pestañas, tema claro u oscuro
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
| `test_identifica_material_y_distancia_sin_ruido` | Cada material se identifica y su distancia se estima en el plano de impedancia |
| `test_impureza_aumenta_el_residuo` | Una pieza con conductividad distinta deja un residuo mayor |
| `test_espira_y_carros` | $L_0$ de la espira en el rango esperado; el chasis baja $L$ y sube $f$; cada carro se reconoce |
| `test_datos_de_la_escena_3d` | Los datos de la escena coinciden con el modelo y las líneas de campo no atraviesan el chasis |
| `test_oscilador_lc_del_detector` | RK4 reproduce la frecuencia y la energía del oscilador, Euler es inestable y Δf sigue la fórmula exacta |

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
