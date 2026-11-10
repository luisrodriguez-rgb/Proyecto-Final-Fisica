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

**Contexto de inicio elegido:** una línea de producción de autopartes por la que pasan piezas de distintos
metales. Es el ejemplo que propuso el profesor y reúne las dos tareas de la detección: saber **qué** metal es y
**a qué distancia** está.

## 0.2 Caso específico de estudio

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

| Etapa | Qué pasa físicamente |
|---|---|
| **D · Detección** | La bobina crea un campo magnético variable alrededor de su cara activa. Cuando una pieza entra en ese campo, el sistema debe decidir qué material es y a qué distancia está. |
| **E · Emisiones** | La pieza responde al campo: en ella se inducen corrientes de Foucault (y, si es ferromagnética, se magnetiza). Esas corrientes crean su propio campo, que vuelve a la bobina y cambia su corriente. Esa respuesta es la "emisión" que el sensor mide. |
| **P · Propiedades** | La respuesta depende de la **frecuencia** (que fija la profundidad de penetración), de la **energía** guardada en el campo y de la **potencia** que la pieza absorbe. Estas propiedades llevan la información del material y de la distancia. |
| **A · Alerta** | El sistema compara la medición con lo que esperaría de cada material y entrega una alerta: material, distancia y, si corresponde, aviso de impureza. |

---

# Parte 2. Formalismo matemático por etapa

## 0.4 D · Detección: propiedades de los materiales y de la radiación

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

La alerta se construye en tres pasos:

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

- **Clasificación automática:** un solo sensor puede separar tornillos de acero, cables de cobre y conectores de
  latón en la misma banda.
- **Control de calidad:** una pieza con la aleación equivocada deja un residuo alto y genera una alerta.
- **Límites:** las piezas de conductividad casi igual (cobre impuro y aluminio) no se distinguen solo con el
  campo; haría falta otra propiedad, como el tamaño o el peso.

Análisis completo: [06 · Validación e impacto](06-validacion-e-impacto.md).

## 0.10 Mapa del proyecto

| Etapa | Documento | Código | Pestaña del simulador |
|---|---|---|---|
| Insumos y caso de estudio | este documento | – | Identificación |
| D · Detección | [01](01-fundamentacion-fisica.md), [02](02-modelamiento-analitico.md) | `sensor/physics.py` | Modelo |
| E · Emisiones | este documento, sección 0.5 | `sensor/identificacion.py` | Identificación |
| P · Propiedades (Maxwell) | [01](01-fundamentacion-fisica.md), [02](02-modelamiento-analitico.md) | `sensor/physics.py`, `sensor/symbolic.py` | Campo, Derivación |
| A · Alerta | este documento, sección 0.7 | `sensor/numerics.py` (comparador), `sensor/identificacion.py` | Paso del objeto, Identificación |
| Simulación numérica | [03](03-metodos-numericos.md) | `sensor/numerics.py` | Respuesta temporal, Validación |
| Solución e impacto | [06](06-validacion-e-impacto.md) | – | Análisis, Identificación |
