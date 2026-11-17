# Guion de la sustentación (15 minutos): resumen

**El guion completo, con todo el texto para decir diapositiva por diapositiva, está en
[`guion.pdf`](guion.pdf)** (fuente: [`guion.tex`](guion.tex)). Trae los tiempos de cada diapositiva, párrafos
opcionales para cuando se va rápido y recuadros en letra pequeña que explican lo complejo. Este archivo es el
resumen de bolsillo: ideas clave, números y preguntas.

Presentación: [`presentacion.pdf`](presentacion.pdf) (25 diapositivas). El profesor escoge quién presenta, así que
**todos** deben poder seguir el guion completo.

| Parte | Tiempo | Diapositivas | Tema |
|---|---|---|---|
| 1 | 0:00 – 2:35 | 1 – 4 | El problema y el esquema D.E.P.A. |
| 2 | 2:35 – 5:30 | 5 – 8 | La física: por qué el carro cambia la espira |
| 3 | 5:30 – 7:25 | 9 – 10 | El modelo: inductancia, chasis y oscilador LC |
| 4 | 7:25 – 10:10 | 11 – 14 | Métodos numéricos: Euler y RK4 |
| 5 | 10:10 – 13:20 | 15 – 19 + demo | Simulación y demostración en vivo |
| 6 | 13:20 – 15:00 | 20 – 25 | Resultados, limitaciones y cierre |

---

## Parte 1 · El problema (0:00 – 2:35)

**Diapositivas 1 a 4:** portada, contenido, introducción y esquema D.E.P.A.

**Imágenes para señalar**
- Portada: el carro llegando a la talanquera (imagen ilustrativa hecha con IA, decirlo).
- Contenido: la escena 3D del simulador con el Spark sobre la espira.
- Introducción: el collage de aplicaciones (semáforos, parqueaderos, fábrica).
- D.E.P.A.: las cuatro cajas en fila.

**Qué decir**
> "Cuando uno llega a un parqueadero, la talanquera se abre sola. Debajo del pavimento hay una espira de alambre que
> detecta el carro. Nuestro proyecto, SEMP, modela ese detector y va un paso más allá: que además reconozca **qué**
> carro llegó. El profesor nos propuso comparar un **Chevrolet Spark** y un **Renault Kwid**."
>
> "Organizamos el proyecto con el esquema D.E.P.A. que vimos en clase. **Detección:** ¿hay carro y cuál es?
> **Emisiones:** cómo responde el chasis al campo. **Propiedades:** frecuencia, energía y potencia. **Alerta:** el
> detector abre la talanquera y dice el modelo. Igual que con el espectrómetro de masas, cada etapa usa solo la
> física que necesita."

**Para recordar**
- La pregunta del proyecto: abrir la talanquera **y** saber si es un Spark o un Kwid, sin cámaras.
- D.E.P.A. = Detección, Emisiones, Propiedades, Alerta.
- Hay un segundo escenario (piezas de una fábrica) que se muestra al final.

**Transición:** "¿Por qué un carro cambia algo en un alambre enterrado? Eso es pura ley de Faraday."

---

## Parte 2 · La física (2:35 – 5:30)

**Diapositivas 5 a 8:** qué pasa físicamente, representación del sistema, caso de estudio, ecuaciones de Maxwell.

**Imágenes para señalar**
- Diapositiva 5: las líneas de campo que suben desde la espira y la placa encima (imagen de IA).
- Diapositiva 6: la **figura de Anatomy** del corte. Señalar la espira de 3 vueltas en la ranura, el cable al detector
  y el chasis a 15 cm (Spark) y 18 cm (Kwid).
- Diapositiva 7: los dos carros y la tabla. Señalar la fila en negrita: **15 cm frente a 18 cm**.

