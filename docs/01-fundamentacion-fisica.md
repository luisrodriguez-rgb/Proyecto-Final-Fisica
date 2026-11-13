# 1. Fundamentación física

> Criterio de la rúbrica: **Fundamentación física (15 %)**, aplicación correcta de las ecuaciones de Maxwell.

## 1.1 Descripción del fenómeno

Un sensor inductivo de proximidad es una bobina alimentada con corriente. La corriente crea un campo
magnético $\vec B(t)$ alrededor de la bobina. Cuando una pieza metálica entra en ese campo, pasa lo siguiente:

1. El flujo magnético que atraviesa la pieza cambia en el tiempo y, por la **ley de Faraday**, se induce en
   ella un campo eléctrico $\vec E$ que circula alrededor del eje de la bobina.
2. Como la pieza es conductora, ese campo mueve cargas: aparecen **corrientes de Foucault**
   $\vec J = \sigma \vec E$ (ley de Ohm en forma local, la misma $\Delta V = iR$ de clase escrita punto a punto).
3. Por la **ley de Lenz**, esas corrientes crean su propio campo, opuesto al de la bobina. Parte del flujo
   deja de enlazar la bobina, así que su **inductancia efectiva disminuye**.
4. Las corrientes de Foucault disipan energía por efecto Joule dentro de la pieza. Para el circuito esa
   pérdida se ve como un **aumento de la resistencia efectiva**.
5. Si la pieza es ferromagnética ($\mu_r \gg 1$), además se magnetiza y concentra el flujo, lo que tiende a
   **aumentar** la inductancia. El resultado final depende de la frecuencia.

El cambio de $L$ y $R$ cambia la corriente del circuito. El sensor compara la amplitud de esa corriente con
la que tendría sin pieza y se activa cuando la diferencia supera un umbral.

Es el mismo principio de la pantalla táctil capacitiva vista en clase, pero con campo magnético: allí el dedo
cambia la capacitancia ($\Delta C = C_{\text{con dedo}} - C_{\text{sin dedo}}$) y aquí la pieza cambia la
inductancia ($\Delta L = L_{\text{con pieza}} - L_0$).

## 1.2 Diagrama del sistema

![Diagrama del sistema](figuras/diagrama-sistema.svg)

La pieza ocupa la región $z<0$. La bobina, de radio $a$, longitud $l$ y $N$ espiras, está entre $z=d$ y
$z=d+l$. A la derecha está el circuito equivalente que resuelve el simulador.

**Caso principal, el carro sobre la espira.** La misma geometría, a otra escala: la "bobina" es una espira
cuadrada de 1.8 m enterrada en el pavimento, y la "pieza" es el chasis de acero del carro, a su altura libre al piso.

![Corte del detector de espira (figura hecha con Anatomy)](figuras/anatomy-corte-espira.png)

## 1.3 Variables del modelo

| Variable | Símbolo | Tipo | Unidad SI |
|---|---|---|---|
| Campo magnético | $\vec B$ | vectorial | T = Wb/m² |
| Intensidad magnética | $\vec H = \vec B/\mu$ | vectorial | A/m |
| Campo eléctrico inducido | $\vec E$ | vectorial | V/m |
| Densidad de corriente (Foucault) | $\vec J$ | vectorial | A/m² |
| Potencial vector | $\vec A$ ($\vec B = \nabla\times\vec A$) | vectorial | Wb/m |
| Flujo magnético | $\Phi_B$ | escalar | Wb |
| Corriente del circuito | $i(t)$ | escalar | A |
| Fem de la fuente | $\varepsilon(t)$ | escalar | V |
| Inductancia, resistencia | $L$, $R$ | escalar | H, Ω |
| Conductividad, permeabilidad relativa | $\sigma$, $\mu_r$ | escalar | S/m, adimensional |
| Frecuencia angular | $\omega = 2\pi f$ | escalar | rad/s |
| Geometría | $N$, $a$, $l$, $d$ | escalar | –, m, m, m |
| Altura libre al piso del carro, profundidad de la espira | $h_{piso}$, $p$ ($d = h_{piso} + p$) | escalar | m |
| Capacitancia y frecuencia del oscilador del detector | $C$, $f_0 = 1/2\pi\sqrt{L_0C}$ | escalar | F, Hz |

