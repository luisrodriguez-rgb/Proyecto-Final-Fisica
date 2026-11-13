# 6. Validación e impacto

## 6.1 Validación física del modelo

| Comprobación                            | Resultado esperado               | Resultado del modelo                    |
| ---------------------------------------- | -------------------------------- | --------------------------------------- |
| Sin pieza                                | $L = L_0$, $R = R_0$         | ✓ exacto                               |
| Conductor perfecto ($\sigma\to\infty$) | $\Gamma\to-1$, $L$ disminuye | $\Gamma = -0.99$ a 1 MHz ✓           |
| Ferromagnético a baja frecuencia        | $L$ aumenta                    | +8.4 % a 100 Hz ✓                      |
| Alejar la pieza                          | el efecto tiende a 0             | ✓ (figura de parámetros vs distancia) |
| Energía disipada en la pieza            | $\Delta R > 0$ siempre         | ✓ en los cinco materiales              |
| Escalón DC                              | $i(\tau) = 0.63\,i_{max}$      | ✓ (prueba automática)                 |
| Euler y RK4                              | órdenes 1 y 4                   | 1.01 y 4.02 ✓                          |
| Campo de una espira                      | $B(0) = \mu_0 I/2a$            | ✓ (prueba automática)                 |

En el mapa de campo, con cobre las líneas de $\vec B$ quedan paralelas a la superficie de la pieza: la
componente normal se anula, como exige la condición de frontera de un buen conductor.

![Campo magnético](figuras/campo-magnetico.png)

## 6.2 Comparación de materiales

Bobina de referencia, $f = 1$ kHz, $d = 5$ mm, umbral del 2 %:

| Material             | $\Delta L/L_0$ | $\Delta R$ (Ω) | Señal $\lvert\Delta I\rvert/I$ | Alcance $S_n$ |
| -------------------- | ---------------- | ----------------- | --------------------------------- | --------------- |
| Acero al carbono     | +5.51 %          | +0.106            | 3.24 %                            | 7.9 mm          |
| Cobre                | −8.45 %         | +0.050            | 2.35 %                            | 6.1 mm          |
| Aluminio             | −8.05 %         | +0.060            | 2.07 %                            | 5.2 mm          |
| Latón               | −6.94 %         | +0.080            | 1.41 %                            | 1.5 mm          |
| Acero inoxidable 304 | −2.71 %         | +0.090            | 0.20 %                            | no se detecta   |

**Comparación con sensores comerciales.** Los fabricantes publican factores de corrección del alcance respecto
al acero: acero 1.0, inoxidable ≈ 0.7, latón ≈ 0.5, aluminio ≈ 0.4 y cobre ≈ 0.3. El modelo acierta en que el
acero es el que se detecta más lejos, pero ordena distinto los no ferrosos. La explicación sale de la
sección 2.6: con la amplitud de corriente como señal, la caída de $L$ y la subida de $R$ se compensan
parcialmente. Los sensores comerciales usan un oscilador LC cuya amplitud depende sobre todo de las
**pérdidas**, es decir, de $\Delta R$. Si se ordena por $\Delta R$, el modelo da inoxidable > latón >
aluminio > cobre, el mismo orden que los fabricantes. Es una validación indirecta del modelo y una
recomendación de diseño: para que el sensor sea casi independiente del metal conviene medir $\Delta R$.

## 6.3 Eficiencia y energía

Con cobre a 5 mm ($I_p = 0.819$ A):

| Magnitud                                                   | Valor                     |
| ---------------------------------------------------------- | ------------------------- |
| Energía magnética máxima $\tfrac12 L I_p^2$           | 183 µJ                   |
| Potencia media total $\tfrac12 R I_p^2$                  | 1.69 W                    |
| Potencia disipada en la pieza $\tfrac12\Delta R\, I_p^2$ | 16.9 mW (1.0 % del total) |

Casi toda la potencia se pierde en el cobre del devanado ($R_0$). Solo un 1 % llega a la pieza, y es esa
fracción la que produce la señal. Los 1.69 W salen de los valores elegidos para ilustrar ($V_0 = 5$ V,
$R_0 = 5\ \Omega$). Un sensor real trabaja con corrientes de miliamperios y consume del orden de mW; el
modelo escala con $V_0^2$.

## 6.4 Impacto en una línea de producción automatizada

El tiempo de respuesta se estima como el tiempo de estabilización del circuito más los ciclos que necesita el
demodulador: $t_r = 5\tau + nT$. Con $\tau = 108\ \mu$s, $f = 1$ kHz y $n = 3$:

| Magnitud                                        | Valor    |
| ----------------------------------------------- | -------- |
| Tiempo de respuesta                             | 3.54 ms  |
| Frecuencia de conmutación máxima $1/(2t_r)$ | 141 Hz   |
| Piezas por minuto                               | ≈ 8 500 |
| Velocidad máxima de la banda (pieza de 30 mm)  | 8.5 m/s  |

Subir la frecuencia de alimentación acorta $t_r$ (a 10 kHz, $t_r \approx 0.84$ ms), pero reduce $\delta$ y
cambia la respuesta a los materiales ferrosos. Es una decisión de diseño entre velocidad y selectividad. En
control de calidad, la diferencia de señal entre materiales permite separar piezas de acero de piezas no
ferrosas con un solo sensor y dos umbrales.

## 6.5 Limitaciones frente a un análisis por elementos finitos (FEM)

