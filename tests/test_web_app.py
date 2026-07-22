import pandas as pd

from web.app import app
from web import data as web_data


def sample_clustered_movies():
    return pd.DataFrame({
        "tconst": ["tt1", "tt2", "tt3"],
        "primaryTitle": ["Movie A", "Movie B", "Movie C"],
        "originalTitle": ["Movie A", "Movie B", "Movie C"],
        "isAdult": [0, 0, 0],
        "startYear": [2000, 2010, 2020],
        "runtimeMinutes": [100, 120, 90],
        "genres": ["Drama", "Action", "Comedy"],
        "averageRating": [8.0, 7.0, 6.0],
        "numVotes": [1000, 5000, 100],
        "decade": [2000, 2010, 2020],
        "mainGenre": ["Drama", "Action", "Comedy"],
        "genreCount": [1, 1, 1],
        "logNumVotes": [3.0, 3.7, 2.0],
        "cluster": [0, 1, 1],
        "distanceToCentroid": [1.0, 2.0, 1.5],
    })


def sample_cluster_summary():
    return pd.DataFrame({
        "cluster": [0, 1],
        "cantidad": [1, 2],
        "rating_promedio": [8.0, 6.5],
        "duracion_promedio": [100, 105],
        "anio_promedio": [2000, 2015],
        "votos_mediana": [1000, 2550],
        "log_votos_promedio": [3.0, 2.8],
        "distancia_promedio": [1.0, 1.75],
        "genero_principal": ["Drama", "Action"],
    })


def sample_cluster_top_movies():
    return pd.DataFrame({
        "cluster": [0, 1],
        "tconst": ["tt1", "tt2"],
        "primaryTitle": ["Cluster Preview A", "Cluster Preview B"],
        "startYear": [2020, 2010],
        "genres": ["Drama", "Action"],
        "averageRating": [8.0, 7.0],
        "numVotes": [5000, 9000],
        "distanceToCentroid": [1.0, 2.0],
    })


def test_index_uses_cluster_top_movies_for_preview(monkeypatch):
    monkeypatch.setattr(web_data, "load_cluster_top_movies", sample_cluster_top_movies)

    app.config["TESTING"] = True
    response = app.test_client().get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Cluster Preview A" in html
    assert "Cluster Preview B" in html
    assert "Blade Runner 2049" not in html


def test_index_falls_back_to_static_preview_when_cluster_top_is_missing(monkeypatch):
    def raise_missing_file():
        raise web_data.WebDataError("Falta cluster_top_movies.csv")

    monkeypatch.setattr(web_data, "load_cluster_top_movies", raise_missing_file)

    app.config["TESTING"] = True
    response = app.test_client().get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Blade Runner 2049" in html


def test_dashboard_uses_web_data_layer(monkeypatch):
    monkeypatch.setattr(web_data, "load_clustered_movies", sample_clustered_movies)
    monkeypatch.setattr(web_data, "load_cluster_summary", sample_cluster_summary)
    monkeypatch.setattr(
        web_data,
        "load_kmeans_evaluation",
        lambda: pd.DataFrame({"k": [2], "inertia": [100], "silhouette_score": [0.321]}),
    )

    app.config["TESTING"] = True
    response = app.test_client().get("/dashboard")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Peliculas analizadas" in html
    assert "3" in html
    assert "silhouette 0.3210" in html
    assert "Cluster 0" in html
    assert "Cluster 1" in html
    assert "2000" in html
    assert "Datos pendientes" not in html


def test_dashboard_shows_notice_when_cluster_files_are_missing(monkeypatch):
    def raise_missing_file():
        raise web_data.WebDataError("Faltan artefactos de clustering")

    monkeypatch.setattr(web_data, "load_clustered_movies", raise_missing_file)

    app.config["TESTING"] = True
    response = app.test_client().get("/dashboard")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Datos pendientes" in html
    assert "Faltan artefactos de clustering" in html
    assert "311,989" in html
