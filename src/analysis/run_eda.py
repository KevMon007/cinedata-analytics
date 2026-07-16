from pathlib import Path

import pandas as pd

from src.analysis.eda import (
    add_derived_columns,
    clustering_feature_summary,
    correlation_matrix,
    dataset_overview,
    decade_summary,
    genre_summary,
    most_voted_movies,
    numeric_summary,
    save_bar_plot,
    save_correlation_heatmap,
    save_distribution_plot,
    save_scatter_plot,
    save_table,
    top_rated_movies,
)
from src.utils.paths import PROJECT_ROOT, REPORTS_FIGURES, REPORTS_TABLES, get_final_dataset_path


REPORT_PATH = PROJECT_ROOT / "reports" / "eda_report.md"


def _markdown_table(df: pd.DataFrame) -> str:
    columns = list(df.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def _write_report(tables: dict[str, Path], figures: dict[str, Path]) -> Path:
    overview = dict(zip(tables["dataset_summary_df"]["metric"], tables["dataset_summary_df"]["value"]))
    genres = tables["genre_summary_df"].head(5)
    decades = tables["decade_summary_df"]
    top_movies = tables["top_rated_movies_df"].head(5)
    corr = tables["correlation_matrix_df"]

    best_decade = decades.sort_values("avg_rating", ascending=False).iloc[0]
    most_common_genre = genres.iloc[0]
    votes_rating_corr = corr.loc["numVotes", "averageRating"]

    lines = [
        "# Reporte EDA",
        "",
        "## Objetivo",
        "",
        "Analizar el dataset final generado por el ETL y preparar decisiones para aprendizaje no supervisado.",
        "",
        "## Dataset",
        "",
        f"- Peliculas analizadas: {int(overview['rows']):,}",
        f"- Columnas: {int(overview['columns'])}",
        f"- Duplicados exactos: {int(overview['duplicates']):,}",
        f"- Valores faltantes totales: {int(overview['missing_values']):,}",
        f"- Periodo cubierto: {int(overview['min_year'])}-{int(overview['max_year'])}",
        f"- Rating promedio: {float(overview['avg_rating']):.2f}",
        f"- Duracion promedio: {float(overview['avg_runtime']):.2f} minutos",
        "",
        "## Hallazgos principales",
        "",
        f"- El genero mas frecuente es `{most_common_genre['genre']}` con {int(most_common_genre['movies']):,} apariciones.",
        f"- La decada con mayor rating promedio es {int(best_decade['decade'])} con {best_decade['avg_rating']:.2f}.",
        f"- La correlacion entre votos y rating es {votes_rating_corr:.3f}; para clustering conviene usar `logNumVotes` por la escala de votos.",
        "- Las variables numericas principales tienen escalas muy distintas, por lo que el modelado debe escalar features antes de entrenar.",
        "",
        "## Top peliculas por rating",
        "",
        _markdown_table(top_movies[["primaryTitle", "startYear", "averageRating", "numVotes"]]),
        "",
        "## Artefactos generados",
        "",
    ]

    for name, path in tables.items():
        if name.endswith("_df"):
            continue
        lines.append(f"- Tabla `{name}`: `{path.relative_to(PROJECT_ROOT).as_posix()}`")
    for name, path in figures.items():
        lines.append(f"- Figura `{name}`: `{path.relative_to(PROJECT_ROOT).as_posix()}`")

    lines.extend([
        "",
        "## Recomendaciones para clustering",
        "",
        "- Usar como base `startYear`, `runtimeMinutes`, `averageRating` y `logNumVotes`.",
        "- Evaluar si `decade` aporta mejor interpretabilidad que `startYear` continuo.",
        "- Tratar `genres` como variable categorica separada o usar `mainGenre` solo para interpretar clusters.",
        "- Probar varios valores de `k` con metodo del codo y silhouette score antes de fijar el numero final de clusters.",
        "- Mantener escalado de variables numericas antes de aplicar K-Means.",
        "",
    ])

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return REPORT_PATH


def run_eda(dataset_path=None) -> dict[str, Path]:
    """Genera tablas, figuras y reporte EDA para el dataset final."""
    path = Path(dataset_path) if dataset_path is not None else get_final_dataset_path()
    df = pd.read_csv(path)
    df_features = add_derived_columns(df)

    dataset_summary_df = dataset_overview(df)
    numeric_summary_df = numeric_summary(df).reset_index().rename(columns={"index": "statistic"})
    genre_summary_df = genre_summary(df, min_movies=100)
    decade_summary_df = decade_summary(df)
    top_rated_movies_df = top_rated_movies(df, top_n=20, min_votes=1000)
    most_voted_movies_df = most_voted_movies(df, top_n=20)
    correlation_matrix_df = correlation_matrix(df).reset_index().rename(columns={"index": "feature"})
    clustering_features_df = clustering_feature_summary(df).reset_index().rename(columns={"index": "statistic"})

    tables = {
        "dataset_summary": save_table(dataset_summary_df, REPORTS_TABLES / "dataset_summary.csv"),
        "numeric_summary": save_table(numeric_summary_df, REPORTS_TABLES / "numeric_summary.csv"),
        "genre_summary": save_table(genre_summary_df, REPORTS_TABLES / "genre_summary.csv"),
        "decade_summary": save_table(decade_summary_df, REPORTS_TABLES / "decade_summary.csv"),
        "top_rated_movies": save_table(top_rated_movies_df, REPORTS_TABLES / "top_rated_movies.csv"),
        "most_voted_movies": save_table(most_voted_movies_df, REPORTS_TABLES / "most_voted_movies.csv"),
        "correlation_matrix": save_table(correlation_matrix_df, REPORTS_TABLES / "correlation_matrix.csv"),
        "clustering_feature_summary": save_table(clustering_features_df, REPORTS_TABLES / "clustering_feature_summary.csv"),
        "dataset_summary_df": dataset_summary_df,
        "genre_summary_df": genre_summary_df,
        "decade_summary_df": decade_summary_df,
        "top_rated_movies_df": top_rated_movies_df,
        "correlation_matrix_df": correlation_matrix(df),
    }

    decade_plot = decade_summary_df.copy()
    decade_plot["decade_label"] = decade_plot["decade"].astype(str)

    figures = {
        "ratings_distribution": save_distribution_plot(df, "averageRating", REPORTS_FIGURES / "ratings_distribution.png"),
        "runtime_distribution": save_distribution_plot(df, "runtimeMinutes", REPORTS_FIGURES / "runtime_distribution.png"),
        "votes_distribution_log": save_distribution_plot(df_features, "logNumVotes", REPORTS_FIGURES / "votes_distribution_log.png"),
        "top_genres": save_bar_plot(genre_summary_df, "movies", "genre", REPORTS_FIGURES / "top_genres.png", "Generos mas frecuentes"),
        "movies_by_decade": save_bar_plot(decade_plot, "movies", "decade_label", REPORTS_FIGURES / "movies_by_decade.png", "Peliculas por decada"),
        "rating_vs_votes": save_scatter_plot(df_features, "logNumVotes", "averageRating", REPORTS_FIGURES / "rating_vs_votes.png"),
        "rating_vs_runtime": save_scatter_plot(df, "runtimeMinutes", "averageRating", REPORTS_FIGURES / "rating_vs_runtime.png"),
        "correlation_heatmap": save_correlation_heatmap(df, REPORTS_FIGURES / "correlation_matrix.png"),
    }

    report_path = _write_report(tables, figures)
    return {**{k: v for k, v in tables.items() if not k.endswith("_df")}, **figures, "report": report_path}


if __name__ == "__main__":
    artifacts = run_eda()
    print("EDA generado:")
    for name, path in artifacts.items():
        print(f"- {name}: {path}")
