# 3. Métodos numéricos

> Criterio de la rúbrica: **Métodos numéricos (20 %)**, implementación y comparación de Euler y RK4.
> Indicadores de la guía: error absoluto, error relativo, convergencia, influencia del paso temporal,
> consistencia dimensional y coherencia con los principios físicos.

Código: [`sensor/numerics.py`](../sensor/numerics.py). Pruebas: [`tests/test_modelo.py`](../tests/test_modelo.py).
Pestañas del simulador: **Respuesta temporal**, **Paso del objeto** y **Validación**.

## 3.1 Problema de valor inicial

Toda la dinámica del sensor se escribe como una EDO de primer orden $\;i' = f(t, i)$, $\;i(0) = I_0$:

| Caso | $f(t, i)$ | Solución de referencia |
|---|---|---|
| Escalón DC | $\dfrac{V_0 - Ri}{L}$, y $-\dfrac{Ri}{L}$ al desenergizar | exacta, ec. (2) |
| Alterna | $\dfrac{V_0\sin\omega t - Ri}{L}$ | exacta, ec. (3) |
| Pieza en movimiento | $\dfrac{V_0\sin\omega t - \left[R(t)+\dot L(t)\right] i}{L(t)}$ | `solve_ivp` con `rtol = 1e-8` |

## 3.2 Métodos programados a mano

Con paso $h = \Delta t$ y $t_k = t_0 + kh$:

**Euler explícito** (se toma la pendiente al inicio del intervalo):

$$i_{k+1} = i_k + h\, f(t_k, i_k)$$

**Runge–Kutta clásico de cuarto orden**: se promedian cuatro pendientes, una al inicio, dos en el punto medio
y una al final del intervalo.

$$\begin{aligned}
k_1 &= f(t_k,\ i_k) & k_2 &= f\!\left(t_k + \tfrac h2,\ i_k + \tfrac h2 k_1\right)\\
k_3 &= f\!\left(t_k + \tfrac h2,\ i_k + \tfrac h2 k_2\right) & k_4 &= f(t_k + h,\ i_k + h k_3)\\
i_{k+1} &= i_k + \tfrac h6\,(k_1 + 2k_2 + 2k_3 + k_4)
\end{aligned}$$

Las funciones `euler` y `rk4` son genéricas (reciben cualquier `f(t, y)`) y no usan ninguna librería de
integración. `scipy.integrate.solve_ivp` (RK45 adaptativo) se usa **solo para contrastar**, como permite la guía.

Dos detalles de implementación:

- **Discontinuidad del interruptor (DC).** Al pasar de A a B la fem salta de $V_0$ a $0$. Si ese salto cae
  dentro de un paso, RK4 evaluaría $k_4$ con la fem equivocada y perdería su orden. Por eso se integra por
  tramos: primero el energizado hasta $t_s$ y luego el desenergizado desde $t_s$.
- **Inductancia variable.** $L(t)$, $R(t)$ y $\dot L(t)$ se precalculan en la malla de medio paso
  $t_k,\ t_k + h/2,\ t_k + h$, que son exactamente los instantes donde RK4 evalúa $f$.

## 3.3 Definición de los errores

$$e_{abs} = \max_k\,\big|i_k - i(t_k)\big|,\qquad
e_{rel} = \frac{e_{abs}}{\max_k |i(t_k)|}\times 100\ \% .$$

El error relativo se normaliza con la amplitud máxima. El cociente punto a punto
$|i_k - i(t_k)|/|i(t_k)|$ no sirve aquí porque la corriente alterna pasa por cero y el cociente diverge.

**Orden observado** entre dos pasos consecutivos (cada fila usa la mitad del paso anterior):

$$p = \frac{\ln(e_k/e_{k+1})}{\ln(h_k/h_{k+1})} .$$

## 3.4 Resultados: convergencia y error

Bobina de referencia con cobre a 5 mm ($L = 0.5462$ mH, $R = 5.0503\ \Omega$, $\tau = 108.1\ \mu$s), $V_0 = 5$ V.

### Alterna, 1 kHz, 3 ciclos

| Pasos/ciclo | $\Delta t$ (µs) | Euler $e_{abs}$ (A) | Euler $e_{rel}$ | RK4 $e_{abs}$ (A) | RK4 $e_{rel}$ | $p$ Euler | $p$ RK4 |
|---|---|---|---|---|---|---|---|
| 10 | 100.0 | 0.208 | 25.6 % | 3.34e−3 | 0.41 % | – | – |
| 20 | 50.0 | 0.078 | 9.27 % | 1.75e−4 | 0.021 % | 1.43 | 4.26 |
| 40 | 25.0 | 0.038 | 4.48 % | 9.85e−6 | 1.2e−3 % | 1.05 | 4.15 |
| 80 | 12.5 | 0.018 | 2.20 % | 5.84e−7 | 7.0e−5 % | 1.02 | 4.08 |
| 160 | 6.25 | 9.14e−3 | 1.09 % | 3.55e−8 | 4.2e−6 % | 1.01 | 4.04 |
| 320 | 3.125 | 4.55e−3 | 0.54 % | 2.19e−9 | 2.6e−7 % | 1.01 | 4.02 |

