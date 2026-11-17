// Números del modelo de Python (sensor/vehiculo.py, sensor/physics.py). No se recalculan aquí: se copian
// tal como los entrega el modelo de Dodd–Deeds para que la figura y el informe digan lo mismo.
//   Espira cuadrada de 1.8 m, 3 vueltas de alambre 14 AWG, ranura de 5 cm, C = 0.10 µF.
//   L0 = mu0 N^2 a [ln(8a/r_w) - 2] = 83.0 µH,  f0 = 1/(2 pi sqrt(L0 C)) = 55.2 kHz.
//   Con el carro centrado: f/f0 = (1 + dL/L0)^(-1/2) (fórmula exacta del oscilador LC).
export const ESPIRA = { lado: 180, vueltas: 3, ranura: { ancho: 0.6, profundidad: 5 }, L0_uH: 83.0, f0_kHz: 55.2 };
export const DELTA_ACERO_MM = 0.087;
export const CARROS = [
  { id: "spark", nombre: "Spark", completo: "Chevrolet Spark GT", altura: 15, dLrel: -12.9, f_kHz: 59.2 },
  { id: "kwid", nombre: "Kwid", completo: "Renault Kwid", altura: 18, dLrel: -11.4, f_kHz: 58.7 },
];
export const lectura = (c) => `${c.nombre} · ${c.altura} cm · ΔL/L ${c.dLrel.toFixed(1).replace("-", "−")} % · ${c.f_kHz.toFixed(1)} kHz`;
