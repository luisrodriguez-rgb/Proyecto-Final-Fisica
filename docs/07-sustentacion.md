# 7. Sustentación

> Criterio de la rúbrica: **Sustentación (10 %)**, claridad y dominio del proyecto.
> El profesor escoge qué integrante presenta, así que **todos** deben poder recorrer este guion.

## 7.1 Guion sugerido (10 minutos)

| Minuto | Tema | Apoyo |
|---|---|---|
| 0 – 1 | Problema: detectar metal sin contacto en una línea de producción | [Propuesta](enunciado/propuesta-sensor-inductivo.docx) |
| 1 – 3 | Física: Faraday → corrientes de Foucault → Lenz → cambian $L$ y $R$ | [Fundamentación](01-fundamentacion-fisica.md), diagrama |
| 3 – 5 | Modelo: Kirchhoff, misma deducción que el RC de clase, $\tau = L/R$, solución AC, $\Delta Z$ | [Modelamiento](02-modelamiento-analitico.md) |
| 5 – 8 | Demostración en vivo | [Guion de demo](05-simulacion.md#54-guion-para-mostrarlo-en-vivo) |
| 8 – 9 | Euler frente a RK4: órdenes 1 y 4, estabilidad $\Delta t < 2\tau$ | Pestaña Validación |
| 9 – 10 | Resultados, eficiencia y limitaciones frente a FEM | [Validación e impacto](06-validacion-e-impacto.md) |

## 7.2 Preguntas probables y respuestas cortas

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
