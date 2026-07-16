import pandas as pd
import pytest

from src.models.cluster import (
    FEATURE_COLUMNS,
    add_clustering_features,
    evaluate_kmeans,
    get_cluster_info,
    get_cluster_movies,
    get_recommendations,
    load_model,
    predict_cluster,
    prepare_features,
    save_model,
    select_best_k,
    train_kmeans,
    validate_clustering_input,
)


def sample_movies_df():
    return pd.DataFrame({
        "tconst": [f"tt{i}" for i in range(1, 9)],
        "primaryTitle": [f"Movie {i}" for i in range(1, 9)],
        "originalTitle": [f"Movie {i}" for i in range(1, 9)],
        "isAdult": [0] * 8,
        "startYear": [1980, 1982, 1985, 2000, 2002, 2005, 2020, 2022],
        "runtimeMinutes": [90, 95, 88, 120, 125, 118, 150, 155],
        "genres": ["Drama", "Drama", "Comedy", "Action", "Action", "Adventure", "Sci-Fi", "Sci-Fi"],
        "averageRating": [6.0, 6.2, 6.1, 7.5, 7.6, 7.4, 8.5, 8.7],
        "numVotes": [100, 120, 110, 5000, 5200, 5100, 80000, 82000],
    })


def test_add_clustering_features_does_not_modify_original_df():
    df = sample_movies_df()
    result = add_clustering_features(df)

    assert "logNumVotes" not in df.columns
    assert "logNumVotes" in result.columns
    assert list(result["decade"].head(3)) == [1980, 1980, 1980]
    assert list(result["mainGenre"].tail(2)) == ["Sci-Fi", "Sci-Fi"]


def test_validate_clustering_input_raises_when_column_missing():
    df = add_clustering_features(sample_movies_df()).drop(columns=["runtimeMinutes"])

    with pytest.raises(ValueError, match="runtimeMinutes"):
        validate_clustering_input(df)


def test_prepare_features_returns_scaled_matrix_and_scaler():
    X_scaled, scaler = prepare_features(sample_movies_df())

    assert X_scaled.shape == (8, len(FEATURE_COLUMNS))
    assert hasattr(scaler, "transform")


def test_evaluate_kmeans_returns_metrics_for_each_k():
    result = evaluate_kmeans(sample_movies_df(), k_values=range(2, 4), silhouette_sample_size=8)

    assert list(result["k"]) == [2, 3]
    assert set(result.columns) == {"k", "inertia", "silhouette_score"}


def test_select_best_k_uses_highest_silhouette_and_lowest_k_on_tie():
    evaluation = pd.DataFrame({
        "k": [2, 3, 4],
        "inertia": [10.0, 8.0, 7.0],
        "silhouette_score": [0.5, 0.7, 0.7],
    })

    assert select_best_k(evaluation) == 3


def test_train_kmeans_adds_cluster_and_distance_columns():
    model, scaler, result = train_kmeans(sample_movies_df(), n_clusters=3)

    assert model.n_clusters == 3
    assert hasattr(scaler, "transform")
    assert "cluster" in result.columns
    assert "distanceToCentroid" in result.columns
    assert result["cluster"].nunique() == 3


def test_predict_cluster_returns_labels_for_new_data():
    model, scaler, clustered = train_kmeans(sample_movies_df(), n_clusters=3)
    labels = predict_cluster(model, scaler, clustered.head(2))

    assert len(labels) == 2


def test_get_cluster_info_returns_one_row_per_cluster():
    _, _, clustered = train_kmeans(sample_movies_df(), n_clusters=3)
    result = get_cluster_info(clustered)

    assert len(result) == 3
    assert "genero_principal" in result.columns


def test_get_cluster_movies_filters_cluster():
    _, _, clustered = train_kmeans(sample_movies_df(), n_clusters=3)
    cluster_label = clustered.iloc[0]["cluster"]
    result = get_cluster_movies(clustered, cluster_label, top_n=2)

    assert len(result) <= 2
    assert set(result["cluster"]) == {cluster_label}


def test_get_recommendations_excludes_source_movie():
    _, _, clustered = train_kmeans(sample_movies_df(), n_clusters=3)
    source = clustered.iloc[0]["tconst"]
    result = get_recommendations(clustered, source, top_n=3)

    assert source not in set(result["tconst"])


def test_save_and_load_model(tmp_path):
    model, scaler, _ = train_kmeans(sample_movies_df(), n_clusters=3)
    filepath = tmp_path / "kmeans_model.joblib"

    save_model(model, scaler, filepath)
    loaded_model, loaded_scaler = load_model(filepath)

    assert loaded_model.n_clusters == 3
    assert hasattr(loaded_scaler, "transform")
