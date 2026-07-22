# Notas de integracion web

## Decision actual

La vista previa del home usa la opcion C: leer `reports/tables/cluster_top_movies.csv`.

Esta opcion respeta directamente los artefactos generados por la fase de aprendizaje no supervisado, porque muestra peliculas destacadas por cluster ya calculadas durante `python -m src.models.run_clustering`.

## Alternativa B

Si el equipo decide usar la opcion B, la vista previa debe calcularse directamente desde `data/final/movies_clustered.csv`.

Cambio recomendado:

1. En `web/app.py`, reemplazar `load_cluster_top_movies()` por `load_clustered_movies()` para la ruta `/`.
2. Usar una funcion tipo `get_preview_recommendations_by_cluster(movies_df)`.
3. Seleccionar una pelicula por cluster desde `movies_clustered.csv`.
4. Ordenar candidatas dentro de cada cluster por una regla explicita.

Reglas candidatas para la opcion B:

- Mayor `numVotes` por cluster para mostrar peliculas reconocibles.
- Menor `distanceToCentroid` por cluster para mostrar peliculas mas representativas del centroide.
- Mayor `averageRating` con minimo de votos para evitar peliculas poco confiables.

La recomendacion inicial para opcion B seria:

1. Filtrar peliculas con `numVotes >= 1000`.
2. Ordenar por `cluster`, `distanceToCentroid` ascendente, `averageRating` descendente y `numVotes` descendente.
3. Tomar una pelicula por cluster.
4. Convertir al mismo formato de tarjetas que consume `index.html`.

## Razon para mantener el formato actual

El template `web/templates/index.html` espera objetos con:

- `title`
- `year`
- `genre`
- `rating`
- `votes`
- `similarity`
- `cluster`
- `description`
- `reasons`

Mientras la funcion nueva respete ese formato, no es necesario modificar el HTML.
