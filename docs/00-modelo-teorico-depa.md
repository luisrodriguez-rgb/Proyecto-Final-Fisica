# 0. Modelo teórico y formalismo matemático (esquema D.E.P.A.)

> Este documento sigue el esqueleto que propuso el profesor para el proyecto **SEMP** (Sensores
> ElectroMagnéticos de Proximidad); ver [orientación del profesor](enunciado/orientacion-profesor.md).
> Primero se describe el proceso por etapas y después se muestra qué matemática necesita cada etapa. El detalle
> de cada parte está en los documentos 01 a 06.

Igual que en el espectrómetro de masas visto en clase, donde cada parte del aparato (acelerador, campo,
deflexión) pide su propia física, aquí cada etapa del sensor pide solo la matemática que necesita.

```
 Insumos ──► [ D · Detección ─► E · Emisiones ─► P · Propiedades ─► A · Alerta ] ──► Solución
 (contexto de inicio)                                                             (contexto de impacto)
                         └───────────── caso específico de estudio ─────────────┘
                                                   ▼
                                               Simulador
```

---

# Parte 1. Modelo teórico

## 0.1 Insumos: contextos de aplicación

| Contexto | Qué se detecta | Qué importa |
|---|---|---|
| Líneas de producción | Presencia y posición de piezas metálicas | Rapidez, distancia fija |
| Clasificación de chatarra y reciclaje | Tipo de metal (ferroso o no ferroso) | Identificación del material |
| Control de calidad | Piezas con aleación equivocada, impurezas o grietas | Sensibilidad a la conductividad |
| Parqueaderos y semáforos | Vehículos sobre una espira enterrada | Distancia y tamaño |
| Velocidad de engranajes | Paso de cada diente | Frecuencia de conmutación |
| Validadores de monedas | Aleación y tamaño de la moneda | Identificación |

**Contexto de inicio elegido: el carro.** El profesor propuso trabajar con un vehículo y comparar dos modelos,
un **Chevrolet Spark GT** y un **Renault Kwid**. Como un sensor inductivo detecta metal, el caso físicamente
coherente es una **espira inductiva en el piso** de la entrada de un parqueadero (o de un semáforo), que detecta el
chasis de acero del carro, reconoce cuál de los dos es y abre la talanquera.

Se conserva un **segundo escenario**, la línea de autopartes con piezas de distintos metales (el primer ejemplo
del profesor), para mostrar la identificación del **material**. El carro muestra la identificación por
**distancia** (altura al piso). Entre los dos se cubren las dos tareas de la detección.

## 0.2 Caso específico de estudio

### Caso principal: espira de parqueadero y dos carros

Una espira cuadrada de 1.8 m de lado (6 × 6 pies, la medida más común), con 3 vueltas de alambre 14 AWG, va
enterrada 5 cm en el pavimento. Forma parte de un oscilador LC. Un carro se detiene encima.

| Dato | Chevrolet Spark GT | Renault Kwid |
|---|---|---|
| Largo × ancho | 3.635 × 1.597 m | 3.680 × 1.586 m |
| Alto | 1.522 m | 1.474 m |
| Distancia entre ejes | 2.375 m | 2.423 m |
| Peso en vacío | 966 kg | 785 kg |
| **Altura libre al piso** | **15 cm** (fuentes: 15 – 17 cm) | **18 cm** (fuentes: 17.2 – 18.5 cm) |

Las fichas técnicas no coinciden del todo; se usa el valor central y se reporta el rango (ver fuentes al final).

**Requisitos del sistema (contexto de impacto):**

1. Detectar que hay un carro sobre la espira.
2. Reconocer si es un Spark o un Kwid.
3. Abrir la talanquera y registrar el modelo.
4. Funcionar a la velocidad de entrada a un parqueadero (5 – 20 km/h).

**Resultado del modelo** (oscilador a 55 kHz):

| | Spark | Kwid |
|---|---|---|
| Distancia chasis–espira | 20 cm | 23 cm |
| Fracción de la espira tapada | 89 % | 88 % |
| $\Delta L/L_0$ | −12.9 % | −11.4 % |
| Cambio de frecuencia del oscilador | +3.9 kHz (59.2 kHz) | +3.4 kHz (58.7 kHz) |
| Altura estimada desde la señal | 14.9 cm ✓ | 18.0 cm ✓ |

