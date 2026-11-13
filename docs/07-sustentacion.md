# 7. Sustentación

> Criterio de la rúbrica: **Sustentación (10 %)**, claridad y dominio del proyecto.
> El profesor escoge qué integrante presenta, así que **todos** deben poder recorrer este guion.

## 7.1 Guion sugerido (15 minutos)

| Minuto | Tema | Apoyo |
|---|---|---|
| 0 – 1.5 | El problema: abrir la talanquera de un parqueadero y saber qué carro llegó, sin cámaras ni botones. Esquema D.E.P.A. | Imagen de portada, [00 · Modelo teórico](00-modelo-teorico-depa.md) |
| 1.5 – 4 | Física: Faraday → corrientes de Foucault en el chasis → Lenz → la inductancia de la espira baja. Por qué a 55 kHz el acero baja $L$ (δ = 0.087 mm). Solo Faraday y Ampère | Figura de Anatomy, [01 · Fundamentación](01-fundamentacion-fisica.md) |
| 4 – 7 | Modelo: inductancia de la espira (83 µH), chasis como placa (Dodd–Deeds), Kirchhoff en la malla LC (como el RC de clase) → $f_0$ = 55.25 kHz; cambio exacto de frecuencia | [02 · Modelamiento](02-modelamiento-analitico.md), sección 2.10 |
| 7 – 10.5 | Demostración en vivo: escena 3D con el Spark y el Kwid, oscilador LC, figura del corte | [Guion de demo](05-simulacion.md#54-guion-para-mostrarlo-en-vivo) |
| 10.5 – 12.5 | Métodos numéricos: Euler frente a RK4 (órdenes 1 y 4), Euler explota en el oscilador; la simulación corrigió la fórmula de frecuencia | Pestaña Validación y oscilador LC, [03](03-metodos-numericos.md) |
| 12.5 – 14 | Resultados: Spark 59.18 kHz, Kwid 58.69 kHz, reconocidos por altura; eficiencia, impacto y escenarios de diseño | [05](05-simulacion.md), [06](06-validacion-e-impacto.md) |
| 14 – 15 | Limitaciones (chasis como placa, carga del carro, FEM) y cierre | [06](06-validacion-e-impacto.md), sección 6.4 |

Si sobra tiempo o el profesor pregunta por la identificación de materiales, mostrar el segundo escenario (pestaña
**Identificación**, bobina de autopartes).

**Frase para abrir (caso del carro):** "SEMP es una espira en el piso de un parqueadero. Cuando un carro se para
encima, su chasis de acero baja la inductancia de la espira; el detector lo nota como un cambio de frecuencia, abre
la talanquera y, por cuánto cambió, sabe si es un Spark o un Kwid."

**Frase para cerrar:** "Con las leyes de Faraday y Ampère, la ley de mallas que vimos en clase y RK4 programado a
mano, el detector reconoce un Spark (59.18 kHz) y un Kwid (58.69 kHz) por la altura de su chasis. El modelo da el
máximo posible del efecto; un análisis por elementos finitos con el chasis real daría el valor exacto."

**Frase alternativa (autopartes):** "SEMP es un sensor para una línea de autopartes. Siguiendo el esquema D.E.P.A., detecta la
pieza, mide cómo responde al campo, usa la frecuencia para saber de qué metal es y la potencia para saber a qué
distancia está, y entrega una alerta."

## 7.2 Preguntas probables y respuestas cortas

**¿Cómo identifica el sensor el material?**
Por la fase del cambio de impedancia. Los conductores no magnéticos dan fase negativa (cerca de −80° el cobre,
−49° el inoxidable) y el acero da fase positiva. La magnitud del cambio da la distancia.

**¿Cómo detecta una impureza?**
Si la medición no cae cerca de ninguna curva de material conocido, el residuo crece y la alerta avisa. Su límite:
un cobre con el 60 % de su conductividad es indistinguible del aluminio, porque el sensor solo ve σ y μᵣ.

**¿Por qué solo usan Faraday y Ampère?**
Porque son las que contienen la física del sensor. Gauss magnética solo da una condición de frontera, Gauss
eléctrica no interviene porque no se acumula carga, y la corriente de desplazamiento es despreciable.


**¿Qué ecuación de Maxwell explica el sensor?**
La ley de Faraday. El campo variable de la bobina induce un campo eléctrico en la pieza, que mueve las
corrientes de Foucault. Ampère–Maxwell da el campo de esas corrientes, y Gauss magnética ($\nabla\cdot\vec B = 0$)
da la continuidad de $B_z$ en la superficie.

**¿Por qué baja la inductancia con el cobre y sube con el acero?**
En el cobre las corrientes inducidas crean un campo opuesto (Lenz) que expulsa flujo. El acero, además, se
magnetiza ($\mu_r = 100$) y concentra el flujo. A baja frecuencia gana la magnetización; a alta frecuencia la
corriente queda en una capa muy delgada y gana el apantallamiento.

**¿Por qué se desprecia la corriente de desplazamiento?**
Porque en el metal $\omega\varepsilon_0/\sigma \approx 10^{-18}$ y en el aire la longitud de onda (300 km)
es enorme frente a la bobina.

**¿Qué es la profundidad de penetración?**
La distancia en la que el campo y las corrientes inducidas caen un factor $e$ dentro del metal:
$\delta = \sqrt{2/\omega\mu\sigma}$. Para cobre a 1 kHz son 2 mm.

**¿Cómo se relaciona con lo visto en clase?**
La malla RL se resuelve igual que la carga del capacitor: Kirchhoff, separación de variables, $\tau$ y el
63 %. La inductancia se define como $C$: flujo enlazado entre corriente, en lugar de carga entre potencial.
La detección es la misma idea de la pantalla táctil capacitiva: medir $\Delta L$ en vez de $\Delta C$.

**¿Por qué RK4 es mejor si hace cuatro veces más cálculos por paso?**
Porque su error baja con $h^4$. Al dividir el paso entre 2, Euler gana un factor 2 y RK4 un factor 16. Para
el 1 % de error, Euler necesita unos 160 pasos por ciclo y RK4 diez.

**¿Cuándo falla Euler?**
Cuando $\Delta t > 2\tau$: cada paso multiplica el error por $|1 - \Delta t/\tau| > 1$ y la solución diverge.
Se puede mostrar en vivo bajando la frecuencia a 100 Hz.

**¿Qué pasa si la pieza se mueve?**
$L$ depende del tiempo y aparece el término $\dot L\, i$. No hay solución cerrada, así que se compara RK4
con SciPy. A velocidades normales ese término es despreciable.

**¿Por qué no se detecta el acero inoxidable con el umbral del 2 %?**
Porque la bajada de $L$ y la subida de $R$ se compensan en la amplitud de la corriente. Los sensores reales
miden pérdidas (oscilador LC); ordenando por $\Delta R$, el modelo reproduce el orden de los fabricantes.

**¿Qué limita al modelo?**
Supone una pieza infinita, una bobina sin núcleo y materiales lineales. Un análisis por elementos finitos
resolvería la geometría real, pero tardaría minutos por punto.

**¿Por qué el carro baja la inductancia si el acero es magnético?**
Porque a 55 kHz el campo entra solo 0.09 mm en el acero: las corrientes de Foucault dominan y apantallan el
campo. La magnetización solo gana a frecuencias bajas, como vimos con la frecuencia ciega del acero.

**¿Cómo distingue el Spark del Kwid?**
Por la altura del chasis: el Spark (15 cm) queda más cerca de la espira que el Kwid (18 cm) y la baja más
(−12.9 % frente a −11.4 %). La carga del carro puede reducir esa diferencia; por eso conviene sumar el largo o el peso.

**¿Los parqueaderos de verdad funcionan así?**
Sí, las espiras inductivas son el detector más usado en talanqueras y semáforos. Los valores de nuestro modelo
son una cota superior porque el chasis real no es una placa plana.

**¿Por qué el detector usa un capacitor?**
Para formar un oscilador LC: su frecuencia $f = 1/2\pi\sqrt{LC}$ depende de la inductancia, y una frecuencia se mide
con mucha precisión contando ciclos. Es la unión del RC de clase y el RL del proyecto: Kirchhoff en la malla da
$L\ddot q + R\dot q + q/C = 0$.

**¿Por qué no usaron Δf/f = −½ ΔL/L?**
Porque es una aproximación para cambios pequeños. Con el Spark la inductancia baja 12.9 %, y la aproximación da
+6.4 % cuando el cambio real es +7.1 %. Lo descubrimos simulando el oscilador con RK4: la frecuencia simulada
coincidía con la fórmula exacta $(1 + \Delta L/L)^{-1/2}$ y no con la aproximada.

**¿Por qué Euler explota en el oscilador si en el circuito RL funcionaba?**
En el RL el valor propio es real y negativo, y Euler es estable si $\Delta t < 2\tau$. En el oscilador los valores
propios son imaginarios, y cada paso de Euler multiplica la amplitud por $\sqrt{1 + (\omega\Delta t)^2} > 1$: la
energía crece con cualquier paso. Con 40 pasos por período se multiplica por $10^{11}$ en 30 períodos.

**¿Qué pasa si el Kwid va cargado?**
Baja un par de centímetros. Si llega a 16 cm, su cambio de inductancia se parece al del Spark y el detector se
equivoca. Para evitarlo se puede sumar el largo del carro con una segunda espira.

**¿Por qué no usar una cámara?**
La espira no le teme a la lluvia, la noche ni la suciedad, no tiene partes expuestas y no guarda imágenes de nadie.
La cámara sí reconoce el modelo exacto, pero es más frágil y costosa de mantener.

**¿El campo de la espira es peligroso?**
No: es de unos 0.09 µT, cientos de veces menor que el campo de la Tierra.

## 7.3 Más preguntas, ligadas a los temas de clase

**¿Qué tiene que ver la ley de Gauss con un sensor magnético?**
Dos cosas. El flujo se calcula igual, $\Phi_B = \vec B\cdot\vec A$, y con él se deduce la inductancia. Y la
versión magnética, $\oint\vec B\cdot d\vec A = 0$, da la condición de frontera en la superficie del metal: la
componente del campo perpendicular a la superficie no puede saltar.

**¿En qué se parece la inductancia a la capacitancia?**
Las dos son una razón que depende solo de la geometría: $C = Q/\Delta V$ (carga por voltio) y $L = \Lambda/i$
(flujo por amperio). Por eso en las dos el número de espiras o el área de las placas importan, y la carga o la
corriente no.

**¿Por qué el acero se comporta distinto, si en clase vimos que los dieléctricos reducen el campo?**
Porque un dieléctrico tiene dipolos eléctricos que se orientan **contra** el campo, y un ferromagnético tiene
dipolos magnéticos que se orientan **a favor**. El primero reduce el campo ($E/K_d$) y el segundo lo refuerza
($\mu_r B$).

**¿La bobina es un dipolo como el que vimos?**
Sí, vista de lejos es un dipolo magnético $m = Ni\pi a^2$ y su campo cae como $1/z^3$, igual que el dipolo
eléctrico de clase. Eso explica por qué el alcance del sensor es del orden de su radio.

**¿Se conserva la energía en el circuito?**
Sí. Multiplicando la ecuación de Kirchhoff por $i$ queda: potencia de la fuente = calor en $R$ + ritmo de cambio de
$\tfrac12Li^2$. Lo verificamos numéricamente con un error de $5\times10^{-7}$.

**¿Por qué con 100 espiras no detecta nada?**
Porque el factor de calidad $Q = \omega L/R$ es muy bajo: la corriente la limita casi solo la resistencia, y un
cambio en $L$ no se nota. Con 300 espiras la señal se triplica.

**¿Qué es la frecuencia ciega del acero?**
Una frecuencia, cerca de 20 kHz, en la que la magnetización y las corrientes de Foucault se cancelan y el acero no
cambia la inductancia. Un sensor que trabajara ahí no lo vería.

**¿Euler sirve para algo?**
Sí, para entender el método y para problemas donde se necesita algo rápido y aproximado. Pero para un error del
1 % necesita unas 16 veces más pasos que RK4, y se vuelve inestable si $\Delta t > 2\tau$.

**¿Cómo saben que el código está bien?**
Por cuatro caminos independientes: la comparación con la solución exacta, el orden de convergencia medido (1.01 y
4.02), la conservación de la energía y el ejercicio RC de clase, que da los resultados conocidos con el mismo código.

## 7.4 Errores comunes que hay que evitar al exponer

- Decir que el metal "atrae" el campo en general. Solo el ferromagnético lo concentra; el cobre lo **expulsa**.
- Confundir $\tau = L/R$ con $\tau = RC$ al hacer la analogía: en el RL la resistencia va en el denominador.
- Decir que RK4 es "4 veces mejor". Es de **orden** 4: al dividir el paso entre 2 el error baja 16 veces.
- Presentar el modelo como exacto. Supone una pieza infinita (en el carro, un chasis plano) y una bobina sin núcleo,
  y conviene decirlo antes de que pregunten.
- Usar $\Delta f/f = -\tfrac12\Delta L/L$ para el carro: con cambios de más del 10 % hay que usar la fórmula exacta.
- Decir que el acero siempre sube la inductancia. A 55 kHz la baja, porque el campo casi no entra en él.
- Decir que el detector mide el campo magnético. Mide una frecuencia; el campo es demasiado débil para medirlo
  directamente.

## 7.5 Lista para el día de la sustentación

- [ ] Simulador abierto y probado en el computador de la exposición (`.venv/bin/streamlit run app.py`).
- [ ] Pestaña **Caso: vehículo** abierta con el Spark, la espira de 1.8 m y 3 vueltas; la escena 3D corriendo.
- [ ] Probar la escena 3D en el computador de la exposición: funciona sin internet, pero necesita WebGL.
- [ ] Para el segundo escenario, parámetros de referencia: cobre, 5 mm, 1 kHz, 150 espiras.
- [ ] Imágenes de [`figuras/ia/`](figuras/ia/) citadas como generadas con IA en las diapositivas.
- [ ] Figuras de [`figuras/`](figuras/) a mano por si falla el computador.
- [ ] Cada integrante practicó el guion completo al menos una vez.
- [ ] Nombres del equipo y reflexión sobre la IAG completados en [08-uso-de-iag.md](08-uso-de-iag.md).
