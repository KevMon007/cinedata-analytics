from pathlib import Path

import pandas as pd

from src.utils.paths import PROJECT_ROOT


CLUSTERED_MOVIES_PATH = PROJECT_ROOT / "data" / "final" / "movies_clustered.csv"
CLUSTER_SUMMARY_PATH = PROJECT_ROOT / "reports" / "tables" / "cluster_summary.csv"
KMEANS_EVALUATION_PATH = PROJECT_ROOT / "reports" / "tables" / "kmeans_evaluation.csv"
CLUSTER_TOP_MOVIES_PATH = PROJECT_ROOT / "reports" / "tables" / "cluster_top_movies.csv"


class WebDataError(RuntimeError):
    """Error cuando faltan artefactos necesarios para la web."""


def _read_csv(path) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise WebDataError(
            f"No se encontro el archivo requerido: {file_path}. "
            "Ejecuta `python -m src.models.run_clustering` antes de levantar la web."
        )
    return pd.read_csv(file_path)


def load_clustered_movies(path=CLUSTERED_MOVIES_PATH) -> pd.DataFrame:
    """Carga el dataset final con clusters."""
    return _read_csv(path)


def load_cluster_summary(path=CLUSTER_SUMMARY_PATH) -> pd.DataFrame:
    """Carga el resumen de clusters generado por la fase de clustering."""
    return _read_csv(path)


def load_kmeans_evaluation(path=KMEANS_EVALUATION_PATH) -> pd.DataFrame:
    """Carga la evaluacion de k para K-Means."""
    return _read_csv(path)


def load_cluster_top_movies(path=CLUSTER_TOP_MOVIES_PATH) -> pd.DataFrame:
    """Carga peliculas destacadas por cluster."""
    return _read_csv(path)


def format_int(value) -> str:
    """Formatea enteros para visualizacion."""
    return f"{int(value):,}"


def get_dashboard_metrics(movies_df: pd.DataFrame, evaluation_df: pd.DataFrame | None = None) -> list[dict]:
    """Genera metricas generales para el dashboard."""
    min_year = int(movies_df["startYear"].min())
    max_year = int(movies_df["startYear"].max())
    cluster_count = int(movies_df["cluster"].nunique())

    cluster_detail = "K-Means"
    if evaluation_df is not None and not evaluation_df.empty:
        best = evaluation_df.sort_values("silhouette_score", ascending=False).iloc[0]
        cluster_detail = f"silhouette {best['silhouette_score']:.4f}"

    return [
        {"label": "Peliculas analizadas", "value": format_int(len(movies_df)), "detail": "dataset IMDb clusterizado"},
        {"label": "Clusters formados", "value": str(cluster_count), "detail": cluster_detail},
        {"label": "Rating promedio", "value": f"{movies_df['averageRating'].mean():.2f}", "detail": "escala 0-10"},
        {"label": "Periodo cubierto", "value": f"{min_year}-{max_year}", "detail": "rango historico"},
    ]


def get_cluster_distribution(cluster_summary_df: pd.DataFrame) -> list[dict]:
    """Genera barras porcentuales de distribucion por cluster."""
    total = cluster_summary_df["cantidad"].sum()
    result = []
    for row in cluster_summary_df.sort_values("cluster").itertuples(index=False):
        percentage = round((row.cantidad / total) * 100, 1) if total else 0
        result.append({
            "label": f"Cluster {row.cluster}",
            "value": percentage,
            "count": format_int(row.cantidad),
        })
    return result


def get_rating_trends(movies_df: pd.DataFrame) -> list[dict]:
    """Genera rating promedio por decada en escala porcentual para la grafica."""
    df = movies_df.copy()
    if "decade" not in df.columns:
        df["decade"] = (df["startYear"] // 10) * 10

    trends = df.groupby("decade")["averageRating"].mean().reset_index()
    trends = trends.sort_values("decade")
    return [
        {"label": str(int(row.decade)), "value": round(float(row.averageRating) * 10, 1)}
        for row in trends.itertuples(index=False)
    ]


def _movie_to_card(row) -> dict:
    distance = float(getattr(row, "distanceToCentroid", 0))
    similarity = max(0, min(100, round(100 - (distance * 12))))
    return {
        "title": row.primaryTitle,
        "year": int(row.startYear),
        "genre": row.genres,
        "rating": round(float(row.averageRating), 1),
        "votes": format_int(row.numVotes),
        "similarity": similarity,
        "cluster": int(row.cluster),
        "description": (
            f"Pelicula del cluster {int(row.cluster)} con rating {float(row.averageRating):.1f}, "
            f"{format_int(row.numVotes)} votos y duracion de {int(getattr(row, 'runtimeMinutes', 0))} min."
        ),
        "reasons": [
            f"Pertenece al cluster {int(row.cluster)}",
            f"Rating promedio de {float(row.averageRating):.1f}/10",
            f"Popularidad: {format_int(row.numVotes)} votos",
        ],
    }


def get_preview_recommendations(movies_df: pd.DataFrame, top_n: int = 4) -> list[dict]:
    """Genera peliculas reales para la vista previa del recomendador."""
    preview = movies_df.sort_values(["numVotes", "averageRating"], ascending=[False, False]).head(top_n)
    return [_movie_to_card(row) for row in preview.itertuples(index=False)]


def get_preview_recommendations_from_cluster_top(cluster_top_df: pd.DataFrame, top_n: int = 5) -> list[dict]:
    """Genera vista previa usando peliculas destacadas por cluster."""
    required = ["cluster", "primaryTitle", "startYear", "genres", "averageRating", "numVotes", "distanceToCentroid"]
    missing = [col for col in required if col not in cluster_top_df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas para preview: {missing}")

    preview = (
        cluster_top_df.sort_values(["cluster", "numVotes", "averageRating"], ascending=[True, False, False])
        .groupby("cluster", as_index=False)
        .head(1)
        .sort_values("cluster")
        .head(top_n)
    )
    return [_movie_to_card(row) for row in preview.itertuples(index=False)]


def build_dashboard_context(
    movies_df: pd.DataFrame,
    cluster_summary_df: pd.DataFrame,
    evaluation_df: pd.DataFrame | None = None,
) -> dict:
    """Construye el contexto completo que consumira /dashboard en el siguiente paso."""
    return {
        "metrics": get_dashboard_metrics(movies_df, evaluation_df),
        "clusters": get_cluster_distribution(cluster_summary_df),
        "trends": get_rating_trends(movies_df),
    }