El Spark, más bajo, cambia más la inductancia. Esa diferencia permite reconocerlo. Simulador: pestaña
**Caso: vehículo**, con la escena 3D del parqueadero, el oscilador LC resuelto con Euler y RK4 y la figura del
corte hecha con Anatomy. Código: [`sensor/vehiculo.py`](../sensor/vehiculo.py).

### Segundo escenario: línea de autopartes

Una banda transportadora lleva piezas mezcladas bajo un sensor fijo:

| Pieza | Material | Por qué es un buen caso |
|---|---|---|
| Tornillos | Acero al carbono | Ferromagnético: aumenta la inductancia |
| Cables | Cobre | Mejor conductor: el mayor apantallamiento |
| Carcasas | Aluminio | Conductividad parecida al cobre: difícil de separar |
| Conectores | Latón | Conductividad intermedia |
| Abrazaderas | Acero inoxidable 304 | No magnético y mal conductor: señal débil |

**Requisitos del sensor (contexto de impacto):**

1. Avisar cuando una pieza pasa a menos de unos 8 mm.
2. Identificar el material de la pieza.
3. Estimar la distancia de la pieza.
4. Avisar cuando la pieza no se parece a ningún material conocido (aleación equivocada o impurezas).
5. Hacerlo lo bastante rápido para la velocidad de la banda.

Sensor de referencia: bobina de 150 espiras, radio 15 mm, longitud 20 mm, $R_0 = 5\ \Omega$, alimentada con
5 V a 1 kHz (y a 5 kHz para la segunda medición).

## 0.3 Descripción del proceso, etapa por etapa

| Etapa | Qué pasa físicamente (carro sobre la espira) |
|---|---|
| **D · Detección** | La espira crea un campo magnético que sube desde el pavimento. Cuando el carro se detiene encima, el sistema debe decidir si hay un carro y cuál de los dos es; la distancia que importa es la altura del chasis. |
| **E · Emisiones** | El chasis de acero responde: en su cara inferior se inducen corrientes de Foucault que crean un campo opuesto (Lenz). Parte del flujo de la espira queda bloqueado y su inductancia baja. |
| **P · Propiedades** | A la **frecuencia** del oscilador (55 kHz) el campo entra apenas 0.09 mm en el acero, así que domina el apantallamiento y la magnetización casi no cuenta. La **potencia** que absorbe el chasis y el cambio de **energía** guardada en la espira dependen de la altura del chasis. |
| **A · Alerta** | Al bajar $L$, la frecuencia del oscilador $f = 1/2\pi\sqrt{LC}$ sube. Si el cambio supera el umbral, se abre la talanquera; la magnitud del cambio da la altura y, con ella, el modelo del carro. |

En el segundo escenario (autopartes) el proceso es el mismo con una bobina pequeña y piezas a milímetros: la
**fase** del cambio identifica el material y la **magnitud** la distancia (secciones 0.4 y 0.5).

---

# Parte 2. Formalismo matemático por etapa

## 0.4 D · Detección: propiedades de los materiales y de la radiación

### En el carro

- **Qué se detecta:** si hay un carro sobre la espira y cuál es.
- **Propiedad del material:** el chasis es de acero ($\sigma = 6\times10^6$ S/m, $\mu_r \approx 100$). Es igual en los
  dos carros, así que **el material no los distingue**.
- **Distancia:** lo que sí cambia es la altura del chasis sobre la espira, $d = h_{piso} + p$, con $p = 5$ cm de
  profundidad de la espira: 20 cm el Spark y 23 cm el Kwid.
- **Propiedad de la radiación:** a la frecuencia del oscilador, 55.2 kHz, la profundidad de penetración en el acero
  es $\delta = 0.087$ mm. Como $\delta$ es mucho menor que el espesor de la lámina, el chasis se comporta casi como
  un conductor perfecto: **la inductancia baja**. Es el caso $\Gamma \to -1$ del método de las imágenes.
