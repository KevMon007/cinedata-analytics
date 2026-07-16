# CineData Analytics

Proyecto de análisis de datos de películas. Extracción, limpieza, modelado y visualización de datos cinematográficos.

## Estructura del proyecto

```
peliculas-proyecto/
├── data/               # Datos raw, processed y final
├── notebooks/          # Notebooks de Jupyter (EDA, limpieza, modelado)
├── src/                # Código fuente (extracción, limpieza, modelos, utilerías)
├── web/                # Aplicación web (Flask/FastAPI)
├── reports/            # Reportes, gráficas y presentaciones
└── tests/              # Pruebas unitarias
```

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

1. Colocar los datos crudos en `data/raw/`
2. Ejecutar el ETL: `python -m src.etl.pipeline`
3. Revisar el dataset final en `data/final/movies_dataset.csv`
4. Ejecutar el EDA: `python -m src.analysis.run_eda`
5. Revisar tablas, figuras y reporte en `reports/`
6. Ejecutar notebooks en orden dentro de `notebooks/`
7. Para levantar la web: `python web/app.py`

## Pipeline ETL

El pipeline toma los archivos IMDb `title.basics.tsv.gz` y `title.ratings.tsv.gz`, filtra solo películas, limpia tipos y rangos, valida el resultado y guarda el dataset final en CSV.

Documentación por etapa:

- `reports/extract_design.md`
- `reports/transform_design.md`
- `reports/load_design.md`
- `reports/eda_report.md`
