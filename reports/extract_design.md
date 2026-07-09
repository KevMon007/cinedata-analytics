# Diseño de Extracción

## Objetivo

Definir y probar la etapa **Extract** del proyecto antes de avanzar a transformación, validación y carga.

Esta etapa solo debe leer datos originales. No debe limpiar, transformar ni guardar datos.

## Archivos Fuente

- `data/raw/title.basics.tsv.gz`
- `data/raw/title.ratings.tsv.gz`

## Formato Esperado

- Formato: TSV comprimido con gzip (`.tsv.gz`)
- Separador: tabulación (`\t`)
- Nulos IMDb: `\N`
- Lectura: `pandas.read_csv(..., sep="\t", na_values="\\N", low_memory=False)`

## Columnas Esperadas

### title.basics.tsv.gz

- `tconst`
- `titleType`
- `primaryTitle`
- `originalTitle`
- `isAdult`
- `startYear`
- `endYear`
- `runtimeMinutes`
- `genres`

### title.ratings.tsv.gz

- `tconst`
- `averageRating`
- `numVotes`

## Validaciones De Extract

La etapa de extracción valida:

- Que el archivo exista.
- Que el archivo no esté vacío.
- Que `\N` sea interpretado como valor nulo.
- Que los archivos IMDb oficiales contengan las columnas esperadas.

## Errores Controlados

- `DataFileNotFoundError`: el archivo no existe.
- `EmptyDataFileError`: el archivo está vacío o no contiene datos legibles.
- `MissingColumnsError`: faltan columnas mínimas esperadas.

## Decisiones Técnicas

- La función genérica `extract_tsv_gz()` puede leer cualquier archivo TSV.GZ.
- Las funciones `load_title_basics()` y `load_title_ratings()` agregan validación de columnas específicas de IMDb.
- El módulo `explorer` reutiliza la misma lectura del ETL para evitar lógica duplicada.

## Criterio De Cierre

La fase Extract se considera cerrada cuando:

- Las funciones de lectura están probadas.
- Los errores esperados tienen mensajes claros.
- Los archivos IMDb pueden leerse correctamente desde `data/raw/`.
- La documentación de extracción está actualizada.