## 1.4 Ecuaciones de Maxwell utilizadas

Se escriben en forma integral, como se trabajaron en clase con la ley de Gauss
($\Phi = \vec E\cdot\vec A$ para una superficie plana y $\oint \vec E\cdot d\vec A = q_{enc}/\varepsilon_0$
para una superficie cerrada), y en forma diferencial.

| Ley | Forma integral | Forma diferencial | Papel en el modelo |
|---|---|---|---|
| Gauss eléctrica | $\oint_A \vec E\cdot d\vec A = q_{enc}/\varepsilon_0$ | $\nabla\cdot\vec E = \rho/\varepsilon_0$ | Dentro del conductor no hay carga neta libre acumulada ($\rho = 0$): las corrientes de Foucault circulan en lazos cerrados. |
| Gauss magnética | $\oint_A \vec B\cdot d\vec A = 0$ | $\nabla\cdot\vec B = 0$ | Las líneas de $\vec B$ son cerradas. Permite escribir $\vec B = \nabla\times\vec A$ y exige que $B_z$ sea continuo en la superficie de la pieza. |
| Faraday | $\oint_C \vec E\cdot d\vec l = -\dfrac{d\Phi_B}{dt}$ | $\nabla\times\vec E = -\dfrac{\partial\vec B}{\partial t}$ | Origen de la fem autoinducida de la bobina ($-L\,di/dt$) y del campo que mueve las corrientes de Foucault. |
| Ampère–Maxwell | $\oint_C \vec B\cdot d\vec l = \mu_0\left(I_{enc} + \varepsilon_0\dfrac{d\Phi_E}{dt}\right)$ | $\nabla\times\vec H = \vec J + \dfrac{\partial\vec D}{\partial t}$ | Da el campo de la bobina y el campo de reacción de las corrientes de Foucault. |

