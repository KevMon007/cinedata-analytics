from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


REQUIRED_COLUMNS = ["tconst", "primaryTitle", "startYear", "runtimeMinutes", "genres", "averageRating", "numVotes"]
FEATURE_COLUMNS = ["startYear", "runtimeMinutes", "averageRating", "logNumVotes"]


def validate_clustering_input(df: pd.DataFrame, feature_columns=None) -> None:
    """Valida que el dataset tenga columnas y valores aptos para clustering."""
    feature_columns = feature_columns or FEATURE_COLUMNS
    required = list(dict.fromkeys(REQUIRED_COLUMNS + feature_columns))
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas para clustering: {missing}")
    if df.empty:
        raise ValueError("El dataset para clustering esta vacio")
    if df[feature_columns].isna().any().any():
        raise ValueError("Las features para clustering contienen valores nulos")
    non_numeric = [col for col in feature_columns if not np.issubdtype(df[col].dtype, np.number)]
    if non_numeric:
        raise ValueError(f"Las features deben ser numericas: {non_numeric}")


def add_clustering_features(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega features derivadas para clustering sin modificar el DataFrame original."""
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas para clustering: {missing}")

    result = df.copy()
    result["decade"] = (result["startYear"] // 10) * 10
    result["mainGenre"] = result["genres"].fillna("Unknown").astype(str).str.split(",").str[0].str.strip()
    result["genreCount"] = result["genres"].fillna("Unknown").astype(str).str.split(",").str.len()
    result["logNumVotes"] = np.log10(result["numVotes"] + 1)
    return result


def prepare_features(df: pd.DataFrame, feature_columns=None):
    """Selecciona y escala las features numericas para clustering."""
    feature_columns = feature_columns or FEATURE_COLUMNS
    df_features = add_clustering_features(df) if "logNumVotes" not in df.columns else df.copy()
    validate_clustering_input(df_features, feature_columns)
    X = df_features[feature_columns].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, scaler


def validate_n_clusters(n_clusters: int, row_count: int) -> None:
    """Valida que k sea compatible con el tamano del dataset."""
    if n_clusters < 2:
        raise ValueError("n_clusters debe ser mayor o igual a 2")
    if n_clusters >= row_count:
        raise ValueError("n_clusters debe ser menor que el numero de registros")


def evaluate_kmeans(
    df: pd.DataFrame,
    k_values=range(2, 11),
    feature_columns=None,
    random_state: int = 42,
    silhouette_sample_size: int = 10000,
) -> pd.DataFrame:
    """Evalua varios valores de k usando inertia y silhouette_score."""
    feature_columns = feature_columns or FEATURE_COLUMNS
    X_scaled, _ = prepare_features(df, feature_columns)
    results = []

    for k in k_values:
        validate_n_clusters(int(k), len(df))
        model = KMeans(n_clusters=int(k), random_state=random_state, n_init=10)
        labels = model.fit_predict(X_scaled)
        sample_size = min(silhouette_sample_size, len(df))
        silhouette = silhouette_score(X_scaled, labels, sample_size=sample_size, random_state=random_state)
        results.append({
            "k": int(k),
            "inertia": round(float(model.inertia_), 4),
            "silhouette_score": round(float(silhouette), 4),
        })

    return pd.DataFrame(results).sort_values("k").reset_index(drop=True)


def select_best_k(evaluation_df: pd.DataFrame) -> int:
    """Selecciona el k con mayor silhouette_score."""
    required = {"k", "silhouette_score"}
    missing = required - set(evaluation_df.columns)
    if missing:
        raise ValueError(f"Faltan columnas de evaluacion: {sorted(missing)}")
    if evaluation_df.empty:
        raise ValueError("La evaluacion de k esta vacia")
    best = evaluation_df.sort_values(["silhouette_score", "k"], ascending=[False, True]).iloc[0]
    return int(best["k"])


def train_kmeans(df: pd.DataFrame, n_clusters=5, random_state=42, feature_columns=None):
    """Entrena K-Means y retorna modelo, scaler y DataFrame con cluster."""
    feature_columns = feature_columns or FEATURE_COLUMNS
    validate_n_clusters(int(n_clusters), len(df))
    df_features = add_clustering_features(df) if "logNumVotes" not in df.columns else df.copy()
    X_scaled, scaler = prepare_features(df_features, feature_columns)
    model = KMeans(n_clusters=int(n_clusters), random_state=random_state, n_init=10)
    labels = model.fit_predict(X_scaled)
    result = df_features.copy()
    result["cluster"] = labels
    result["distanceToCentroid"] = np.linalg.norm(X_scaled - model.cluster_centers_[labels], axis=1).round(4)
    return model, scaler, result


def predict_cluster(model, scaler, new_data: pd.DataFrame, feature_columns=None):
    """Asigna un cluster a nuevos datos."""
    feature_columns = feature_columns or FEATURE_COLUMNS
    df_features = add_clustering_features(new_data) if "logNumVotes" not in new_data.columns else new_data.copy()
    validate_clustering_input(df_features, feature_columns)
    X_scaled = scaler.transform(df_features[feature_columns])
    return model.predict(X_scaled)


def get_cluster_info(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna resumen estadistico de cada cluster."""
    if "cluster" not in df.columns:
        raise ValueError("El DataFrame no tiene columna 'cluster'. Ejecuta train_kmeans primero.")

    summary = df.groupby("cluster").agg(
        cantidad=("tconst", "count"),
        rating_promedio=("averageRating", "mean"),
        duracion_promedio=("runtimeMinutes", "mean"),
        anio_promedio=("startYear", "mean"),
        votos_mediana=("numVotes", "median"),
        log_votos_promedio=("logNumVotes", "mean"),
        distancia_promedio=("distanceToCentroid", "mean"),
    ).round(2)

    genre_col = "mainGenre" if "mainGenre" in df.columns else "genres"
    summary["genero_principal"] = df.groupby("cluster")[genre_col].agg(
        lambda x: x.value_counts().index[0] if len(x) > 0 else "Unknown"
    )
    return summary.reset_index().sort_values("cluster")


def get_cluster_movies(df: pd.DataFrame, cluster_label, top_n=10) -> pd.DataFrame:
    """Retorna las peliculas mas visibles de un cluster por votos."""
    if "cluster" not in df.columns:
        raise ValueError("El DataFrame no tiene columna 'cluster'.")
    cluster_df = df[df["cluster"] == cluster_label]
    return cluster_df.sort_values("numVotes", ascending=False).head(top_n).reset_index(drop=True)


def get_recommendations(df: pd.DataFrame, tconst: str, top_n: int = 10) -> pd.DataFrame:
    """Recomienda peliculas del mismo cluster priorizando cercania al centroide y rating."""
    if "cluster" not in df.columns:
        raise ValueError("El DataFrame no tiene columna 'cluster'.")
    matches = df[df["tconst"] == tconst]
    if matches.empty:
        raise ValueError(f"No se encontro la pelicula: {tconst}")

    movie = matches.iloc[0]
    candidates = df[(df["cluster"] == movie["cluster"]) & (df["tconst"] != tconst)].copy()
    return (
        candidates.sort_values(["distanceToCentroid", "averageRating", "numVotes"], ascending=[True, False, False])
        .head(top_n)
        .reset_index(drop=True)
    )


def calculate_distance_to_centroid(model, scaler, movie_row: pd.DataFrame, feature_columns=None):
    """Calcula distancia y similitud aproximada de una pelicula a su centroide."""
    feature_columns = feature_columns or FEATURE_COLUMNS
    df_features = add_clustering_features(movie_row) if "logNumVotes" not in movie_row.columns else movie_row.copy()
    validate_clustering_input(df_features, feature_columns)
    X_scaled = scaler.transform(df_features[feature_columns])
    cluster_label = model.predict(X_scaled)[0]
    centroid = model.cluster_centers_[cluster_label]
    distance = np.linalg.norm(X_scaled[0] - centroid)
    centroid_distances = np.linalg.norm(model.cluster_centers_ - model.cluster_centers_.mean(axis=0), axis=1)
    max_distance = np.max(centroid_distances)
    similarity = max(0, 100 - (distance / max_distance * 100)) if max_distance > 0 else 100
    return int(cluster_label), round(float(distance), 4), round(float(similarity), 2)


def save_model(model, scaler, filepath, feature_columns=None):
    """Guarda el modelo K-Means, scaler y columnas usadas."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "scaler": scaler, "feature_columns": feature_columns or FEATURE_COLUMNS}, filepath)


def load_model(filepath):
    """Carga un modelo K-Means y scaler desde un archivo .joblib."""
    data = joblib.load(filepath)
    return data["model"], data["scaler"]


def load_model_bundle(filepath):
    """Carga el paquete completo del modelo guardado."""
    return joblib.load(filepath)