| Limitación del modelo             | Qué haría un modelo FEM (COMSOL, FEMM, Elmer)                                             |
| ---------------------------------- | ------------------------------------------------------------------------------------------- |
| Pieza como semiespacio infinito    | Geometría real: piezas pequeñas, delgadas (espesor < 3δ) o con bordes acoplan menos      |
| Bobina de capa delgada sin núcleo | Núcleo de ferrita en copa, que concentra el campo en la cara activa y aumenta el alcance   |
| Materiales lineales                | Saturación, histéresis magnética, dependencia de $\mu_r$ con el campo y la temperatura |
| Régimen cuasi-estático           | Capacitancia entre espiras y resonancia propia de la bobina                                 |
| Movimiento axial y lento           | Paso lateral de la pieza, velocidad alta y efectos de movimiento ($\vec v\times\vec B$)   |
| Electrónica idealizada            | Oscilador LC real, ruido, deriva térmica                                                   |

A cambio, el modelo es **semianalítico**: se evalúa en milisegundos y permite barrer parámetros en vivo. Con
FEM cada punto tardaría minutos. Como herramienta de diseño preliminar y de enseñanza, el compromiso es
adecuado.

## 6.6 Comprobaciones adicionales del modelo

| Comprobación                                               | Resultado                                                                        |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Flujo por espira con campo uniforme, $L\approx N\Phi_B/i$ | 0.55 mH frente a 0.60 mH de Wheeler (diferencia por la no uniformidad del campo) |
| Campo lejano frente a dipolo $\mu_0 2m/4\pi z^3$          | razón 0.99 a 8 radios ✓                                                        |
| Balance de energía al energizar                            | error $5\times10^{-7}$ ✓                                                      |
| Ejercicio RC de clase con el mismo código                  | $\tau = 12$ s, $q_{max} = 1.8$ mC, RK4 con error $6\times10^{-10}$ C ✓    |
| Cambio relativo de $L$ independiente de $N$             | −8.45 % para cualquier $N$ ✓ (las dos crecen con $N^2$)                    |

## 6.7 Recomendaciones de diseño que salen del modelo

1. **Aumentar el radio antes que la corriente.** El alcance escala con el radio ($S_n/a \approx 1$ en bobinas
   grandes) porque el campo cae como $1/z^3$. Más corriente no cambia la forma de esa caída.
2. **Factor de calidad alto.** Alambre grueso o más espiras para que $\omega L \gg R$. Con $Q < 0.5$ casi no hay señal.
3. **Frecuencia entre 2 y 10 kHz para metales mixtos.** En ese rango el cobre ya está cerca de su máximo y el acero
   todavía se detecta. Hay que evitar la frecuencia ciega del acero (~20 kHz).
4. **Medir pérdidas ($\Delta R$) en lugar de la amplitud** si se necesita detectar todos los metales de forma
   parecida, como hacen los osciladores LC comerciales.
5. **Usar histéresis.** Evita que la salida parpadee cuando la pieza se queda cerca del umbral.

## 6.8 Aplicaciones

El apunte de clase pide consultar aplicaciones del circuito RC. Estas son las del principio inductivo que modelamos:

| Aplicación                                        | Cómo usa el mismo principio                                                                  |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Conteo y posicionamiento de piezas en bandas       | Exactamente el caso simulado                                                                  |
| Medición de velocidad de engranajes (RPM)         | Cada diente que pasa frente a la bobina es una pieza; la frecuencia de pulsos da la velocidad |
| Detectores de metales y de minas                   | Bobina grande (alcance ∝ radio) y medición de $\Delta Z$                                  |
| Lazos inductivos en semáforos y parqueaderos      | Una espira enterrada en el pavimento detecta la carrocería del carro                         |
| Validadores de monedas                             | La frecuencia y la amplitud de $\Delta Z$ identifican la aleación de la moneda             |
| Ensayos no destructivos por corrientes de Foucault | Una grieta interrumpe las corrientes y cambia $\Delta Z$; se usa en aviones y tuberías     |
| Cocinas de inducción y frenos magnéticos         | La misma física, pero buscando el calor ($\Delta R$) en vez de la señal                   |

## 6.9 Comparación con otras tecnologías de detección

|                         | Inductivo                      | Capacitivo (visto en clase)              | Óptico                |
| ----------------------- | ------------------------------ | ---------------------------------------- | ---------------------- |
| Detecta                 | Solo metales                   | Metales, plásticos, líquidos, personas | Cualquier objeto opaco |
| Alcance típico         | 1 – 40 mm                     | 1 – 30 mm                               | centímetros a metros  |
| Polvo, aceite, suciedad | No le afectan                  | Le afectan                               | Le afectan mucho       |
| Costo y robustez        | Bajo y muy robusto             | Bajo                                     | Medio                  |
| Uso típico             | Piezas metálicas en máquinas | Nivel de líquidos, pantallas            | Cajas en bandas        |

## 6.10 Fuentes de error del modelo

| Fuente                               | Efecto esperado                                                                                      |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------- |
| $\sigma$ y $\mu_r$ tabulados     | El acero real tiene $\mu_r$ entre 50 y 1000 según la aleación; cambia mucho el resultado ferroso |
| Fórmula de Wheeler                  | Error cercano al 1 % en $L_0$                                                                      |
| Malla de integración de Dodd–Deeds | Error relativo de 1.3×10⁻⁶ frente a una malla diez veces más fina                                |
| Paso temporal                        | Controlado: RK4 con 40 pasos por ciclo da $10^{-5}$ A de error                                     |
