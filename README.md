# Simulador de sensor electromagnético de proximidad

Simulador interactivo (Streamlit + Plotly + Matplotlib) de un sensor inductivo: una bobina RL
alimentada con V₀·sin(ωt) cuya inductancia y resistencia cambian cuando se acerca un objeto metálico.
Incluye alimentación alterna o escalón DC y tema claro u oscuro.

**Informe completo, organizado por los criterios de la rúbrica: [`docs/`](docs/README.md).**

## Ejecutar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py
```

Pruebas (orden de convergencia, límites físicos, campo de una espira):

```bash
.venv/bin/python -m pytest -q tests
```

## Estructura

| Archivo | Contenido |
|---|---|
| `sensor/physics.py` | L₀ (Wheeler), modelo de corrientes de Foucault de **Dodd–Deeds** (ΔZ por integral de Bessel), profundidad de penetración δ, campo B por integrales elípticas + método de imágenes |
| `sensor/numerics.py` | **Euler y RK4 a mano**, solución exacta, `solve_ivp`, estudio de convergencia (orden observado), simulación con L(t) variable, demodulador y comparador con histéresis |
| `sensor/symbolic.py` | Deducción con **SymPy**: `dsolve` de la EDO RL, régimen permanente, Z, φ, τ, energía, potencia y sensibilidades ∂Iₚ/∂L, ∂Iₚ/∂R |
| `app.py` | Interfaz con 7 pestañas |
| `ui.py` | Temas claro/oscuro, plantilla de gráficas y componentes visuales |
| `scripts/generar_figuras.py` | Figuras del informe en `docs/figuras` |
| `tests/test_modelo.py` | Pruebas automáticas |
| `docs/` | Informe por criterio de la rúbrica, enunciado y figuras |

## Pestañas de la app → rúbrica

1. **Modelo** – ΔL y ΔR vs distancia para 5 materiales, curva de detección y distancia de conmutación Sₙ, ΔL vs frecuencia (el acero cambia de signo: magnetización vs. apantallamiento). *(Desarrollo analítico)*
2. **Respuesta temporal** – I(t): exacta, RK4, Euler y SciPy; en alterna con banda de umbral y en escalón DC con i_max y el 63 % en t = τ; aviso de inestabilidad de Euler (Δt > 2τ); energía y potencia. *(Simulación)*
3. **Paso del objeto** – objeto que se acerca y aleja: resuelve dI/dt = [V − (R + L̇)I]/L con L(t), envolvente demodulada, umbral ON/OFF con histéresis y salida digital. *(Respuesta transitoria ante variación de L)*
4. **Campo** – mapa de líneas de B y |B| con la pieza y δ; perfil axial B_z con y sin objeto.
5. **Validación numérica** – error vs Δt en log-log con pendientes 1 y 4, orden observado, tabla de error absoluto y relativo (descargable en CSV). *(Análisis numérico)*
6. **Derivación (SymPy)** – deducción simbólica y verificación del residuo = 0.
7. **Análisis** – lectura física del caso, tabla comparativa de materiales, velocidad máxima de banda / piezas por minuto, limitaciones frente a FEM. *(Validación e impacto)*

## Modelo

- L₀ = μ₀N²πa² / (l + 0.9a)  (la fórmula ideal μ₀N²A/l sobreestima un 67.5 % en esta bobina corta)
- ΔZ = jωπμ₀a²N² ∫ J₁²(αa) Γ(α) F²(α) dα,  F = (e^{−αd} − e^{−α(d+l)})/(αl),
  Γ = (μᵣα − α₁)/(μᵣα + α₁),  α₁ = √(α² + jωμ₀μᵣσ)
- L_eff = L₀ + Im(ΔZ)/ω,  R_eff = R₀ + Re(ΔZ)
- Detección: |Iₚ − Iₚ,₀| / Iₚ,₀ ≥ umbral

Referencia: C. V. Dodd & W. E. Deeds, *Analytical solutions to eddy-current probe-coil problems*,
J. Appl. Phys. 39, 2829 (1968).