**Cuáles se necesitan.** Siguiendo la orientación del profesor, solo se discuten las ecuaciones que el sensor
usa. **Faraday** es la central y **Ampère** (sin corriente de desplazamiento) da los campos. Gauss magnética
entra solo como condición de frontera, y Gauss eléctrica no se necesita: no hay acumulación de carga. Ver
[00 · Modelo teórico D.E.P.A.](00-modelo-teorico-depa.md#06-p--propiedades-de-las-ondas-em-solo-las-ecuaciones-de-maxwell-necesarias).

### Justificación de la aproximación cuasi-estática

Se desprecia la corriente de desplazamiento $\varepsilon_0\,d\Phi_E/dt$:

- **Dentro del metal**, la razón entre corriente de desplazamiento y de conducción es
  $\omega\varepsilon_0/\sigma$. Para cobre a 1 kHz: $\dfrac{2\pi(1000)(8.85\times10^{-12})}{5.96\times10^{7}}
  \approx 9\times10^{-19}$. Es completamente despreciable.
- **En el aire**, la longitud de onda a 1 kHz es $\lambda = c/f = 300$ km, mucho mayor que la bobina
  (centímetros). No hay radiación y el campo sigue a la corriente de forma instantánea.

Con esto, las ecuaciones que se resuelven son

$$\nabla\times\vec H = \vec J = \sigma\vec E,\qquad \nabla\times\vec E = -j\omega\vec B,\qquad \nabla\cdot\vec B = 0 .$$

Combinándolas con $\vec B = \nabla\times\vec A$, se obtiene en el aire $\nabla^2\vec A = 0$ y en el
conductor la **ecuación de difusión**

$$\nabla^2\vec A = j\omega\mu_0\mu_r\sigma\,\vec A ,$$

cuya escala natural de longitud es la **profundidad de penetración**

$$\delta = \sqrt{\frac{2}{\omega\mu_0\mu_r\sigma}} .$$

Las corrientes de Foucault viven en una capa de espesor $\sim\delta$. Para cobre a 1 kHz,
$\delta = 2.06$ mm; para acero al carbono ($\mu_r = 100$), $\delta = 0.65$ mm.

## 1.5 Condiciones de frontera e iniciales

**Frontera** (superficie de la pieza, $z = 0$, sin corrientes superficiales):

- $B_z$ es continuo (de $\oint\vec B\cdot d\vec A = 0$ sobre una caja de altura cero).
- $H_\rho = B_\rho/\mu$ es continuo (de Ampère sobre un rectángulo de altura cero).
- Los campos tienden a cero lejos de la bobina ($z\to\pm\infty$, $\rho\to\infty$).

Con esas condiciones aparece el coeficiente de reflexión
$\Gamma = \dfrac{\mu_r\alpha - \alpha_1}{\mu_r\alpha + \alpha_1}$ usado en el
[modelamiento analítico](02-modelamiento-analitico.md#24-efecto-de-la-pieza-metálica).

Casos límite que sirven para revisar el modelo:

| Material | Condición | $\Gamma$ | Efecto sobre $L$ |
|---|---|---|---|
| Conductor perfecto | $\sigma\to\infty$: $B_z = 0$ en la superficie | $-1$ | Disminuye (imagen con corriente opuesta) |
| Ferromagnético no conductor | $\sigma = 0$: $H_\rho\approx 0$ en la superficie | $(\mu_r-1)/(\mu_r+1)$ | Aumenta (imagen con la misma corriente) |
| Aire | $\sigma = 0,\ \mu_r = 1$ | $0$ | No cambia |

**Inicial**: corriente de la bobina $i(0) = I_0$ (por defecto $0$, bobina desenergizada).

## 1.6 Hipótesis

1. Régimen cuasi-estático (justificado arriba).
2. Materiales lineales, homogéneos e isótropos: $\sigma$ y $\mu_r$ constantes, sin saturación ni histéresis.
3. Bobina de capa delgada, sin núcleo de ferrita y sin capacitancia entre espiras.
4. Pieza modelada como un semiespacio: más ancha que la bobina y más gruesa que unas $3\delta$.
5. Movimiento lento de la pieza frente al período de la fuente: para cada posición se usa la inductancia
   de esa posición ("inductancia constante por cada posición de detección", como sugiere la propuesta).

## 1.7 Del campo eléctrico de clase al campo magnético del sensor

Lo visto en clase para el campo eléctrico tiene su equivalente magnético. Esta correspondencia ordena todo el proyecto.

| Electrostática (clase) | Magnetismo del sensor |
|---|---|
| Carga puntual: $\vec E = K\dfrac{q}{r^2}\hat r$ | Elemento de corriente (Biot–Savart): $d\vec B = \dfrac{\mu_0}{4\pi}\dfrac{i\,d\vec l\times\hat r}{r^2}$ |
| $\vec E = -\nabla V$ (potencial escalar) | $\vec B = \nabla\times\vec A$ (potencial vector) |
| Gauss: $\oint\vec E\cdot d\vec A = q_{enc}/\varepsilon_0$ | Gauss magnética: $\oint\vec B\cdot d\vec A = 0$ (no hay "cargas magnéticas") |
| Flujo $\Phi_E = \vec E\cdot\vec A$ | Flujo $\Phi_B = \vec B\cdot\vec A$ |
| Capacitancia $C = Q/\lvert\Delta V\rvert$, depende solo de la geometría | Inductancia $L = \Lambda/i$, depende solo de la geometría |
| Capacitor de placas: el campo queda confinado entre las placas | Solenoide: el campo queda confinado dentro de la bobina |
| Dieléctrico: se polariza y **reduce** el campo, $E_d = E/K_d$ | Ferromagnético: se magnetiza y **refuerza** el campo, $B = \mu_r\mu_0 H$ |
| Conductor en equilibrio: $\vec E = 0$ adentro, la carga se va a la superficie | Conductor con campo variable: $\vec B$ solo entra una capa $\delta$, las corrientes van a la superficie |
| Energía $\tfrac12 CV^2$, densidad $u_E = \tfrac12\varepsilon_0E^2$ | Energía $\tfrac12 Li^2$, densidad $u_B = \dfrac{B^2}{2\mu_0}$ |
| Dipolo eléctrico: campo lejano $\propto 1/r^3$ | Dipolo magnético: campo lejano $\propto 1/r^3$ |
| Pantalla táctil: el dedo cambia $C$, se mide $\Delta C$ | Sensor inductivo: la pieza cambia $L$, se mide $\Delta L$ |

Dos de estas filas explican casi todo el sensor:

- **El conductor apantalla.** En clase vimos que dentro de un conductor en equilibrio el campo eléctrico es cero
  porque las cargas libres se reacomodan. Con un campo magnético que cambia pasa algo parecido: las corrientes
  inducidas se reacomodan para anular el campo dentro del metal, pero no lo consiguen del todo. El campo entra
  una profundidad $\delta$ y por eso la pantalla es imperfecta y depende de la frecuencia.
- **El material magnético se comporta al revés que el dieléctrico.** Un dieléctrico debilita el campo eléctrico
  porque sus dipolos se orientan en contra. Un ferromagnético refuerza el campo magnético porque sus dipolos se
  orientan a favor. Eso explica por qué el acero puede **aumentar** la inductancia.

## 1.8 Flujo magnético a través de la bobina

Igual que en el apunte de Gauss, el flujo a través de una superficie plana es el producto punto entre el campo y
el vector área, $\vec A = A\hat n$:

$$\Phi_B = \vec B\cdot\vec A = BA\cos\alpha .$$

La espira es perpendicular al eje, así que en el centro $\alpha = 0$ y $\Phi_B = BA$. Con los valores de
referencia (sin pieza, corriente pico $0.800$ A), el campo en el centro de la bobina es

$$B_{centro} = 4.17\ \text{mT}\qquad(\text{el solenoide ideal daría } \mu_0Ni/l = 7.54\ \text{mT}).$$

Si se supone ese campo uniforme sobre el área $A = \pi a^2 = 7.07\times10^{-4}$ m², cada espira atrapa
$\Phi_B \approx 2.95\times10^{-6}$ Wb y el flujo enlazado es $\Lambda = N\Phi_B \approx 4.4\times10^{-4}$ Wb.
Entonces $L \approx \Lambda/i = 0.55$ mH, muy cerca de los 0.60 mH de la fórmula de Wheeler. La diferencia viene de
que el campo no es uniforme: es más fuerte cerca del alambre que en el centro.

Sobre una superficie **cerrada** el flujo magnético es siempre cero (Gauss magnética): todas las líneas que salen
por una cara de la bobina vuelven a entrar por la otra, como muestra el mapa de campo del simulador.

## 1.9 Órdenes de magnitud

| Magnitud | Valor | Para comparar |
|---|---|---|
| Campo en el centro de la bobina | 4.2 mT | Campo de la Tierra: 0.05 mT; imán de nevera: ~5 mT |
| Densidad de energía en el centro $B^2/2\mu_0$ | 6.9 J/m³ | |
| Momento dipolar $m = Ni\pi a^2$ | 0.085 A·m² | |
| Profundidad de penetración en cobre (1 kHz) | 2.1 mm | Más delgada que una moneda |
| Corriente de desplazamiento / de conducción en cobre | $10^{-18}$ | |
| Longitud de onda a 1 kHz | 300 km | La bobina mide 30 mm |

## 1.10 La bobina vista de lejos: un dipolo magnético

En la clase de interacción eléctrica se calculó el campo de un dipolo eléctrico y se vio que lejos cae como
$1/r^3$. Una espira con corriente es el equivalente magnético: un **dipolo magnético** de momento
$m = Ni\pi a^2$. Sobre el eje y lejos de la bobina ($z \gg a$),

$$B_z \approx \frac{\mu_0}{4\pi}\frac{2m}{z^3} .$$

| Distancia al borde de la bobina | $B$ calculado / $B$ de dipolo |
|---|---|
| 30 mm ($2a$) | 0.82 |
| 60 mm ($4a$) | 0.96 |
| 120 mm ($8a$) | 0.99 |

![Campo dipolar](figuras/campo-dipolo.png)

**Consecuencia para el sensor:** el campo que llega a la pieza cae como $1/z^3$, y el campo de las corrientes de
Foucault que vuelve a la bobina cae otra vez. El efecto total disminuye mucho más rápido que el campo. Por eso
**el alcance de un sensor inductivo es del orden de su radio**: para detectar más lejos hay que hacer la bobina
más grande, no solo darle más corriente.

## 1.11 La ley de Lenz, paso a paso

Para fijar los signos, tomemos el instante en que la corriente de la bobina **aumenta** en sentido horario
visto desde arriba (regla de la mano derecha: el campo de una corriente horaria vista desde arriba apunta hacia
abajo):

1. El campo de la bobina apunta hacia abajo, hacia la pieza, y está creciendo.
2. El flujo hacia abajo a través de cualquier círculo en la superficie del metal crece: $d\Phi_B/dt > 0$.
3. Faraday: el campo eléctrico inducido circula de modo que su propio campo se oponga a ese aumento; visto desde
   arriba circula en sentido **antihorario**.
4. En el metal, $\vec J = \sigma\vec E$ también circula en sentido antihorario.
5. Una corriente antihoraria vista desde arriba crea un campo hacia **arriba**: se opone al aumento del flujo
   hacia abajo.

Medio ciclo después todo se invierte, y siempre se cumple lo mismo: las corrientes de Foucault se oponen al cambio
que las produce.

## 1.12 El caso del carro: la misma física a otra escala

Todo lo anterior vale para la espira de parqueadero. Lo que cambia son las escalas, y conviene revisarlas una por
una para justificar que el modelo sigue siendo válido.

| Magnitud | Bobina de autopartes | Espira de parqueadero |
|---|---|---|
| Tamaño | radio 15 mm, 150 vueltas | cuadrado de 1.8 m (radio equivalente 1.02 m), 3 vueltas |
| Inductancia | 0.60 mH | 83 µH |
| Frecuencia | 1 kHz (fuente) | 55.2 kHz (oscilador LC con $C$ = 0.1 µF) |
| Objeto y distancia | pieza a milímetros | chasis de acero a 20 – 23 cm |
| Profundidad de penetración en el acero | 0.65 mm | 0.087 mm |
| Efecto del acero sobre $L$ | sube (magnetización) | **baja** (apantallamiento) |

**Por qué el acero baja la inductancia aquí y la subía en la bobina pequeña.** A 55 kHz el campo entra apenas
0.087 mm en el acero, mucho menos que el espesor de la lámina del chasis (alrededor de 1 mm). Las corrientes de
Foucault se concentran en esa capa y expulsan el flujo, así que el chasis se comporta casi como un conductor
perfecto ($\Gamma \to -1$). La magnetización solo gana a frecuencias bajas: es la "frecuencia ciega" del acero
encontrada en el estudio de escenarios, que para la bobina pequeña está cerca de 20 kHz. El detector de espira
trabaja muy por encima de ella.

**La aproximación cuasi-estática sigue valiendo.** A 55.2 kHz la longitud de onda es $c/f = 5.4$ km, unas 3 000
veces el tamaño de la espira. En el acero, la razón entre corriente de desplazamiento y de conducción es
$\omega\varepsilon_0/\sigma = 5\times10^{-13}$. Las ecuaciones necesarias son otra vez solo Faraday y Ampère, con
Gauss magnética como condición de frontera en la cara inferior del chasis.

**Un campo muy débil.** Con 50 mA en la espira, el campo en su centro es $B = \mu_0 N I / 2a \approx 0.09\ \mu$T,
unas 500 veces menor que el campo de la Tierra (unos 50 µT). Aun así el detector funciona, porque no mide el campo:
mide la **frecuencia** del oscilador. El campo terrestre es constante y no induce nada (Faraday solo responde a
cambios), así que no interfiere.

**El alcance depende del tamaño de la espira.** Vista de lejos, la espira es un dipolo magnético de momento
$m = N I A = 0.49$ A·m², y su campo cae como $1/z^3$ a partir de distancias del orden de su tamaño (sección
1.10). Por eso una espira de 1.8 m detecta un chasis a 20 cm con un cambio de inductancia de más del 10 %. Una
bicicleta o una moto, con poco metal y estrecho, cambian mucho menos: es el problema práctico conocido de estos
detectores.

**Hipótesis adicionales del caso del carro:**

1. El chasis se trata como una placa plana de acero infinita a la altura libre al piso. Un chasis real tiene huecos,
   el túnel de la transmisión y el escape, así que el valor calculado es una **cota superior**.
2. El tamaño finito del carro se incluye multiplicando el cambio de impedancia por la fracción de la espira que el
   carro tapa (factor de cobertura).
3. La espira cuadrada se representa por una espira circular de igual área.
4. $\mu_r$ y $\sigma$ del acero son constantes; la carga del carro no cambia su altura.
