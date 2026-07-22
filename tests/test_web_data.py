import pandas as pd
import pytest

from web.data import (
    WebDataError,
    build_dashboard_context,
    format_int,
    get_cluster_distribution,
    get_dashboard_metrics,
    get_preview_recommendations,
    get_preview_recommendations_from_cluster_top,
    get_rating_trends,
    load_clustered_movies,
)


def sample_clustered_movies():
    return pd.DataFrame({
        "tconst": ["tt1", "tt2", "tt3", "tt4"],
        "primaryTitle": ["Movie A", "Movie B", "Movie C", "Movie D"],
        "originalTitle": ["Movie A", "Movie B", "Movie C", "Movie D"],
        "isAdult": [0, 0, 0, 0],
        "startYear": [1999, 2001, 2005, 2020],
        "runtimeMinutes": [100, 120, 90, 150],
        "genres": ["Drama", "Action", "Comedy", "Sci-Fi"],
        "averageRating": [8.0, 7.0, 6.0, 9.0],
        "numVotes": [1000, 5000, 100, 10000],
        "decade": [1990, 2000, 2000, 2020],
        "mainGenre": ["Drama", "Action", "Comedy", "Sci-Fi"],
        "genreCount": [1, 1, 1, 1],
        "logNumVotes": [3.0, 3.7, 2.0, 4.0],
        "cluster": [0, 1, 1, 0],
        "distanceToCentroid": [1.0, 2.0, 1.5, 0.5],
    })


def sample_cluster_summary():
    return pd.DataFrame({
        "cluster": [0, 1],
        "cantidad": [2, 2],
        "rating_promedio": [8.5, 6.5],
        "duracion_promedio": [125, 105],
        "anio_promedio": [2010, 2003],
        "votos_mediana": [5500, 2550],
        "log_votos_promedio": [3.5, 2.8],
        "distancia_promedio": [0.75, 1.75],
        "genero_principal": ["Drama", "Action"],
    })


def sample_cluster_top_movies():
    return pd.DataFrame({
        "cluster": [0, 0, 1, 1],
        "tconst": ["tt1", "tt2", "tt3", "tt4"],
        "primaryTitle": ["Cluster 0 Top", "Cluster 0 Second", "Cluster 1 Top", "Cluster 1 Second"],
        "startYear": [2020, 2019, 2000, 2001],
        "genres": ["Drama", "Comedy", "Action", "Thriller"],
        "averageRating": [8.0, 8.5, 7.0, 7.5],
        "numVotes": [5000, 1000, 9000, 2000],
        "distanceToCentroid": [1.0, 0.5, 2.0, 1.5],
    })


def test_load_clustered_movies_reads_csv(tmp_path):
    filepath = tmp_path / "movies_clustered.csv"
    expected = sample_clustered_movies()
    expected.to_csv(filepath, index=False)

    result = load_clustered_movies(filepath)

    pd.testing.assert_frame_equal(result, expected)


def test_load_clustered_movies_missing_file_raises_clear_error(tmp_path):
    with pytest.raises(WebDataError, match="run_clustering"):
        load_clustered_movies(tmp_path / "missing.csv")


def test_format_int_adds_thousands_separator():
    assert format_int(1234567) == "1,234,567"


def test_get_dashboard_metrics_uses_real_values():
    evaluation = pd.DataFrame({"k": [2, 3], "inertia": [100, 90], "silhouette_score": [0.2, 0.35]})

    result = get_dashboard_metrics(sample_clustered_movies(), evaluation)

    assert result[0] == {
        "label": "Peliculas analizadas",
        "value": "4",
        "detail": "dataset IMDb clusterizado",
    }
    assert result[1]["value"] == "2"
    assert result[1]["detail"] == "silhouette 0.3500"
    assert result[2]["value"] == "7.50"
    assert result[3]["value"] == "1999-2020"


def test_get_cluster_distribution_returns_percentages_and_counts():
    result = get_cluster_distribution(sample_cluster_summary())

    assert result == [
        {"label": "Cluster 0", "value": 50.0, "count": "2"},
        {"label": "Cluster 1", "value": 50.0, "count": "2"},
    ]


def test_get_rating_trends_groups_by_decade():
    result = get_rating_trends(sample_clustered_movies())

    assert result == [
        {"label": "1990", "value": 80.0},
        {"label": "2000", "value": 65.0},
        {"label": "2020", "value": 90.0},
    ]


def test_get_preview_recommendations_uses_top_voted_movies():
    result = get_preview_recommendations(sample_clustered_movies(), top_n=2)

    assert [movie["title"] for movie in result] == ["Movie D", "Movie B"]
    assert result[0]["cluster"] == 0
    assert result[0]["votes"] == "10,000"
    assert result[0]["similarity"] == 94


def test_get_preview_recommendations_from_cluster_top_uses_one_movie_per_cluster():
    result = get_preview_recommendations_from_cluster_top(sample_cluster_top_movies(), top_n=2)

    assert [movie["title"] for movie in result] == ["Cluster 0 Top", "Cluster 1 Top"]
    assert [movie["cluster"] for movie in result] == [0, 1]
    assert result[0]["votes"] == "5,000"
    assert result[0]["similarity"] == 88


def test_get_preview_recommendations_from_cluster_top_validates_columns():
    with pytest.raises(ValueError, match="distanceToCentroid"):
        get_preview_recommendations_from_cluster_top(sample_cluster_top_movies().drop(columns=["distanceToCentroid"]))


def test_build_dashboard_context_contains_expected_sections():
    result = build_dashboard_context(
        sample_clustered_movies(),
        sample_cluster_summary(),
        pd.DataFrame({"k": [2], "inertia": [100], "silhouette_score": [0.2]}),
    )

    assert set(result) == {"metrics", "clusters", "trends"}
    assert len(result["metrics"]) == 4
    assert len(result["clusters"]) == 2
    assert len(result["trends"]) == 3
