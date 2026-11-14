# Presentación (Beamer, plantilla Icesi)

Diapositivas de la sustentación con la plantilla que entregó el profesor.

| Archivo | Contenido |
|---|---|
| `presentacion.tex` | Las 22 diapositivas, con el mismo preámbulo, colores y pie de página de la plantilla |
| `logo_icesi.png` | Logo de la universidad |
| `figuras/` | Gráficas del proyecto (copias de `docs/figuras`) |
| `presentacion.pdf` | Versión compilada para revisar sin Overleaf |

## Subir a Overleaf

1. En Overleaf, **New Project → Upload Project** y subir un `.zip` con el contenido de esta carpeta
   (`presentacion.tex`, `logo_icesi.png` y la carpeta `figuras/`).
2. Compilar con **pdfLaTeX** (el compilador por defecto).

Para armar el `.zip` desde la raíz del repositorio:

```bash
cd presentacion && zip -r ../presentacion-overleaf.zip presentacion.tex logo_icesi.png figuras
```

Si el proyecto de Overleaf ya existe, basta con reemplazar el contenido de `formato presentación.tex` por el de
`presentacion.tex` y subir la carpeta `figuras/`.

## Estructura

Sigue las secciones de la plantilla, con el modelo teórico organizado según el esquema D.E.P.A. del profesor:

1. Portada y contenido
2. Introducción
3. Modelo teórico: esquema D.E.P.A., variables y supuestos, representación del campo, formalismo (Maxwell,
   circuito RL, efecto de la pieza) y caso de estudio
4. Implementación numérica: Euler y RK4, procedimiento computacional y convergencia
5. Simulación computacional: modelo de simulación, parámetros y escenarios, identificación del material
6. Resultados y discusión
7. Conclusiones, referencias, material complementario y cierre

## Regenerar las figuras

Las figuras salen del código del proyecto. Si cambia el modelo:

```bash
.venv/bin/python scripts/generar_figuras.py
cp docs/figuras/*.png presentacion/figuras/
```
