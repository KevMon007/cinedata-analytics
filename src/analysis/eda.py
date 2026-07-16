from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


NUMERIC_COLUMNS = ["startYear", "runtimeMinutes", "averageRating", "numVotes"]
EDA_COLUMNS = [
    "tconst", "primaryTitle", "originalTitle", "isAdult",
    "startYear", "runtimeMinutes", "genres", "averageRating", "numVotes",
]


def validate_eda_columns(df: pd.DataFrame) -> None:
    """Valida que el dataset final tenga las columnas requeridas para EDA."""
    missing = [col for col in EDA_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas para EDA: {missing}")


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega columnas utiles para analisis sin modificar el DataFrame original."""
    validate_eda_columns(df)
    result = df.copy()
    result["decade"] = (result["startYear"] // 10) * 10
    result["mainGenre"] = result["genres"].fillna("Unknown").astype(str).str.split(",").str[0].str.strip()
    result["genreCount"] = result["genres"].fillna("Unknown").astype(str).str.split(",").str.len()
    result["logNumVotes"] = np.log10(result["numVotes"] + 1)
    return result


def dataset_overview(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna metricas generales de calidad y cobertura del dataset final."""
    validate_eda_columns(df)
    metrics = {
        "rows": len(df),
        "columns": len(df.columns),
        "duplicates": int(df.duplicated().sum()),
        "missing_values": int(df.isna().sum().sum()),
        "min_year": int(df["startYear"].min()),
        "max_year": int(df["startYear"].max()),
        "avg_rating": round(float(df["averageRating"].mean()), 2),
        "median_rating": round(float(df["averageRating"].median()), 2),
        "avg_runtime": round(float(df["runtimeMinutes"].mean()), 2),
        "median_runtime": round(float(df["runtimeMinutes"].median()), 2),
        "max_votes": int(df["numVotes"].max()),
    }
    return pd.DataFrame([{"metric": key, "value": value} for key, value in metrics.items()])


def numeric_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna estadisticas descriptivas de columnas numericas relevantes."""
    validate_eda_columns(df)
    return df[NUMERIC_COLUMNS].describe().round(2)


def expand_genres(df: pd.DataFrame) -> pd.DataFrame:
    """Expande la columna genres para analizar una fila por pelicula-genero."""
    validate_eda_columns(df)
    result = df.copy()
    result["genre"] = result["genres"].fillna("Unknown").astype(str).str.split(",")
    result = result.explode("genre")
    result["genre"] = result["genre"].str.strip().replace("", "Unknown")
    return result.drop(columns=["genres"])


def genre_summary(df: pd.DataFrame, min_movies: int = 100) -> pd.DataFrame:
    """Resume cantidad, rating, duracion y votos por genero."""
    genres = expand_genres(df)
    summary = genres.groupby("genre").agg(
        movies=("tconst", "count"),
        avg_rating=("averageRating", "mean"),
        avg_runtime=("runtimeMinutes", "mean"),
        median_votes=("numVotes", "median"),
    )
    summary = summary[summary["movies"] >= min_movies]
    return summary.round(2).sort_values(["movies", "avg_rating"], ascending=[False, False]).reset_index()


def decade_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Resume cantidad, rating, duracion y votos por decada."""
    result = add_derived_columns(df)
    summary = result.groupby("decade").agg(
        movies=("tconst", "count"),
        avg_rating=("averageRating", "mean"),
        avg_runtime=("runtimeMinutes", "mean"),
        median_votes=("numVotes", "median"),
    )
    return summary.round(2).reset_index().sort_values("decade")


def top_rated_movies(df: pd.DataFrame, top_n: int = 20, min_votes: int = 1000) -> pd.DataFrame:
    """Retorna peliculas mejor calificadas con un minimo de votos."""
    validate_eda_columns(df)
    columns = ["tconst", "primaryTitle", "startYear", "genres", "averageRating", "numVotes"]
    return (
        df[df["numVotes"] >= min_votes]
        .sort_values(["averageRating", "numVotes"], ascending=[False, False])
        .head(top_n)[columns]
        .reset_index(drop=True)
    )


def most_voted_movies(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Retorna peliculas con mayor cantidad de votos."""
    validate_eda_columns(df)
    columns = ["tconst", "primaryTitle", "startYear", "genres", "averageRating", "numVotes"]
    return df.sort_values("numVotes", ascending=False).head(top_n)[columns].reset_index(drop=True)


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna matriz de correlacion para variables numericas relevantes."""
    validate_eda_columns(df)
    return df[NUMERIC_COLUMNS].corr().round(3)


def clustering_feature_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Resume variables candidatas para aprendizaje no supervisado."""
    result = add_derived_columns(df)
    columns = NUMERIC_COLUMNS + ["decade", "genreCount", "logNumVotes"]
    return result[columns].describe().round(2)


def save_table(df: pd.DataFrame, filepath) -> Path:
    """Guarda una tabla CSV creando la carpeta destino."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    return path


def save_distribution_plot(df: pd.DataFrame, column: str, filepath, bins: int = 40) -> Path:
    """Guarda histograma de una columna numerica."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    sns.histplot(df[column], bins=bins, kde=True)
    plt.title(f"Distribucion de {column}")
    plt.xlabel(column)
    plt.ylabel("Peliculas")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def save_bar_plot(data: pd.DataFrame, x: str, y: str, filepath, title: str, limit: int = 20) -> Path:
    """Guarda grafica de barras horizontal."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_data = data.head(limit).copy()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=plot_data, x=x, y=y, color="#4C78A8")
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def save_scatter_plot(df: pd.DataFrame, x: str, y: str, filepath, sample_size: int = 20000) -> Path:
    """Guarda scatter plot con muestreo para evitar graficas demasiado pesadas."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    plot_data = df.sample(n=min(sample_size, len(df)), random_state=42) if len(df) > sample_size else df
    plt.figure(figsize=(9, 5))
    sns.scatterplot(data=plot_data, x=x, y=y, alpha=0.25, s=12, edgecolor=None)
    plt.title(f"{y} vs {x}")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def save_correlation_heatmap(df: pd.DataFrame, filepath) -> Path:
    """Guarda heatmap de correlacion de variables numericas."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix(df), annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    plt.title("Matriz de correlacion")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def summary_stats(df):
    """Retorna estadisticas descriptivas del DataFrame."""
    return df.describe()


def plot_distribution(df, column):
    """Grafica la distribucion de una columna numerica en pantalla."""
    plt.figure(figsize=(8, 5))
    sns.histplot(df[column], kde=True)
    plt.title(f"Distribucion de {column}")
    plt.show()


def plot_correlation_matrix(df):
    """Grafica la matriz de correlacion en pantalla."""
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.select_dtypes(include="number").corr(), annot=True, cmap="coolwarm")
    plt.title("Matriz de correlacion")
    plt.show()
