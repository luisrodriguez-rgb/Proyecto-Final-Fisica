# Informe del proyecto, organizado por la rúbrica

Proyecto: **SEMP, diseño y simulación de sensores electromagnéticos de proximidad**.
El enunciado, la guía con la rúbrica y la [orientación del profesor](enunciado/orientacion-profesor.md) están en
[`enunciado/`](enunciado/).

**Empieza por [00 · Modelo teórico y formalismo (D.E.P.A.)](00-modelo-teorico-depa.md)**: es el esqueleto que pidió
el profesor (insumos, detección, emisiones, propiedades, alerta y solución) y remite a los demás documentos.

## Índice por criterio

| Criterio | Peso | Documento | Código | Pestaña del simulador |
|---|---|---|---|---|
| Esqueleto del proyecto (orientación del profesor) | – | [00 · Modelo teórico D.E.P.A.](00-modelo-teorico-depa.md) | `sensor/identificacion.py` | Identificación |
| Fundamentación física | 15 % | [01 · Fundamentación física](01-fundamentacion-fisica.md) | `sensor/physics.py` | Modelo, Campo |
| Modelamiento analítico | 20 % | [02 · Modelamiento analítico](02-modelamiento-analitico.md) | `sensor/symbolic.py`, `sensor/physics.py` | Derivación, Modelo |
| Métodos numéricos | 20 % | [03 · Métodos numéricos](03-metodos-numericos.md) | `sensor/numerics.py`, `tests/` | Respuesta temporal, Validación |
| Programación | 10 % | [04 · Programación](04-programacion.md) | todo el repositorio | – |
| Simulación | 15 % | [05 · Simulación](05-simulacion.md) | `app.py`, `ui.py` | todas |
| Validación e impacto | 10 % | [06 · Validación e impacto](06-validacion-e-impacto.md) | `scripts/generar_figuras.py` | Análisis |
| Sustentación | 10 % | [07 · Sustentación](07-sustentacion.md) | – | demostración en vivo |
| Uso de IAG (sección 6 de la guía) | – | [08 · Uso de IAG](08-uso-de-iag.md) | – | – |

## Relación con la estructura de entrega de la guía (sección 4)

| Entrega | Dónde está |
|---|---|
| 4.1 Modelamiento matemático: planteamiento, ecuaciones, hipótesis, solución analítica, análisis dimensional | Documentos 01 y 02 |
| 4.2 Implementación numérica: Euler y RK4, comparación y análisis de errores | Documento 03 y `sensor/numerics.py` |
| 4.3 Simulador computacional | `app.py` y documento 05 |
| 4.4 Resultados: gráficas, tablas, eficiencia, validación física e impacto | Documento 06 y [`figuras/`](figuras/) |

## Relación con los temas de clase

| Tema de clase | Cómo se usa en el proyecto |
|---|---|
| Circuito RC: Kirchhoff, convención de signos, separación de variables, τ y 63 % | Misma deducción para la bobina (2.3.1 – 2.3.3) y modo **Escalón DC** del simulador |
| Ley de Gauss: flujo $\Phi = \vec E\cdot\vec A$ | Flujo magnético $\Phi_B = \vec B\cdot\vec A$ para deducir $L$ (2.2) y Gauss magnética en las condiciones de frontera (1.5) |
| Capacitancia $C = Q/\Delta V$ y campos en la materia | Inductancia $L = \Lambda/i$ y respuesta de conductores y ferromagnéticos (1.1, 2.4) |
| Pantallas táctiles capacitivas: detección por $\Delta C$ | Detección por $\Delta L$ (1.1, 7.2) |
| Interacción eléctrica: $\vec E = -\nabla V$ | Potencial vector $\vec B = \nabla\times\vec A$ (1.3, 1.4) |

## Referencias

- C. V. Dodd y W. E. Deeds, "Analytical solutions to eddy-current probe-coil problems", *Journal of Applied
  Physics* 39, 2829 (1968).
- H. A. Wheeler, "Simple inductance formulas for radio coils", *Proceedings of the IRE* 16, 1398 (1928).
- D. J. Griffiths, *Introduction to Electrodynamics*, 4.ª ed., cap. 7 (ley de Faraday e inductancia).
- Apuntes de clase: *Análisis del circuito RC*, *Ley de Gauss*, *Campos eléctricos en la materia*,
  *Pantallas táctiles capacitivas* e *Interacción eléctrica*.
- Guía de proyectos y propuesta del curso, en [`enunciado/`](enunciado/).

## Regenerar las figuras

```bash
.venv/bin/python scripts/generar_figuras.py
```
