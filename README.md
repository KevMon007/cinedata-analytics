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
2. Ejecutar notebooks en orden dentro de `notebooks/`
3. Para levantar la web: `python web/app.py`