- **La distancia se lee en la intensidad:** el cambio de inductancia cae con la altura, a razón de unos 0.5 puntos de
  $\Delta L/L$ por centímetro entre 15 y 18 cm.

### En la línea de autopartes (segundo escenario)

La detección necesita dos grupos de propiedades.

**Propiedades de los materiales:** conductividad $\sigma$ y permeabilidad relativa $\mu_r$.

| Material | $\sigma$ (S/m) | $\mu_r$ |
|---|---|---|
| Cobre | $5.96\times10^{7}$ | 1 |
| Aluminio | $3.77\times10^{7}$ | 1 |
| Latón | $1.5\times10^{7}$ | 1 |
| Acero inoxidable 304 | $1.45\times10^{6}$ | 1.02 |
| Acero al carbono | $6.0\times10^{6}$ | 100 |

**Propiedades de la radiación:** frecuencia $f$ y potencia. Las dos se combinan con las del material en la
profundidad de penetración,

$$\delta = \sqrt{\frac{2}{\omega\mu_0\mu_r\sigma}},$$

que dice hasta dónde entra el campo en la pieza.

### Con la frecuencia se identifica

La pieza cambia la impedancia de la bobina en $\Delta Z = \Delta R + j\omega\Delta L$. La **dirección** de ese
cambio, su fase $\arg\Delta Z$, depende sobre todo del material y de la frecuencia, y poco de la distancia:

| Material (1 kHz) | Fase de $\Delta Z$ a 2 mm | a 5 mm | a 12 mm |
|---|---|---|---|
| Cobre | −79.7° | −81.0° | −83.1° |
| Aluminio | −77.2° | −78.8° | −81.4° |
| Latón | −70.8° | −73.0° | −76.8° |
| Acero inoxidable 304 | −44.7° | −48.5° | −55.8° |
| Acero al carbono | +66.5° | +62.8° | +53.7° |

- Los conductores no magnéticos tienen fase negativa: $\Delta L < 0$ (apantallamiento).
- El acero al carbono tiene fase positiva: $\Delta L > 0$ (magnetización).
- Entre los no ferrosos, cuanto mejor conduce el metal, más cerca de −90° queda la fase.

Al cambiar la frecuencia cambia $\delta$ y las fases se mueven de forma distinta en cada material. Por eso medir
con **dos frecuencias** separa mejor los materiales.

### Con la potencia se establecen distancias

La **magnitud** del cambio, y con ella la potencia que absorbe la pieza, cae rápidamente con la distancia, porque
el campo de la bobina es el de un dipolo ($B\propto 1/z^3$, sección 1.10):

| Distancia (cobre, 1 kHz) | $\lvert\Delta Z\rvert/\omega L_0$ | Potencia absorbida por la pieza $\tfrac12\Delta R\,I_p^2$ |
|---|---|---|
| 2 mm | 0.140 | 32.3 mW |
| 5 mm | 0.086 | 16.9 mW |
| 8 mm | 0.056 | 9.6 mW |
| 12 mm | 0.034 | 5.0 mW |

Una vez identificado el material, la magnitud medida se convierte en distancia con esta curva.