**Qué decir**
> "La espira lleva corriente alterna y crea un campo magnético que sube desde el piso. Cuando el carro se para
> encima, ese campo que cambia induce corrientes en el chasis de acero: es la **ley de Faraday**. Por la **ley de
> Lenz**, esas corrientes de Foucault crean un campo contrario y bloquean parte del flujo. Resultado: la inductancia
> de la espira **baja**."
>
> "Los dos carros son casi del mismo tamaño. La diferencia clave es la **altura del chasis**: 15 cm el Spark y 18 cm
> el Kwid. El más bajo cambia más la espira, y así los distinguimos."
>
> "Como pidió el profesor, usamos solo las ecuaciones de Maxwell necesarias: **Faraday**, que es la central, y
> **Ampère**. Gauss magnética solo entra como condición de frontera."

**Para recordar**
- Cadena: **campo que cambia → Faraday → corrientes de Foucault → Lenz → la inductancia baja**.
- Pregunta trampa: *"Si el acero es magnético, ¿no debería subir la inductancia?"* Respuesta: a 55 kHz el campo entra
  solo **0.087 mm** en el acero (profundidad de penetración). El chasis se comporta como un conductor perfecto y
  **expulsa** el flujo. La magnetización solo gana a frecuencias bajas.
- No se usa corriente de desplazamiento: la longitud de onda a 55 kHz es de 5.4 km, miles de veces la espira.
- Espira: cuadrada de **1.8 m**, **3 vueltas**, enterrada a **5 cm**.

**Transición:** "Ahora pongamos números a esa idea."

---

## Parte 3 · El modelo matemático (5:30 – 7:25)

**Diapositivas 9 y 10:** inductancia y efecto del chasis; oscilador LC.

**Imágenes para señalar**
- Diapositiva 9: la tabla con **−12.9 %** (Spark) y **−11.4 %** (Kwid).
- Diapositiva 10: el recuadro de la fórmula exacta y la tabla con **59.18 kHz** y **58.69 kHz**.

**Qué decir**
> "La espira, sin carro, tiene una inductancia de **83 microhenrios**. El efecto del chasis lo calculamos con la
> solución de Dodd y Deeds para una placa conductora, multiplicada por la fracción de la espira que el carro tapa.
> Con el Spark la inductancia baja un **12.9 %**; con el Kwid, que es más alto, un **11.4 %**."
>
> "¿Cómo lo mide el detector? Conecta la espira a un capacitor y forma un **oscilador LC**. Aplicamos la ley de mallas
> de Kirchhoff **igual que en el circuito RC de clase**, pero ahora hay capacitor y bobina, y sale
> $L\ddot q + R\dot q + q/C = 0$. Es una oscilación que se va apagando, con frecuencia $1/2\pi\sqrt{LC}$:
> **55.25 kHz** sin carro."
>
> "Si la inductancia baja, la frecuencia sube. Con el Spark llega a **59.18 kHz** y con el Kwid a **58.69 kHz**."

**Para recordar**
- $L_0$ = **83 µH**, $f_0$ = **55.25 kHz**, factor de calidad $Q$ = **48**.
- Fórmula exacta: $f/f_0 = (1 + \Delta L/L_0)^{-1/2}$. **No** usar la aproximación $-\tfrac12\Delta L/L$ (eso se
  explica en la parte 4).
- Conexión con clase: el oscilador LC es la unión del **RC de clase** y del **RL** de la espira; la misma ley de
  mallas y la misma convención de signos.
- La inductancia se define como la capacitancia: flujo por amperio en lugar de carga por voltio.

**Transición:** "La ecuación del oscilador la resolvimos también numéricamente, y ahí apareció algo interesante."

---

## Parte 4 · Métodos numéricos (7:25 – 10:10)

**Diapositivas 11 a 14:** Euler y RK4, convergencia, Euler explota, la simulación corrigió la fórmula.

**Imágenes para señalar**
- Diapositiva 12: la gráfica log-log con las pendientes 1 y 4.
- Diapositiva 13: la gráfica de energía. Señalar la **línea roja de Euler subiendo hasta $10^{11}$** y la azul de RK4
  bajando como debe.
- Diapositiva 14: los dos números, **6.44 %** frente a **7.13 %**.

