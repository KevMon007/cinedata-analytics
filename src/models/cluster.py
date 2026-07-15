import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import joblib


FEATURE_COLUMNS = ["startYear", "runtimeMinutes", "averageRating", "numVotes"]


def prepare_features(df):
    """Selecciona y escala las features numéricas para clustering."""
    X = df[FEATURE_COLUMNS].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled, scaler


def train_kmeans(df, n_clusters=5, random_state=42):
    """Entrena un modelo K-Means y retorna el modelo, scaler y labels."""
    X_scaled, scaler = prepare_features(df)
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = model.fit_predict(X_scaled)
    df = df.copy()
    df["cluster"] = labels
    return model, scaler, df


def predict_cluster(model, scaler, new_data):
    """Asigna un cluster a nuevos datos."""
    X_scaled = scaler.transform(new_data[FEATURE_COLUMNS])
    return model.predict(X_scaled)


def get_cluster_info(df):
    """Retorna resumen estadístico de cada cluster."""
    if "cluster" not in df.columns:
        raise ValueError("El DataFrame no tiene columna 'cluster'. Ejecuta train_kmeans primero.")

    summary = df.groupby("cluster").agg(
        cantidad=("tconst", "count"),
        rating_promedio=("averageRating", "mean"),
        duracion_promedio=("runtimeMinutes", "mean"),
        año_promedio=("startYear", "mean"),
        votos_promedio=("numVotes", "mean"),
    ).round(2)

    genre_per_cluster = df.groupby("cluster")["genres"].agg(
        lambda x: x.value_counts().index[0] if len(x) > 0 else "Unknown"
    )
    summary["genero_principal"] = genre_per_cluster
    return summary.reset_index()


def get_cluster_movies(df, cluster_label, top_n=10):
    """Retorna las películas más representativas de un cluster (mayor cantidad de votos)."""
    cluster_df = df[df["cluster"] == cluster_label]
    return cluster_df.sort_values("numVotes", ascending=False).head(top_n)


def calculate_distance_to_centroid(model, scaler, movie_row):
    """Calcula la distancia de una película al centroide de su cluster."""
    X_scaled = scaler.transform(movie_row[FEATURE_COLUMNS])
    cluster_label = model.predict(X_scaled)[0]
    centroid = model.cluster_centers_[cluster_label]
    distance = np.linalg.norm(X_scaled[0] - centroid)
    max_distance = np.max(np.linalg.norm(model.cluster_centers_ - model.cluster_centers_.mean(axis=0), axis=1))
    similarity = max(0, 100 - (distance / max_distance * 100)) if max_distance > 0 else 100
    return cluster_label, round(distance, 4), round(similarity, 2)


def save_model(model, scaler, filepath):
    """Guarda el modelo K-Means y el scaler en un archivo .joblib."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "scaler": scaler}, filepath)


def load_model(filepath):
    """Carga un modelo K-Means y scaler desde un archivo .joblib."""
    data = joblib.load(filepath)
    return data["model"], data["scaler"]
