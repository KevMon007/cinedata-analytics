# Diseño de la fase de aprendizaje no supervisado

## Objetivo

Agrupar peliculas por similitud usando K-Means sobre el dataset final generado por el ETL.

## Entrada

- `data/final/movies_dataset.csv`

## Features

La fase usa las siguientes variables numericas:

- `startYear`
- `runtimeMinutes`
- `averageRating`
- `logNumVotes`

`logNumVotes` se deriva de `numVotes` usando `log10(numVotes + 1)` para reducir el efecto de escala de la popularidad.

Tambien se agregan columnas interpretativas:

- `decade`
- `mainGenre`
- `genreCount`

## Seleccion de k

Por defecto se evalua `k=2..10` con:

- `inertia`
- `silhouette_score`

El valor final de `k` se selecciona automaticamente usando el mayor `silhouette_score`.

Tambien puede fijarse manualmente:

```bash
python -m src.models.run_clustering --k 5
```

## Salidas

- `data/final/movies_clustered.csv`
- `models/kmeans_model.joblib`
- `reports/tables/kmeans_evaluation.csv`
- `reports/tables/cluster_summary.csv`
- `reports/tables/cluster_top_movies.csv`
- `reports/figures/kmeans_elbow.png`
- `reports/figures/kmeans_silhouette.png`
- `reports/figures/cluster_distribution.png`
- `reports/figures/cluster_rating_runtime.png`
- `reports/clustering_report.md`

## Interpretacion

Cada cluster se resume con:

- cantidad de peliculas
- rating promedio
- duracion promedio
- anio promedio
- mediana de votos
- genero principal
- distancia promedio al centroide

## Uso posterior

El dataset clusterizado queda listo para alimentar recomendaciones y reemplazar datos estaticos del dashboard.