**Qué decir**
> "Programamos Euler y Runge-Kutta 4 a mano. Como el oscilador es de segundo orden, lo escribimos como un sistema
> con la carga y la corriente. La frecuencia la medimos **contando cruces por cero**, como hace un detector real."
>
> "RK4 converge con **orden 4**: si duplicamos los pasos, el error baja **16 veces**. Euler, en cambio, **explota**
> en el oscilador: cada paso multiplica la amplitud por un número mayor que uno, sin importar qué tan pequeño sea
> el paso. Con 40 pasos por período la energía crece cien mil millones de veces."
>
> "Y lo más importante: al principio usamos la fórmula aproximada del cambio de frecuencia, que daba **6.44 %**. La
> simulación con RK4 daba **7.13 %** con cualquier paso. Revisamos y la simulación tenía razón: la aproximación solo
> vale para cambios pequeños, y un carro cambia la inductancia un 13 %. **El método numérico decidió qué fórmula
> usar** y corregimos todo el proyecto."

**Para recordar**
- Euler: orden 1. RK4: orden 4 (medidos 1.01 y 4.02).
- **Por qué Euler explota:** en el oscilador los valores propios son imaginarios y $|1 + j\omega h| > 1$ siempre. En el
  circuito RL sí funcionaba si $\Delta t < 2\tau$.
- RK4 da la frecuencia con error de $5\times10^{-6}$ y reproduce la pérdida exacta de energía ($e^{-Rt/L}$).
- La historia de la fórmula corregida es el mejor ejemplo de **validación**: contarla con calma.

**Transición:** "Todo esto lo metimos en un simulador. Vamos a verlo."

---

## Parte 5 · Simulación y demostración (10:10 – 13:20)

**Diapositivas 15 a 19** y **1.5 minutos de demostración en vivo** (pestaña **Caso: vehículo**).

**Imágenes para señalar**
- Diapositiva 15: el Spark al atardecer (59.18 kHz, pantalla "SPARK", talanquera abierta) y el Kwid de día.
- Diapositiva 16: la curva que baja con la altura, con los dos puntos marcados.
- Diapositiva 17: el **trapecio** de la frecuencia mientras el carro cruza.
- Diapositiva 18: la vista a ras del piso con las líneas de campo bajo el chasis, y la tabla del tamaño de la espira.
- Diapositiva 19: el plano de impedancia del segundo escenario.

**Qué decir**
> "El simulador tiene una escena 3D del parqueadero. Los carros están hechos con sus medidas reales y todas las
> lecturas salen del modelo en Python."

**Demostración en vivo (1.5 min)**
1. Dejar que el **Spark** llegue y se detenga: la frecuencia sube a 59.18 kHz, la pantalla dice SPARK y se abre la
   talanquera.
2. Cambiar a la cámara **"A ras"**: mostrar que las líneas de campo se acuestan bajo el chasis.
3. Cambiar al **Kwid**: la frecuencia sube menos, 58.69 kHz.
4. Si hay tiempo: en el oscilador LC, mostrar que Euler explota y RK4 no.

> "La gráfica resume el proyecto: más bajo el carro, más baja la inductancia y más sube la frecuencia. Invirtiendo
> la curva, el detector estima la altura: **14.9 cm** para el Spark y **18.0 cm** para el Kwid. Los reconoce."
>
> "Cuando el carro cruza, la señal es un trapecio de unos 2 segundos a 10 km/h, y el detector necesita solo 18
> milisegundos para medir. Probando diseños, la mejor espira es **del tamaño del carro** y poco profunda."
>
> "El mismo modelo, con una bobina pequeña, identifica el **material** de piezas en una fábrica: la fase del cambio da
> el metal y la magnitud la distancia, con 100 % de acierto."

**Para recordar**
- Alturas estimadas: **14.9 cm** y **18.0 cm**.
- Diferencia entre los carros: **0.49 kHz**, fácil de medir.
- Espira óptima: **1.5 a 1.8 m**; menos profunda, más señal; las vueltas cambian la frecuencia, no el cambio relativo.
- Si falla el computador: usar las diapositivas 15 a 18, que tienen las capturas de la escena.

**Transición:** "Para cerrar, qué tan bien funciona y qué le falta."

---