### Escalón DC, duración $6\tau$

| Pasos/τ | $\Delta t$ (µs) | Euler $e_{abs}$ (A) | Euler $e_{rel}$ | RK4 $e_{abs}$ (A) | RK4 $e_{rel}$ | $p$ Euler | $p$ RK4 |
|---|---|---|---|---|---|---|---|
| 2 | 54.07 | 0.117 | 12.4 % | 2.89e−4 | 0.031 % | – | – |
| 4 | 27.04 | 0.051 | 5.42 % | 1.46e−5 | 1.6e−3 % | 1.20 | 4.30 |
| 8 | 13.52 | 0.024 | 2.55 % | 8.23e−7 | 8.7e−5 % | 1.09 | 4.15 |
| 16 | 6.76 | 0.012 | 1.24 % | 4.88e−8 | 5.2e−6 % | 1.04 | 4.08 |
| 32 | 3.38 | 5.77e−3 | 0.61 % | 2.97e−9 | 3.2e−7 % | 1.02 | 4.04 |
| 64 | 1.69 | 2.86e−3 | 0.30 % | 1.83e−10 | 1.9e−8 % | 1.01 | 4.02 |

![Convergencia](figuras/convergencia.png)

**Lectura de las tablas**

- Al dividir $\Delta t$ entre 2, el error de Euler se divide entre 2 ($p\to 1$) y el de RK4 entre 16 ($p\to 4$).
  Coinciden con los órdenes teóricos $\mathcal O(h)$ y $\mathcal O(h^4)$.
- Para una precisión del 1 %, Euler necesita unos 160 pasos por ciclo; RK4 la alcanza con 10.
- RK4 hace 4 evaluaciones de $f$ por paso y Euler 1. Aun así, RK4 con 20 pasos (80 evaluaciones) es unas 26 veces
  más preciso que Euler con 320 pasos (320 evaluaciones).
- Con pasos muy pequeños el error de RK4 baja hasta el redondeo de máquina ($\sim10^{-15}$ A) y el orden deja de
  poder medirse. El simulador lo indica.

## 3.5 Influencia del paso: estabilidad

En la EDO homogénea $i' = -i/\tau$, un paso de Euler multiplica la corriente por $(1 - h/\tau)$. Para que el
error no crezca hace falta

$$\left|1 - \frac{h}{\tau}\right| < 1 \quad\Rightarrow\quad h < 2\tau .$$

RK4 multiplica por $1 - x + x^2/2 - x^3/6 + x^4/24$ con $x = h/\tau$, que es estable para $h < 2.785\,\tau$.
Con $\tau = 108\ \mu$s el límite de Euler es $\Delta t < 216\ \mu$s. A 100 Hz y 40 pasos por ciclo,
$\Delta t = 250\ \mu$s: Euler diverge y el simulador lo avisa. Lo que hay que comparar es $\Delta t/\tau$, no
$\Delta t$ solo.

## 3.6 Consistencia dimensional y coherencia física

- $h\,f(t,i)$ tiene unidades de s·A/s = A, igual que $i$, así que cada actualización es dimensionalmente
  correcta. El parámetro que controla la estabilidad, $h/\tau$, es adimensional.
- **Coherencia física** verificada en [`tests/test_modelo.py`](../tests/test_modelo.py):
  - en $t = \tau$ la corriente es el 63 % de $i_{max}$;
  - al desenergizar, la corriente decae a cero;
  - un conductor no magnético reduce $L$ y aumenta $R$; un ferromagnético a baja frecuencia aumenta $L$;
  - el efecto disminuye con la distancia;
  - un conductor perfecto da $\Gamma \to -1$;
  - el campo en el centro de una espira es $\mu_0 I/2a$.
- La energía disipada es siempre positiva ($\Delta R > 0$ para todo material), como exige la segunda ley.

## 3.7 Caso sin solución analítica: pieza en movimiento

Con $L(t)$ variable no hay fórmula cerrada. La referencia es `solve_ivp` con tolerancia $10^{-8}$. Con
40 pasos por ciclo, RK4 difiere de ella unos $10^{-5}$ A y Euler unos $4\times10^{-2}$ A, la misma relación que
en los casos con solución exacta. La envolvente de la corriente coincide con la curva cuasi-estática
$V_0/|Z(d(t))|$, lo que confirma que $\dot L\,i$ es despreciable a velocidades de banda normales.

## 3.8 Extensiones no implementadas

La guía aclara que Euler y RK4 bastan para modelos de EDO. Resolver directamente las ecuaciones de Maxwell en
3D (geometría finita de la pieza, núcleo de ferrita) requeriría diferencias finitas o elementos finitos. Aquí
esa parte se sustituye por la solución semianalítica de Dodd–Deeds, que reduce el problema a una integral en
una dimensión.
