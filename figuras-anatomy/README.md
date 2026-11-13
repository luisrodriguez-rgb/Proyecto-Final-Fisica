# Figuras con Anatomy

Figuras isométricas hechas con la skill [Anatomy](https://github.com/wheresryan22/anatomy) (licencia MIT). El kit
necesario está copiado en `kit/` para que la figura se pueda reconstruir desde el repositorio.

## Fig 1 · Detector de espira bajo un Spark y un Kwid (`corte-espira/`)

Corte del pavimento por el centro de la espira: ranura con 3 vueltas de alambre y sellante, cable de conexión a la
caja de paso y al detector, chasis de acero a la altura del Spark (15 cm) o del Kwid (18 cm), corrientes de
Foucault y líneas de campo. Al pasar el cursor (o con las flechas) se cambia de carro y la lectura muestra ΔL/L y
la frecuencia del oscilador, tomadas de `sensor/vehiculo.py`.

```bash
cd figuras-anatomy/corte-espira
node build.mjs           # tema oscuro  -> corte-espira.html
node build.mjs --light   # tema claro   -> corte-espira-light.html
node build.mjs --audit   # verificación de geometría
```

Capturas para el informe: `docs/figuras/anatomy-corte-espira.png` (claro) y `anatomy-corte-espira-oscuro.png`.

Limitaciones: el campo de la figura es un modelo 2D en el plano del corte con el acero como conductor perfecto
(muestra la tendencia, no los valores de Dodd–Deeds); las corrientes de Foucault se dibujan en la cara superior
del chasis porque la vista isométrica no muestra la inferior; ancho de ranura, alambres y espesor de lámina están
agrandados para que se vean.
