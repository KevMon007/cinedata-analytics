# Reporte EDA

## Objetivo

Analizar el dataset final generado por el ETL y preparar decisiones para aprendizaje no supervisado.

## Dataset

- Peliculas analizadas: 311,988
- Columnas: 9
- Duplicados exactos: 0
- Valores faltantes totales: 0
- Periodo cubierto: 1900-2026
- Rating promedio: 6.13
- Duracion promedio: 93.89 minutos

## Hallazgos principales

- El genero mas frecuente es `Drama` con 145,157 apariciones.
- La decada con mayor rating promedio es 2020 con 6.23.
- La correlacion entre votos y rating es 0.067; para clustering conviene usar `logNumVotes` por la escala de votos.
- Las variables numericas principales tienen escalas muy distintas, por lo que el modelado debe escalar features antes de entrenar.

## Top peliculas por rating

| primaryTitle | startYear | averageRating | numVotes |
| --- | --- | --- | --- |
| Vinara O Vema | 2026 | 9.7 | 1152 |
| One/4 | 2026 | 9.7 | 1037 |
| Moda Kavida Vaatavarana | 2026 | 9.7 | 1011 |
| Dama Dum Mast Kalandar | 2026 | 9.6 | 3503 |
| Laggam Time | 2026 | 9.6 | 1081 |

## Artefactos generados

- Tabla `dataset_summary`: `reports/tables/dataset_summary.csv`
- Tabla `numeric_summary`: `reports/tables/numeric_summary.csv`
- Tabla `genre_summary`: `reports/tables/genre_summary.csv`
- Tabla `decade_summary`: `reports/tables/decade_summary.csv`
- Tabla `top_rated_movies`: `reports/tables/top_rated_movies.csv`
- Tabla `most_voted_movies`: `reports/tables/most_voted_movies.csv`
- Tabla `correlation_matrix`: `reports/tables/correlation_matrix.csv`
- Tabla `clustering_feature_summary`: `reports/tables/clustering_feature_summary.csv`
- Figura `ratings_distribution`: `reports/figures/ratings_distribution.png`
- Figura `runtime_distribution`: `reports/figures/runtime_distribution.png`
- Figura `votes_distribution_log`: `reports/figures/votes_distribution_log.png`
- Figura `top_genres`: `reports/figures/top_genres.png`
- Figura `movies_by_decade`: `reports/figures/movies_by_decade.png`
- Figura `rating_vs_votes`: `reports/figures/rating_vs_votes.png`
- Figura `rating_vs_runtime`: `reports/figures/rating_vs_runtime.png`
- Figura `correlation_heatmap`: `reports/figures/correlation_matrix.png`

## Recomendaciones para clustering

- Usar como base `startYear`, `runtimeMinutes`, `averageRating` y `logNumVotes`.
- Evaluar si `decade` aporta mejor interpretabilidad que `startYear` continuo.
- Tratar `genres` como variable categorica separada o usar `mainGenre` solo para interpretar clusters.
- Probar varios valores de `k` con metodo del codo y silhouette score antes de fijar el numero final de clusters.
- Mantener escalado de variables numericas antes de aplicar K-Means.
