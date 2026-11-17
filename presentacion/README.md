# Presentación (Beamer, plantilla Icesi)

Diapositivas de la sustentación con la plantilla que entregó el profesor.

| Archivo | Contenido |
|---|---|
| `presentacion.tex` | Las 25 diapositivas, con el mismo preámbulo, colores y pie de página de la plantilla |
| `logo_icesi.png` | Logo de la universidad |
| `figuras/` | Gráficas del proyecto, escena 3D y figura de Anatomy (copias de `docs/figuras`) e imágenes de apoyo generadas con IA (`ia-*.jpg`, convertidas desde `docs/figuras/ia`) |
| `guion.pdf` / `guion.tex` | Guion completo de 15 minutos: texto para decir en cada diapositiva, tiempos, opcionales y explicaciones en letra pequeña |
| `guion.md` | Resumen de bolsillo del guion: ideas clave, números y preguntas |
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

Caso principal: la espira de parqueadero que reconoce un Chevrolet Spark GT y un Renault Kwid. Sigue las secciones
de la plantilla, con el modelo teórico organizado según el esquema D.E.P.A.:

1. Portada, contenido e introducción
2. Modelo teórico: D.E.P.A., qué pasa físicamente, representación del sistema, caso de estudio y formalismo
   (Maxwell necesario, inductancia y chasis, oscilador LC)
3. Implementación numérica: Euler y RK4 como sistema, convergencia, Euler explota en el oscilador, la simulación
   corrigió la fórmula
4. Simulación: escena 3D, lo que mide el detector, el carro cruzando, escenarios de diseño, segundo escenario
   (identificación del material)
5. Resultados, discusión, conclusiones, referencias, material complementario y cierre

Las imágenes generadas con IA llevan su crédito en la diapositiva, como pide la guía.

## Regenerar las figuras

Las figuras salen del código del proyecto. Si cambia el modelo:

```bash
.venv/bin/python scripts/generar_figuras.py
cp docs/figuras/*.png presentacion/figuras/
```
