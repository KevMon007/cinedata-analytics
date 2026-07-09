import pandas as pd
import numpy as np

from src.utils.paths import (
    MIN_YEAR, MAX_YEAR, MIN_RUNTIME, MAX_RUNTIME, MIN_NUM_VOTES,
)


def drop_duplicates(df):
    """Elimina filas duplicadas."""
    return df.drop_duplicates()


def fill_missing_values(df, strategy="median"):
    """Rellena valores faltantes con la estrategia indicada."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            if strategy == "median":
                df[col] = df[col].fillna(df[col].median())
            elif strategy == "mean":
                df[col] = df[col].fillna(df[col].mean())
    return df


def clean_dataframe(df):
    """Limpieza general del DataFrame."""
    df = df.copy()
    df = drop_duplicates(df)
    df = df.dropna(how="all")
    return df


INPUT_BASICS_COLUMNS = [
    "tconst", "titleType", "primaryTitle", "originalTitle",
    "isAdult", "startYear", "runtimeMinutes", "genres",
]

INPUT_RATINGS_COLUMNS = [
    "tconst", "averageRating", "numVotes",
]

KEEP_COLUMNS = [
    "tconst", "primaryTitle", "originalTitle", "isAdult",
    "startYear", "runtimeMinutes", "genres",
    "averageRating", "numVotes"
]


def _validate_input_columns(df: pd.DataFrame, required: list[str], name: str = "DataFrame") -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{name}: faltan columnas requeridas: {missing}")


def clean_title_basics(df):
    """Filtra solo películas, limpia tipos y aplica rangos configurables."""
    _validate_input_columns(df, INPUT_BASICS_COLUMNS, "clean_title_basics")

    df = df.copy()
    df = df[df["titleType"] == "movie"]

    selected_columns = [
        "tconst", "primaryTitle", "originalTitle", "isAdult",
        "startYear", "runtimeMinutes", "genres",
    ]
    df = df[selected_columns]

    if df.empty:
        return df

    df["startYear"] = pd.to_numeric(df["startYear"], errors="coerce")
    df["runtimeMinutes"] = pd.to_numeric(df["runtimeMinutes"], errors="coerce")
    df = df.dropna(subset=["tconst", "primaryTitle", "startYear", "runtimeMinutes"])
    df = df[
        df["startYear"].between(MIN_YEAR, MAX_YEAR)
        & df["runtimeMinutes"].between(MIN_RUNTIME, MAX_RUNTIME)
    ]
    df["primaryTitle"] = df["primaryTitle"].astype(str).str.strip()
    df["originalTitle"] = df["originalTitle"].astype(str).str.strip()
    df["genres"] = df["genres"].fillna("Unknown").astype(str).str.strip()
    df["isAdult"] = df["isAdult"].fillna(0).astype(int)
    df = df.drop_duplicates(subset=["tconst"])
    df["startYear"] = df["startYear"].astype(int)
    df["runtimeMinutes"] = df["runtimeMinutes"].astype(int)
    return df.reset_index(drop=True)


def clean_title_ratings(df):
    """Limpieza de ratings: elimina nulos, convierte tipos y filtra rangos."""
    _validate_input_columns(df, INPUT_RATINGS_COLUMNS, "clean_title_ratings")

    df = df.copy()
    df = df.dropna(subset=["tconst"])

    if df.empty:
        return df

    df["averageRating"] = pd.to_numeric(df["averageRating"], errors="coerce")
    df["numVotes"] = pd.to_numeric(df["numVotes"], errors="coerce")
    df = df.dropna(subset=["averageRating", "numVotes"])
    df = df[df["averageRating"].between(0, 10)]
    df = df[df["numVotes"] >= MIN_NUM_VOTES]
    df = df.drop_duplicates(subset=["tconst"])
    df["numVotes"] = df["numVotes"].astype(int)
    return df.reset_index(drop=True)


def merge_movies_ratings(basics_df, ratings_df):
    """Une películas limpias con ratings mediante inner join en tconst."""
    df = basics_df.merge(ratings_df, on="tconst", how="inner")
    return df[KEEP_COLUMNS]