Detalle: [01 · Fundamentación física](01-fundamentacion-fisica.md) y
[02 · Modelamiento analítico](02-modelamiento-analitico.md#24-efecto-de-la-pieza-metálica).

## 0.5 E · Emisiones: cómo se detectan, se miden y se cuantifican

### En el carro

La "emisión" del chasis es el campo de las corrientes de Foucault que se inducen en su cara inferior. Se mide
de forma indirecta: ese campo reduce el flujo que enlaza la espira, la inductancia baja y el oscilador cambia de
frecuencia. La cantidad que se mide es entonces una **frecuencia**, que un microcontrolador cuenta con mucha
precisión.

- **Cuánta energía absorbe el chasis:** con 50 mA en la espira, el Spark absorbe 80 µW y el Kwid 67 µW, que se
  vuelven calor en la lámina.
- **Cómo se cuantifica:** se cuentan los cruces por cero de la señal del oscilador durante un tiempo fijo y se
  comparan con la frecuencia sin carro. El simulador hace exactamente eso con la solución de RK4.

### En la línea de autopartes (segundo escenario)

**Qué se mide.** El sensor no ve directamente las corrientes de Foucault: ve su efecto en la corriente de la
bobina. Se miden dos números, la **amplitud** $I_p$ y el **desfase** $\varphi$ de la corriente respecto al
voltaje. Con ellos se reconstruye la impedancia y el cambio que produjo la pieza:

$$Z = \frac{V_0}{I_p}e^{j\varphi},\qquad \Delta Z = Z - Z_0,\qquad z = \frac{\Delta Z}{\omega L_0}.$$

**Método de análisis: el plano de impedancia.** Cada material dibuja una curva $z(d)$ al variar la distancia (es
el método de los equipos industriales de ensayo por corrientes de Foucault). La medición se asigna a la curva
más cercana:

$$\text{material} = \arg\min_m\ \min_d \left\lVert z_{med} - z_m(d)\right\rVert,$$

y el punto de la curva donde se alcanza ese mínimo da la distancia estimada.

**Cómo se sabe que hay una impureza.** Si la pieza no se parece a ningún material del catálogo, la distancia a la
curva más cercana (el **residuo**) es grande. Una pieza de cobre con un 20 % menos de conductividad deja un residuo
de 1.5 – 1.8 % de su firma, contra 0.3 % de una pieza pura. Hay un límite físico: el sensor solo ve $\sigma$ y
$\mu_r$, así que un cobre con el 60 % de su conductividad tiene casi la conductividad del aluminio y se identifica
como aluminio.

**Cuántas piezas y de qué material.** Cada medición entrega un material y una distancia. Contando las alertas a lo
largo de la banda se sabe cuántas piezas de cada material pasaron.

Implementación: [`sensor/identificacion.py`](../sensor/identificacion.py). Pestaña **Identificación** del simulador.

## 0.6 P · Propiedades de las ondas EM: solo las ecuaciones de Maxwell necesarias

Siguiendo la indicación del profesor, se discuten solo las ecuaciones que el sensor necesita:

| Ecuación | ¿Se usa? | Para qué |
|---|---|---|
| **Faraday**, $\oint\vec E\cdot d\vec l = -\dfrac{d\Phi_B}{dt}$ | **Sí, es la central** | Induce las corrientes de Foucault en la pieza y la fem $-L\,di/dt$ en la bobina |
| **Ampère** sin corriente de desplazamiento, $\oint\vec B\cdot d\vec l = \mu_0 I_{enc}$ | **Sí** | Campo de la bobina y campo de reacción de la pieza |
| Gauss magnética, $\oint\vec B\cdot d\vec A = 0$ | Solo como condición de frontera | Continuidad de $B_z$ en la superficie de la pieza |
| Gauss eléctrica | No | No hay acumulación de carga: las corrientes de Foucault son lazos cerrados |
| Corriente de desplazamiento | No | Es $10^{18}$ veces menor que la de conducción en el metal |

**Sobre las "ondas".** A 1 kHz la longitud de onda es de 300 km y la bobina mide 3 cm: el sensor trabaja en el
**campo cercano**, donde el campo sigue a la corriente sin propagarse como onda. Las propiedades que importan son
las mismas que en una onda:

| Propiedad | Expresión | Papel en el sensor |
|---|---|---|
| Frecuencia | $\omega = 2\pi f$, $\delta = \sqrt{2/\omega\mu\sigma}$ | Identifica el material |
| Energía | $E = \tfrac12 L I_p^2$, densidad $u_B = B^2/2\mu_0$ | 183 µJ en la bobina; la pieza la modifica al cambiar $L$ |
| Potencia | $P = \tfrac12 R I_p^2$; en la pieza $\tfrac12\Delta R\,I_p^2$ | Indica la distancia; es el 1 % de la potencia total |

Detalle: [01 · Fundamentación física](01-fundamentacion-fisica.md#14-ecuaciones-de-maxwell-utilizadas).

## 0.7 A · Alerta: sistema de detección

**En el carro.** El detector de espira es un oscilador LC. Al bajar la inductancia sube la frecuencia:

$$f = \frac{1}{2\pi\sqrt{LC}}\quad\Rightarrow\quad \frac{f}{f_0} = \left(1 + \frac{\Delta L}{L_0}\right)^{-1/2}
\;\approx\; 1 - \frac{1}{2}\frac{\Delta L}{L_0}\quad\text{(solo si } \lvert\Delta L/L_0\rvert \ll 1).$$

Con un carro el cambio es grande (−12.9 % con el Spark) y la aproximación lineal se queda corta: da +6.4 % y la
fórmula exacta +7.1 %. La simulación del oscilador con RK4 confirma el valor exacto
([03 · Métodos numéricos](03-metodos-numericos.md#39-el-oscilador-lc-del-detector)).

El detector compara la frecuencia con la que tenía sin carro. Si el cambio supera la sensibilidad configurada
(los equipos comerciales trabajan entre 0.01 % y 1 % de $\Delta L/L$), activa la salida: la talanquera se abre.
La magnitud del cambio se convierte en altura del chasis con la curva $\Delta L/L$(altura) y se elige el carro de
altura más parecida. Cuando el carro cruza, la señal sube mientras tapa la espira y baja cuando sale; su duración
depende del largo del carro y de la velocidad.

**En la línea de autopartes.** La alerta se construye en tres pasos:

1. **¿Hay pieza?** La amplitud cambia más que el umbral: $\lvert I_p - I_{p,0}\rvert / I_{p,0} \ge$ umbral
   (2 %). Un comparador con **histéresis** evita que la salida parpadee cuando la pieza está en el límite.
2. **¿Qué es y dónde está?** Clasificación en el plano de impedancia (sección 0.5).
3. **¿Es confiable?** Si el residuo supera su límite, la alerta dice "posible impureza o aleación fuera de
   catálogo" en lugar de un material.

Ejemplo de salida del simulador: *"Cobre a 6.0 mm · no ferroso"*.

El tiempo de medida pone el límite de velocidad de la banda. Con 16 promedios, dos frecuencias y 3 ciclos por
medición se tarda unos 96 ms: a 1 m/s la pieza avanza 96 mm mientras se mide.

---

# Solución e impacto

## 0.8 Eficiencia de la solución

### En el carro

| | Spark | Kwid | Diferencia |
|---|---|---|---|
| $\Delta L/L_0$ | −12.87 % | −11.39 % | 1.48 puntos |
| Frecuencia del oscilador | 59.18 kHz | 58.69 kHz | 0.49 kHz |
| Altura estimada | 14.9 cm | 18.0 cm | 3.1 cm |

- **Detección:** los dos carros superan por mucho la sensibilidad típica de un detector comercial (0.01 – 1 %).
- **Reconocimiento:** el criterio de corte natural está a mitad de camino, unos 16.5 cm. La diferencia de 0.49 kHz
  se mide con facilidad, así que el límite no es el instrumento sino el carro: un Kwid muy cargado puede bajar uno o
  dos centímetros y acercarse al Spark.
- **Tiempo de respuesta:** un período del oscilador dura 18 µs. Contar unos 1 000 ciclos (18 ms) da una resolución
  de frecuencia de aproximadamente 0.1 %, de sobra para separar los dos carros mientras el carro todavía se detiene.

### En la línea de autopartes (segundo escenario)

Evaluación con el simulador: 40 piezas de cada material a distancias aleatorias entre 1 y 8 mm, ruido de medida de
0.2 % en amplitud y 0.1° en fase por medición.

| Configuración | Material correcto | Ferroso / no ferroso | Error de distancia |
|---|---|---|---|
| 1 frecuencia, sin promediar | 84 % | 100 % | 0.29 mm |
| 2 frecuencias, sin promediar | 89 % | 100 % | 0.13 mm |
| 1 frecuencia, 16 promedios | 100 % | 100 % | 0.07 mm |
| 2 frecuencias, 16 promedios | 100 % | 100 % | 0.03 mm |

**Conclusiones:**

- Separar **ferrosos de no ferrosos** es robusto en todas las configuraciones, porque la fase cambia de signo.
- Los errores restantes son entre **cobre, aluminio y latón**, cuyas curvas están cerca. Se corrigen con dos
  frecuencias o promediando.
- Promediar mejora la exactitud a costa de tiempo: es el compromiso entre **precisión y velocidad de la banda**.

## 0.9 Impacto

- **Parqueaderos y semáforos:** la espira detecta el carro sin cámaras y sin piezas móviles, bajo la lluvia o de
  noche. Reconocer el tipo de vehículo permite cobrar tarifas distintas o contar el tránsito por clase.
- **Límite del caso del carro:** el Spark y el Kwid se diferencian en solo 1.5 puntos de $\Delta L/L$. La carga
  (pasajeros o baúl lleno) baja el carro un par de centímetros y puede confundirlos; para un reconocimiento
  robusto habría que sumar el largo del carro (duración de la señal con dos espiras) o el peso.
- **Valores del modelo:** el chasis se trata como una placa plana, así que los cambios calculados son una cota
  superior; los detectores reales reportan cambios de pocos por ciento.

- **Clasificación automática:** un solo sensor puede separar tornillos de acero, cables de cobre y conectores de
  latón en la misma banda.
- **Control de calidad:** una pieza con la aleación equivocada deja un residuo alto y genera una alerta.
- **Límites:** las piezas de conductividad casi igual (cobre impuro y aluminio) no se distinguen solo con el
  campo; haría falta otra propiedad, como el tamaño o el peso.

Análisis completo: [06 · Validación e impacto](06-validacion-e-impacto.md).

## 0.10 Mapa del proyecto

| Etapa | Documento | Código | Pestaña del simulador |
|---|---|---|---|
| Insumos y caso de estudio | este documento | `sensor/vehiculo.py`, `sensor/escena.py`, `assets/escena3d.js` | Caso: vehículo (escena 3D), Identificación |
| Figura del corte del detector | [figuras-anatomy](../figuras-anatomy/README.md) | `figuras-anatomy/corte-espira/` | Caso: vehículo |
| D · Detección | [01](01-fundamentacion-fisica.md), [02](02-modelamiento-analitico.md) | `sensor/physics.py` | Modelo |
| E · Emisiones | este documento, sección 0.5 | `sensor/identificacion.py` | Identificación |
| P · Propiedades (Maxwell) | [01](01-fundamentacion-fisica.md), [02](02-modelamiento-analitico.md) | `sensor/physics.py`, `sensor/symbolic.py` | Campo, Derivación |
| A · Alerta | este documento, sección 0.7 | `sensor/vehiculo.py` (oscilador LC), `sensor/numerics.py` (comparador), `sensor/identificacion.py` | Caso: vehículo, Paso del objeto, Identificación |
| Simulación numérica | [03](03-metodos-numericos.md) | `sensor/numerics.py` | Respuesta temporal, Validación |
| Solución e impacto | [06](06-validacion-e-impacto.md) | – | Análisis, Identificación |

## Fuentes de los datos de los carros

- Ficha técnica del Spark GT (Renting Colombia): largo, alto, entre ejes y peso.
  https://renting.rentingcolombia.com/hubfs/(RPN)%20Renting%20Persona%20Natural/Fichas%20tecnicas%20autos%20/Ficha%20tecnica%20Spark%20GT.pdf
- Altura libre al piso del Spark (2010–2014): https://cars-data.com/en/chevrolet/spark/dimensions ; otra fuente da
  17 cm: https://www.91wheels.com/faqs/what-is-the-ground-clearance-of-chevrolet-spark/217164
- Renault Kwid 1.0 (ficha de Autocosmos Perú, origen Colombia): largo, ancho, alto, peso y 180 mm de altura libre.
  https://www.autocosmos.com.pe/catalogo/comparar?v1=169660&v2=169662
- Kwid E-Tech en Colombia, 172 mm de altura libre: https://noticias.autocosmos.com.co/2025/10/20/renault-kwid-e-tech-2026-llega-a-colombia-escala-en-diseno-tecnologia-y-seguridad
- Espiras de detección de vehículos (tamaños, vueltas, frecuencias): FHWA, *Traffic Detector Handbook*,
  https://www.fhwa.dot.gov/publications/research/operations/its/06139/appendc.cfm
