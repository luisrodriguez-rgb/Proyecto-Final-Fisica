# 8. Uso de inteligencia artificial generativa (IAG)

La guía (sección 6) permite usar IAG en cualquier etapa, siempre que se use de forma crítica, se justifique y
se cite lo que produjo.

## 8.1 Herramientas y alcance

| Herramienta | Para qué se usó |
|---|---|
| Claude (Anthropic), mediante Claude Code | Escribir el código del simulador (`app.py`, `ui.py`, `sensor/`), las pruebas, el script de figuras y los primeros borradores de estos documentos |
| Asistente conversacional (antes de empezar el código) | Proponer la estructura inicial del proyecto y una primera plantilla del simulador |
| Claude Code con la skill Anatomy | La figura isométrica del corte del detector de espira (`figuras-anatomy/`) |
| Whisper (transcripción local) | Transcribir los audios de la orientación del profesor para resumirlos en `docs/enunciado/` |
| ChatGPT o Gemini (Nano Banana) | Las imágenes de apoyo de `docs/figuras/ia/`, generadas con los prompts de `docs/prompts-imagenes.md` |

**Cita sugerida**: Anthropic. (2026). *Claude* (modelo de lenguaje) [Software]. https://claude.ai.
Contenido generado con asistencia de IAG y revisado por el equipo.

## 8.2 Decisiones críticas sobre lo que propuso la IAG

- La primera plantilla modelaba la pieza con coeficientes empíricos $\alpha$ y $\beta$ sin justificación física.
  Se reemplazó por la solución de Dodd–Deeds, que sale de las ecuaciones de Maxwell y se puede defender.
- La plantilla tenía dos criterios de detección distintos (uno para el indicador y otro para la variable
  `detectado`). Se unificó en uno solo: la variación relativa de amplitud.
- Se agregó el escalón DC para conectar el modelo con la deducción del circuito RC vista en clase.
- Para el caso del carro, la IAG propuso dos ubicaciones del sensor (en el piso o en el carro). El equipo eligió la
  espira en el piso porque un sensor inductivo detecta metal y así la diferencia entre los dos carros sale de la física.
- La fórmula de cambio de frecuencia $\Delta f/f \approx -\tfrac12\Delta L/L$ se usó al principio. Al simular el
  oscilador LC con RK4 apareció una diferencia (7.13 % frente a 6.44 %), y se cambió a la fórmula exacta en todo el
  proyecto. Es un ejemplo de verificar con el método numérico lo que propone la IAG.
- Las imágenes generadas con IA muestran carros genéricos, no un Spark ni un Kwid; se usan solo como ilustración y
  los datos reales se escriben aparte.
- Cada resultado numérico de los documentos se comprobó ejecutando el código, y los comportamientos físicos
  esperados se fijaron como pruebas automáticas.

## 8.3 Pendiente para el equipo

La guía pide justificar el uso de la IAG para alcanzar los resultados de aprendizaje. El equipo debe completar
esta sección con su propia reflexión: qué entendió revisando el código y las deducciones, qué verificó a mano
(por ejemplo, la separación de variables de la sección 2.3.1, la frecuencia del oscilador LC de la sección 2.10.3 y
el análisis dimensional) y qué haría distinto.
