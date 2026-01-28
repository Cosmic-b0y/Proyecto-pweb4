# Investigación: Arquitectura de Software

## Contenido

Documento LaTeX/Overleaf que cubre:

1. **Requerimientos Funcionales**
2. **Requerimientos No Funcionales**  
3. **Arquitectura Hexagonal**
4. **Clean Architecture (Arquitectura Limpia)**
5. **Casos de Uso**

## Estructura del Documento

- Portada con datos del alumno
- Índice automático
- Introducción
- Desarrollo (5 temas)
- Metodología
- Conclusión
- Bibliografía (formato APA)
- Anexos con diagramas y tablas

## Cómo usar en Overleaf

1. Ir a [Overleaf](https://www.overleaf.com)
2. Crear nuevo proyecto → "Blank Project"
3. Subir el archivo `main.tex`
4. **Modificar los datos de la portada** (líneas 50-58):
   - `\nombreAlumno`
   - `\grupo`
   - `\numeroControl`
   - `\nombreDocente`
   - `\universidadNombre`
5. Subir el logo de la universidad como `logo_universidad.png`
6. Descomentar la línea del logo en la portada
7. Compilar con pdfLaTeX

## Personalización

Los datos de la portada se configuran en las líneas 50-58 del archivo `main.tex`.

## Compilación Local

```bash
pdflatex main.tex
pdflatex main.tex  # Segunda vez para índice
```
