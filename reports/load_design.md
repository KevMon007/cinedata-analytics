# Diseño de la fase Load

## Objetivo

Guardar el dataset final validado del pipeline ETL en un archivo consumible por las siguientes etapas del proyecto.

## Entrada

La fase recibe un `DataFrame` ya transformado y validado con las columnas finales:

- `tconst`
- `primaryTitle`
- `originalTitle`
- `isAdult`
- `startYear`
- `runtimeMinutes`
- `genres`
- `averageRating`
- `numVotes`

## Salida principal

- `data/final/movies_dataset.csv`

La ruta puede configurarse con las variables `FINAL_DATA_PATH` y `FINAL_DATASET_FILE`.

## Reglas de carga

1. Crear la carpeta destino si no existe.
2. Guardar el archivo CSV con `index=False`.
3. Usar codificación `utf-8`.
4. No modificar los datos durante la carga.

## Implementación

La función principal es `load_csv()` en `src/etl/load.py`.

El pipeline completo la ejecuta desde `src/etl/pipeline.py` después de la validación del dataset final.

## Decisiones

Por ahora la carga oficial del ETL es a CSV porque el dataset final se usa como entrada para análisis, modelado y visualización.

Las variables de base de datos en `.env.example` quedan reservadas para una futura extensión, pero no forman parte del alcance actual de `Load`.

## Pruebas

La fase se valida con:

- `tests/test_load.py`: prueba la creación del archivo CSV y que no se guarde índice.
- `tests/test_pipeline.py`: prueba el flujo completo Extract, Transform, Validation y Load con archivos temporales.
