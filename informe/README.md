# Informe escrito (plantilla del profesor)

Documento para entregar impreso, hecho con la plantilla de artículo a dos columnas que entregó el profesor.

| Archivo | Contenido |
|---|---|
| `informe.tex` | El informe: resumen, introducción, modelo teórico, implementación numérica, simulación, resultados y discusión, conclusiones, 16 referencias y las observaciones sobre IA y material complementario |
| `figuras/` | Figuras del proyecto (`modelo_teorico.png` es el diagrama del sistema; las demás son copias de `docs/figuras`) |
| `informe.pdf` | Versión compilada, lista para imprimir en tamaño carta |

## Compilar en Overleaf

1. **New Project → Upload Project** con un `.zip` de esta carpeta (`informe.tex` y `figuras/`).
2. Compilar con **pdfLaTeX**. La bibliografía está dentro del archivo (`thebibliography`), así que no hace falta BibTeX.

```bash
cd informe && zip -r ../informe-overleaf.zip informe.tex figuras
```

## Cambios respecto a la plantilla

- `babel` con las opciones `es-tabla` (las tablas se llaman "Tabla" y no "Cuadro") y `es-nodecimaldot` (punto
  decimal también dentro de las fórmulas).
- Un comando `\usoia{...}` para la declaración de uso de IA al final de cada apartado, como exige la plantilla.
- `\emergencystretch` para evitar líneas que se salen de la columna.
- La figura de convergencia usa los datos reales del proyecto con `pgfplots`.
