# Diseño del Pipeline ETL

## Objetivo

Construir un dataset final de películas a partir de archivos originales de IMDb.

## Archivos de entrada

- `data/raw/title.basics.tsv.gz`
- `data/raw/title.ratings.tsv.gz`

## Archivo de salida

- `data/final/movies_dataset.csv`

## Etapas

### Extract

Leer los archivos originales desde la carpeta `data/raw/` usando `pandas.read_csv` con `sep='\t'`, `na_values='\\N'` y `low_memory=False`.

### Transform

1. **Filtrar solo películas** — `titleType == 'movie'`
2. **Eliminar registros sin año** — `startYear` no nulo
3. **Eliminar registros sin duración** — `runtimeMinutes` no nulo
4. **Convertir año a número** — `startYear` a `int`
5. **Convertir duración a número** — `runtimeMinutes` a `int`
6. **Separar o limpiar géneros** — mantener como string separado por comas
7. **Unir películas con ratings** — merge por `tconst` (inner join)

### Validation

1. `tconst` no nulo
2. `startYear` numérico
3. `runtimeMinutes` numérico
4. `averageRating` entre 0 y 10
5. `numVotes` mayor o igual a 0

### Load

Guardar el dataset final en `data/final/movies_dataset.csv` con `index=False`.

## Columnas esperadas

| Columna | Tipo | Fuente |
|---|---|---|
| `tconst` | `object` | title.basics |
| `primaryTitle` | `object` | title.basics |
| `originalTitle` | `object` | title.basics |
| `isAdult` | `int64` | title.basics |
| `startYear` | `int64` | title.basics |
| `runtimeMinutes` | `int64` | title.basics |
| `genres` | `object` | title.basics |
| `averageRating` | `float64` | title.ratings |
| `numVotes` | `int64` | title.ratings |
