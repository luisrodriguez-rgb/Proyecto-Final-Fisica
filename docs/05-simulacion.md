# 5. Simulación computacional

> Criterio de la rúbrica: **Simulación (15 %)**, interactividad y representación del sistema.

## 5.1 Parámetros modificables (barra lateral)

| Grupo | Parámetro | Rango |
|---|---|---|
| Bobina | Número de espiras $N$ | 10 – 500 |
| | Radio $a$, longitud $l$ | 5 – 50 mm, 5 – 100 mm |
| | Resistencia del devanado $R_0$ | 0.5 – 100 Ω |
| Fuente | Alimentación | alterna $V_0\sin\omega t$ o escalón DC |
| | Frecuencia $f$ | 100 Hz – 50 kHz |
| | Amplitud $V_0$, corriente inicial $I(0)$ | 1 – 24 V, −2 – 2 A |
| Objeto | Material | aire, cobre, aluminio, latón, acero inoxidable 304, acero al carbono |
| | Distancia $d$ | 0.5 – 40 mm |
| | Umbral de activación, histéresis | 0.2 – 20 %, 0 – 30 % |
| Numérico | Pasos por ciclo, duración (alterna) | 8 – 400, 1 – 20 ciclos |
| | Pasos por τ, duración (escalón DC) | 2 – 200, 2 – 20 τ |

El selector de la parte superior cambia entre tema claro y oscuro.

## 5.2 Pestañas

| Pestaña | Qué muestra |
|---|---|
| **Modelo** | $\Delta L/L_0$ y $\Delta R$ frente a la distancia para todos los materiales, curva de detección con el umbral y la distancia de conmutación $S_n$, efecto de la frecuencia, ecuaciones del modelo |
| **Respuesta temporal** | $i(t)$ exacta, RK4, Euler y SciPy. En alterna, la zona muerta del umbral; en DC, $i_{max}$, el 63 % en $t=\tau$ y el cambio del interruptor. Energía y potencia |
| **Paso del objeto** | La pieza se acerca y se aleja: $d(t)$, $L(t)$, $i(t)$, envolvente demodulada, umbrales ON/OFF con histéresis y salida digital del sensor |
| **Campo** | Líneas de $\vec B$ y mapa de $\lvert\vec B\rvert$ con la pieza y $\delta$; perfil $B_z$ sobre el eje con y sin pieza |
| **Validación** | Error frente a $\Delta t$ en log-log con pendientes 1 y 4, orden observado, límites de estabilidad, tabla descargable en CSV, error en el tiempo |
| **Derivación** | Deducción simbólica con SymPy y sensibilidades evaluadas con los parámetros actuales |
| **Análisis** | Interpretación física del caso, comparación de materiales, rendimiento en una línea de producción y limitaciones frente a FEM |

## 5.3 Cumplimiento de las características mínimas de la guía (3.1)

| Característica mínima | Dónde está |
|---|---|
| Parámetros físicos modificables | Barra lateral: bobina, fuente y objeto |
| Condiciones iniciales | $I(0)$ en la barra lateral |
| Visualización de las variables electromagnéticas | $L_{\text{eff}}$, $R_{\text{eff}}$, $\lvert Z\rvert$, $\varphi$, $\delta$, $\Gamma$ en la cabecera y en Modelo |
| Representación de campos | Pestaña Campo: líneas de $\vec B$, $\lvert\vec B\rvert$ y $B_z(z)$ |
| Gráficas temporales | Respuesta temporal y Paso del objeto |
| Comparación de escenarios | Cinco materiales superpuestos, con y sin pieza, AC frente a DC, Euler frente a RK4 |
| Cálculo de energía, potencia o eficiencia | Energía $\tfrac12LI^2$, potencia total y disipada en la pieza, piezas por minuto |
| Interpretación de resultados | Texto generado según el caso en la pestaña Análisis |
| Señal de salida y umbral (propuesta) | Indicador de estado en la cabecera, curva de detección y salida digital |

## 5.4 Guion para mostrarlo en vivo

1. Con cobre a 5 mm, mostrar el indicador **Detectado** y $\Delta L = -8.45$ %.
2. Alejar la pieza con el control de distancia hasta que el indicador pase a **Sin detección**, cerca de
   $S_n = 6.1$ mm.
3. Cambiar a acero al carbono: $\Delta L$ se vuelve positiva. Subir la frecuencia a 50 kHz y ver que vuelve
   a ser negativa.
4. **Paso del objeto**: la salida se activa y se desactiva en distancias distintas por la histéresis.
5. **Validación**: bajar los pasos por ciclo y ver cómo crece el error de Euler. Mostrar las pendientes 1 y 4.
6. Cambiar a **Escalón DC** y relacionarlo con el circuito RC de clase (63 % en $t = \tau$).
