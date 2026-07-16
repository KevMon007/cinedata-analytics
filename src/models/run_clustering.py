import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.models.cluster import (
    FEATURE_COLUMNS,
    evaluate_kmeans,
    get_cluster_info,
    get_cluster_movies,
    save_model,
    select_best_k,
    train_kmeans,
)
from src.utils.paths import PROJECT_ROOT, REPORTS_FIGURES, REPORTS_TABLES, get_final_dataset_path


MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "kmeans_model.joblib"
CLUSTERED_DATASET_PATH = PROJECT_ROOT / "data" / "final" / "movies_clustered.csv"
REPORT_PATH = PROJECT_ROOT / "reports" / "clustering_report.md"


def save_table(df: pd.DataFrame, filepath) -> Path:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    return path


def save_kmeans_elbow_plot(evaluation_df: pd.DataFrame, filepath) -> Path:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    sns.lineplot(data=evaluation_df, x="k", y="inertia", marker="o")
    plt.title("Metodo del codo - K-Means")
    plt.xlabel("k")
    plt.ylabel("Inertia")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def save_silhouette_plot(evaluation_df: pd.DataFrame, filepath) -> Path:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    sns.lineplot(data=evaluation_df, x="k", y="silhouette_score", marker="o")
    plt.title("Silhouette score por k")
    plt.xlabel("k")
    plt.ylabel("Silhouette score")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def save_cluster_distribution_plot(cluster_summary: pd.DataFrame, filepath) -> Path:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=cluster_summary, x="cluster", y="cantidad", color="#4C78A8")
    plt.title("Distribucion de peliculas por cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Peliculas")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def save_cluster_scatter_plot(df_clustered: pd.DataFrame, filepath, sample_size: int = 30000) -> Path:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_data = df_clustered.sample(n=min(sample_size, len(df_clustered)), random_state=42)
    plt.figure(figsize=(9, 6))
    sns.scatterplot(
        data=plot_data,
        x="runtimeMinutes",
        y="averageRating",
        hue="cluster",
        palette="tab10",
        alpha=0.35,
        s=14,
        edgecolor=None,
    )
    plt.title("Clusters por duracion y rating")
    plt.xlabel("Duracion en minutos")
    plt.ylabel("Rating promedio")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def build_cluster_top_movies(df_clustered: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    frames = []
    for cluster_label in sorted(df_clustered["cluster"].unique()):
        movies = get_cluster_movies(df_clustered, cluster_label, top_n=top_n).copy()
        frames.append(movies)
    columns = [
        "cluster", "tconst", "primaryTitle", "startYear", "genres",
        "averageRating", "numVotes", "distanceToCentroid",
    ]
    return pd.concat(frames, ignore_index=True)[columns]


def markdown_table(df: pd.DataFrame) -> str:
    columns = list(df.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def write_report(
    evaluation_df: pd.DataFrame,
    cluster_summary: pd.DataFrame,
    cluster_top_movies: pd.DataFrame,
    selected_k: int,
    forced_k: int | None,
    tables: dict[str, Path],
    figures: dict[str, Path],
) -> Path:
    best_row = evaluation_df[evaluation_df["k"] == selected_k].iloc[0]
    largest_cluster = cluster_summary.sort_values("cantidad", ascending=False).iloc[0]

    lines = [
        "# Reporte de Clustering",
        "",
        "## Objetivo",
        "",
        "Agrupar peliculas por similitud usando K-Means sobre el dataset final del ETL.",
        "",
        "## Configuracion",
        "",
        f"- Features usadas: `{', '.join(FEATURE_COLUMNS)}`",
        "- Escalado: `StandardScaler`",
        "- Evaluacion de k: `2..10` por defecto",
        f"- k seleccionado: `{selected_k}`",
        f"- Seleccion: {'manual' if forced_k is not None else 'automatica por silhouette_score'}",
        f"- Silhouette score del k seleccionado: `{best_row['silhouette_score']}`",
        "",
        "## Resumen de clusters",
        "",
        markdown_table(cluster_summary),
        "",
        "## Hallazgos principales",
        "",
        f"- El cluster mas grande es `{int(largest_cluster['cluster'])}` con {int(largest_cluster['cantidad']):,} peliculas.",
        "- `logNumVotes` se usa para reducir el efecto de escala de `numVotes`.",
        "- Los clusters deben interpretarse con sus promedios, genero principal y peliculas mas votadas.",
        "",
        "## Peliculas destacadas por cluster",
        "",
        markdown_table(cluster_top_movies[["cluster", "primaryTitle", "startYear", "averageRating", "numVotes"]]),
        "",
        "## Artefactos generados",
        "",
    ]

    for name, path in tables.items():
        lines.append(f"- Tabla `{name}`: `{path.relative_to(PROJECT_ROOT).as_posix()}`")
    for name, path in figures.items():
        lines.append(f"- Figura `{name}`: `{path.relative_to(PROJECT_ROOT).as_posix()}`")

    lines.extend([
        f"- Dataset clusterizado: `{CLUSTERED_DATASET_PATH.relative_to(PROJECT_ROOT).as_posix()}`",
        f"- Modelo: `{MODEL_PATH.relative_to(PROJECT_ROOT).as_posix()}`",
        "",
        "## Siguiente paso",
        "",
        "Usar `movies_clustered.csv` para alimentar recomendaciones y reemplazar datos estaticos del dashboard.",
        "",
    ])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


def run_clustering(
    dataset_path=None,
    k: int | None = None,
    k_min: int = 2,
    k_max: int = 10,
    random_state: int = 42,
    silhouette_sample_size: int = 10000,
) -> dict[str, Path]:
    """Ejecuta evaluacion, entrenamiento y reporte de clustering."""
    path = Path(dataset_path) if dataset_path is not None else get_final_dataset_path()
    df = pd.read_csv(path)

    evaluation_df = evaluate_kmeans(
        df,
        k_values=range(k_min, k_max + 1),
        random_state=random_state,
        silhouette_sample_size=silhouette_sample_size,
    )
    selected_k = int(k) if k is not None else select_best_k(evaluation_df)
    model, scaler, df_clustered = train_kmeans(df, n_clusters=selected_k, random_state=random_state)

    cluster_summary = get_cluster_info(df_clustered)
    cluster_top_movies = build_cluster_top_movies(df_clustered, top_n=5)

    CLUSTERED_DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clustered.to_csv(CLUSTERED_DATASET_PATH, index=False, encoding="utf-8")
    save_model(model, scaler, MODEL_PATH, feature_columns=FEATURE_COLUMNS)

    tables = {
        "kmeans_evaluation": save_table(evaluation_df, REPORTS_TABLES / "kmeans_evaluation.csv"),
        "cluster_summary": save_table(cluster_summary, REPORTS_TABLES / "cluster_summary.csv"),
        "cluster_top_movies": save_table(cluster_top_movies, REPORTS_TABLES / "cluster_top_movies.csv"),
    }
    figures = {
        "kmeans_elbow": save_kmeans_elbow_plot(evaluation_df, REPORTS_FIGURES / "kmeans_elbow.png"),
        "kmeans_silhouette": save_silhouette_plot(evaluation_df, REPORTS_FIGURES / "kmeans_silhouette.png"),
        "cluster_distribution": save_cluster_distribution_plot(cluster_summary, REPORTS_FIGURES / "cluster_distribution.png"),
        "cluster_rating_runtime": save_cluster_scatter_plot(df_clustered, REPORTS_FIGURES / "cluster_rating_runtime.png"),
    }
    report = write_report(evaluation_df, cluster_summary, cluster_top_movies, selected_k, k, tables, figures)

    return {
        **tables,
        **figures,
        "clustered_dataset": CLUSTERED_DATASET_PATH,
        "model": MODEL_PATH,
        "report": report,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Ejecuta clustering K-Means sobre movies_dataset.csv")
    parser.add_argument("--dataset", default=None, help="Ruta opcional al dataset final")
    parser.add_argument("--k", type=int, default=None, help="k manual. Si se omite, se elige por silhouette_score")
    parser.add_argument("--k-min", type=int, default=2, help="k minimo para evaluacion automatica")
    parser.add_argument("--k-max", type=int, default=10, help="k maximo para evaluacion automatica")
    parser.add_argument("--silhouette-sample-size", type=int, default=10000, help="Muestra usada para silhouette_score")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    artifacts = run_clustering(
        dataset_path=args.dataset,
        k=args.k,
        k_min=args.k_min,
        k_max=args.k_max,
        silhouette_sample_size=args.silhouette_sample_size,
    )
    print("Clustering generado:")
    for name, path in artifacts.items():
        print(f"- {name}: {path}")
