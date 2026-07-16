# Reporte de Clustering

## Objetivo

Agrupar peliculas por similitud usando K-Means sobre el dataset final del ETL.

## Configuracion

- Features usadas: `startYear, runtimeMinutes, averageRating, logNumVotes`
- Escalado: `StandardScaler`
- Evaluacion de k: `2..10` por defecto
- k seleccionado: `5`
- Seleccion: automatica por silhouette_score
- Silhouette score del k seleccionado: `0.2791`

## Resumen de clusters

| cluster | cantidad | rating_promedio | duracion_promedio | anio_promedio | votos_mediana | log_votos_promedio | distancia_promedio | genero_principal |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 92551 | 7.18 | 82.35 | 2011.92 | 28.0 | 1.53 | 1.07 | Documentary |
| 1 | 51880 | 6.44 | 103.93 | 2005.53 | 2505.0 | 3.54 | 1.28 | Drama |
| 2 | 28449 | 6.63 | 143.05 | 2001.91 | 79.0 | 1.99 | 1.59 | Drama |
| 3 | 67148 | 5.96 | 84.59 | 1957.35 | 55.0 | 1.85 | 1.26 | Drama |
| 4 | 71960 | 4.51 | 90.76 | 2009.17 | 126.0 | 2.06 | 1.17 | Comedy |

## Hallazgos principales

- El cluster mas grande es `0` con 92,551 peliculas.
- `logNumVotes` se usa para reducir el efecto de escala de `numVotes`.
- Los clusters deben interpretarse con sus promedios, genero principal y peliculas mas votadas.

## Peliculas destacadas por cluster

| cluster | primaryTitle | startYear | averageRating | numVotes |
| --- | --- | --- | --- | --- |
| 0 | Chhava | 2024 | 8.4 | 2277 |
| 0 | Secrets of Sinauli | 2021 | 8.9 | 2254 |
| 0 | Marilena from P7 | 2006 | 7.8 | 2122 |
| 0 | The Beatles: Get Back - The Rooftop Concert | 2022 | 8.9 | 2014 |
| 0 | Space Station 3D | 2002 | 7.4 | 1809 |
| 1 | The Shawshank Redemption | 1994 | 9.3 | 3201987 |
| 1 | The Dark Knight | 2008 | 9.1 | 3182754 |
| 1 | Inception | 2010 | 8.8 | 2829291 |
| 1 | Fight Club | 1999 | 8.8 | 2623111 |
| 1 | Interstellar | 2014 | 8.7 | 2550065 |
| 2 | Zack Snyder's Justice League | 2021 | 7.9 | 475155 |
| 2 | Once Upon a Time in America | 1984 | 8.3 | 409160 |
| 2 | Seven Samurai | 1954 | 8.6 | 402857 |
| 2 | Gone with the Wind | 1939 | 8.2 | 356405 |
| 2 | Lawrence of Arabia | 1962 | 8.3 | 342481 |
| 3 | The Cabinet of Dr. Caligari | 1920 | 8.0 | 76422 |
| 3 | Sherlock Jr. | 1924 | 8.1 | 66161 |
| 3 | The Circus | 1928 | 8.1 | 38667 |
| 3 | The Mummy | 1932 | 6.9 | 33442 |
| 3 | Man with a Movie Camera | 1929 | 8.3 | 30477 |
| 4 | Disaster Movie | 2008 | 1.9 | 98097 |
| 4 | Justin Bieber: Never Say Never | 2011 | 1.7 | 76054 |
| 4 | Reis | 2017 | 1.0 | 74715 |
| 4 | Melania | 2026 | 1.6 | 69061 |
| 4 | The Prototype | 2022 | 2.3 | 47352 |

## Artefactos generados

- Tabla `kmeans_evaluation`: `reports/tables/kmeans_evaluation.csv`
- Tabla `cluster_summary`: `reports/tables/cluster_summary.csv`
- Tabla `cluster_top_movies`: `reports/tables/cluster_top_movies.csv`
- Figura `kmeans_elbow`: `reports/figures/kmeans_elbow.png`
- Figura `kmeans_silhouette`: `reports/figures/kmeans_silhouette.png`
- Figura `cluster_distribution`: `reports/figures/cluster_distribution.png`
- Figura `cluster_rating_runtime`: `reports/figures/cluster_rating_runtime.png`
- Dataset clusterizado: `data/final/movies_clustered.csv`
- Modelo: `models/kmeans_model.joblib`

## Siguiente paso

Usar `movies_clustered.csv` para alimentar recomendaciones y reemplazar datos estaticos del dashboard.
