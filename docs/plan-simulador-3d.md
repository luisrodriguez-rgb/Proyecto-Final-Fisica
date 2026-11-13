# Plan: simulador 3D del caso del carro

> **Estado:** la escena 3D está hecha (`assets/escena3d.html`, `assets/escena3d.js`, `sensor/escena.py`) y se ve
> en la pestaña **Caso: vehículo**, con carros detallados, cielo, asfalto mojado y luces. La figura de Anatomy está
> en `figuras-anatomy/corte-espira/` y sus capturas en `docs/figuras/anatomy-corte-espira*.png`. Se probó el
> postproceso de brillo (bloom) de Three.js r147, pero producía franjas en el pavimento y se quitó; el brillo de la
> espira se simula con un halo.

## Objetivo

Que el simulador se vea como un sistema real y no solo como gráficas. El profesor pidió probar dos carros (un
Chevrolet Spark GT y un Renault Kwid), y la referencia visual es el simulador de otro equipo, que muestra todo el
sistema en 3D con etiquetas de potencia en cada parte.

La escena: **la entrada de un parqueadero**. Un carro avanza por el pavimento, pasa sobre la espira enterrada, el
detector cambia de frecuencia, la talanquera se levanta y una pantalla muestra qué carro llegó.

## Opciones evaluadas

| Opción | Qué es | A favor | En contra |
|---|---|---|---|
| **A. Escena 3D en vivo dentro de Streamlit** (elegida) | Un componente HTML con Three.js dentro de la app; la física sigue en Python | Interactivo de verdad (girar la cámara, cambiar de carro, reproducir el paso). Conserva Python, como pide la guía. Los números salen del mismo modelo | Streamlit solo manda datos hacia la escena: se precalculan en Python y se envían como JSON |
| B. App web aparte (React + Three.js) | Reescribir la interfaz y portar la física a JavaScript | Lo más fluido | Duplica la física en dos lenguajes; se aleja de la guía, que recomienda Python y Streamlit |
| C. Solo Anatomy | Figura isométrica ilustrada (SVG, WebGL opcional) | Acabado de ilustración técnica | Es lenta a propósito: un carro entero es su nivel más largo (6 h o más). No se actualiza con los controles de la app sin programar un puente. "No es una librería de gráficas" |
| **D. Anatomy para figuras** (elegida, junto con A) | Figuras ilustradas para el informe y las diapositivas | Muy buen acabado para lo impreso, donde no hace falta interactividad | Una figura mediana tarda alrededor de una hora |

**Decisión: A + D.** Escena 3D en vivo para el simulador y la demostración, y Anatomy para las figuras del
documento impreso y de la presentación.

## A. Escena 3D en vivo

### Arquitectura

```
 sensor/vehiculo.py ──► escena_datos(carro, espira, velocidad)  ──►  JSON
   (física en Python)     · posición del carro x(t)                    │
                          · ΔL/L(t), f(t), potencia en el chasis       ▼
                          · líneas de campo (Biot–Savart)     components.html(escena.html + JSON)
                          · corrientes de Foucault (intensidad)        │
                                                                       ▼
                                                    Three.js: anima, dibuja y muestra lecturas
```

- Los datos de **los dos carros** se mandan a la vez, así que cambiar de carro dentro de la escena es instantáneo,
  sin recargar la app.
- **Three.js se guarda en el repositorio**, no se carga de internet, para que la demostración funcione aunque el
  salón no tenga conexión.
- Si el computador no tiene WebGL, la pestaña sigue mostrando las gráficas 2D actuales.

### Qué se ve

| Elemento | Detalle |
|---|---|
| Pavimento y espira | Asfalto con la ranura de la espira; el cable brilla con la corriente alterna |
| Carro | Modelo 3D construido con las **medidas reales** (largo, ancho, alto, altura al piso, distancia entre ejes) de cada carro, con ruedas que giran. Colores distintos y sin logos de marca |
| Campo magnético | Líneas calculadas en Python con Biot–Savart, con pulsos que viajan por ellas; se aplastan contra el chasis cuando el carro está encima |
| Corrientes de Foucault | Anillos que brillan en la cara inferior del chasis, con intensidad proporcional a la cobertura |
| Detector | Caja en un poste con pantalla: $L$, $f$, $\Delta f$ y el modelo reconocido |
| Talanquera | Se levanta cuando la señal supera el umbral |
| Etiquetas | Al estilo de la referencia: "Espira: 83 µH", "Chasis absorbe X mW", "Oscilador: 55.2 → 58.8 kHz" |
| Gráfica en vivo | Mini gráfica de $-\Delta L/L$ que avanza con el carro |

### Controles

- Carro: Spark o Kwid.
- Reproducir, pausar y velocidad del carro.
- Cámaras: vista general, a ras del piso (para ver el chasis y la espira) y desde arriba.
- Mostrar u ocultar etiquetas, campo y corrientes.
- Arrastrar para girar la cámara y la rueda para acercar.

### Pasos

1. Función `escena_datos` en Python y su prueba (los datos de la escena coinciden con `vehiculo.paso`).
2. Escena base: pavimento, espira, cámara, luces y los dos carros con sus medidas.
3. Animación del paso, lecturas del detector y talanquera.
4. Campo magnético y corrientes de Foucault.
5. Integración en la pestaña **Caso: vehículo**, tema claro y oscuro.
6. Verificación en el navegador: capturas en los dos temas, los dos carros y las tres cámaras.

## D. Figuras con Anatomy

Instalación (requiere Node 20.10 o superior; aquí hay Node 24):

```bash
npx skills add wheresryan22/anatomy -g -a claude-code
```

Figuras propuestas, de tamaño mediano (40 a 80 piezas, alrededor de una hora cada una):

1. **Corte del detector de espira:** sección del pavimento con la ranura, las vueltas del cable, el sellante, el
   cable de conexión, el detector con su oscilador y, encima, el chasis del carro con las corrientes de Foucault.
   Es la figura central del informe.
2. **Sensor inductivo industrial abierto** (segundo escenario): carcasa, núcleo de ferrita, bobina y tarjeta del
   oscilador, frente a una pieza metálica.

No se propone dibujar el carro completo con Anatomy: es su nivel más largo (6 h o más) y en la escena 3D ya
aparece.

## Otras herramientas disponibles para la parte visual

| Herramienta | Uso posible |
|---|---|
| `baoyu-image-gen` | Imágenes generadas con IA para la portada o el fondo de las diapositivas (sin logos de marca) |
| `baoyu-slide-deck`, `pptx` | Diapositivas de la sustentación |
| `remotion` | Un video corto del carro pasando sobre la espira, por si falla la demostración en vivo |
| `baoyu-diagram` | Diagramas del esquema D.E.P.A. |

## Riesgos

| Riesgo | Cómo se maneja |
|---|---|
| El salón no tiene internet | Three.js guardado en el repositorio |
| El computador de la sustentación es lento | La escena tiene pocos objetos y las líneas de campo se precalculan |
| Streamlit recarga la escena con cada control | Los dos carros van precargados; la escena guarda su propio estado |
| Usar marcas reales | Solo nombres y medidas públicas de fichas técnicas; sin logos |