## Parte 6 · Resultados y cierre (13:20 – 15:00)

**Diapositivas 20 a 22 y 25:** resultados principales, discusión, conclusiones, gracias.

**Imágenes para señalar**
- Diapositiva 20: la tabla del caso del carro.
- Diapositiva 21: la tabla espira frente a cámara y ultrasonido.

**Qué decir**
> "Los dos carros se detectan y se reconocen. El modelo coincide con cómo funcionan los detectores reales: el chasis
> baja la inductancia y el carro más bajo la baja más."
>
> "Tiene limitaciones, y las decimos: tratamos el chasis como una placa plana, así que el efecto calculado es un
> **máximo**. Un Kwid cargado puede bajar a 16 cm y confundirse con un Spark; una segunda espira que mida el largo
> lo resolvería. Un análisis por elementos finitos daría el valor exacto."

**Frase de cierre**
> "Con las leyes de Faraday y Ampère, la ley de mallas que vimos en clase y RK4 programado a mano, el detector
> reconoce un Spark a 59.18 kHz y un Kwid a 58.69 kHz por la altura de su chasis. Gracias."

**Para recordar**
- Decir las limitaciones **antes** de que pregunten.
- Ventajas de la espira: funciona de noche y con lluvia, no tiene partes expuestas, consume menos de 1 mW.

---

## Números que hay que saber de memoria

| Qué | Valor |
|---|---|
| Espira | 1.8 m, 3 vueltas, 5 cm de profundidad |
| Inductancia sin carro | 83 µH |
| Frecuencia sin carro | 55.25 kHz |
| Altura del Spark / Kwid | 15 cm / 18 cm |
| Cambio de inductancia Spark / Kwid | −12.9 % / −11.4 % |
| Frecuencia con Spark / Kwid | **59.18 kHz / 58.69 kHz** |
| Altura estimada | 14.9 cm / 18.0 cm |
| Profundidad de penetración en el acero a 55 kHz | 0.087 mm |
| Orden de Euler / RK4 | 1 / 4 (medidos 1.01 / 4.02) |
| Aproximación lineal frente a exacta | 6.44 % frente a 7.13 % |
| Campo de la espira | 0.09 µT (500 veces menos que el de la Tierra) |

## Preguntas más probables (respuesta en una frase)

- **¿Qué ley de Maxwell es la clave?** Faraday: el campo que cambia induce las corrientes en el chasis.
- **¿Por qué baja la inductancia si el acero es magnético?** A 55 kHz el campo entra solo 0.087 mm y domina el
  apantallamiento de las corrientes de Foucault.
- **¿Cómo se relaciona con la clase?** El oscilador se resuelve con la ley de mallas como el RC, y la inductancia se
  define como la capacitancia.
- **¿Por qué no usaron Δf/f = −½ ΔL/L?** Porque solo vale para cambios pequeños; la simulación con RK4 mostró que con
  un 13 % de cambio la exacta da 7.13 % y la aproximada 6.44 %.
- **¿Por qué Euler explota?** En un oscilador cada paso de Euler multiplica la amplitud por $\sqrt{1+(\omega h)^2} > 1$.
- **¿Qué pasa si el Kwid va cargado?** Baja a unos 16 cm y se confunde con el Spark; se arregla midiendo también el
  largo con una segunda espira.
- **¿Por qué no una cámara?** La espira no le teme a la lluvia ni a la noche y no tiene partes expuestas; la cámara
  reconoce el modelo exacto pero es más frágil y costosa.
- **¿El campo es peligroso?** No: 0.09 µT, cientos de veces menor que el campo de la Tierra.

Más preguntas y respuestas en [`docs/07-sustentacion.md`](../docs/07-sustentacion.md).

## Antes de empezar

- [ ] Simulador abierto en la pestaña **Caso: vehículo**, con el Spark y la espira de 1.8 m.
- [ ] Probar la escena 3D en el computador de la exposición (necesita WebGL, no necesita internet).
- [ ] PDF de la presentación abierto como respaldo.
- [ ] Cada integrante ensayó el guion completo una vez con cronómetro.
