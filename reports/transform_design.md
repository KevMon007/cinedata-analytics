# Diseño de Transformación

## Objetivo

Limpiar y preparar los datos extraídos de IMDb para construir el dataset final de películas.

Esta etapa recibe los DataFrames crudos de Extract y devuelve un solo DataFrame limpio, listo para validación y carga.

## Archivos de Entrada

- `title.basics.tsv.gz` → `DataFrame` con 9 columnas
- `title.ratings.tsv.gz` → `DataFrame` con 3 columnas

## Reglas de Limpieza

### title.basics

| Regla | Justificación |
|---|---|
| Conservar solo `titleType == "movie"` | El proyecto solo analiza películas. Se descartan series, cortos, documentales, etc. |
| Eliminar registros sin `startYear` | Una película sin año de estreno no es útil para el análisis temporal. |
| Eliminar registros sin `runtimeMinutes` | Sin duración no se puede analizar distribución ni filtrar por metraje. |
| Filtrar `startYear` entre 1900 y 2030 | Rangos configurables vía `.env`. Valores fuera de rango suelen ser errores de datos. |
| Filtrar `runtimeMinutes` entre 1 y 500 | Rangos configurables. Duraciones extremas (>500 min) son casos atípicos o errores. |
| Rellenar `genres` nulos con `"Unknown"` | El género no es crítico para la existencia de la película. Se prefiere conservar el registro. |
| Convertir `startYear` y `runtimeMinutes` a `int` | Operaciones numéricas requieren tipo entero. |
| Limpiar espacios en textos | Normalización de strings. |
| Eliminar duplicados por `tconst` | Cada identificador debe ser único. |

### title.ratings

| Regla | Justificación |
|---|---|
| Eliminar registros sin `tconst` | No se puede asociar la calificación a ninguna película. |
| Eliminar registros sin `averageRating` o `numVotes` | Datos incompletos no aportan valor. |
| Filtrar `averageRating` entre 0 y 10 | Rango oficial de IMDb. |
| Filtrar `numVotes` >= 0 | No existen votos negativos. |
| Eliminar duplicados por `tconst` | Una sola calificación por película. |
| Convertir `numVotes` a `int` | Tipo numérico entero. |

### Merge

- **Tipo**: Inner join por `tconst`
- **Justificación**: Solo interesan películas que tengan calificación. Las películas sin rating se descartan.

## Columnas del Dataset Final

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

## Validaciones Internas

- Se valida que las columnas requeridas existan antes de procesar.
- Si después de filtrar no quedan registros, se retorna un DataFrame vacío con las columnas correctas.
- Si el merge no encuentra coincidencias, se retorna un DataFrame vacío con las columnas finales.

## Rangos Configurables

| Variable | Default | Archivo |
|---|---|---|
| `MIN_YEAR` | 1900 | `.env` |
| `MAX_YEAR` | 2030 | `.env` |
| `MIN_RUNTIME` | 1 | `.env` |
| `MAX_RUNTIME` | 500 | `.env` |
| `MIN_NUM_VOTES` | 0 | `.env` |

## Criterio de Cierre

La fase Transform se considera cerrada cuando:

- Las reglas de limpieza están implementadas y probadas.
- Los rangos configurables pueden modificarse vía `.env`.
- Los DataFrames vacíos se manejan sin errores.
- Las pruebas cubren:
  - Filtrado correcto de películas
  - Eliminación de nulos
  - Rangos de año y duración
  - Géneros nulos convertidos a "Unknown"
  - Duplicados eliminados
  - Merge con y sin coincidencias
  - Error claro si faltan columnas
