import pandas as pd
import numpy as np


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


KEEP_COLUMNS = [
    "tconst", "primaryTitle", "originalTitle", "isAdult",
    "startYear", "runtimeMinutes", "genres",
    "averageRating", "numVotes"
]


def clean_title_basics(df):
    """Filtra solo películas, elimina nulos y convierte tipos."""
    df = df.copy()
    df = df[df["titleType"] == "movie"]
    df = df.dropna(subset=["startYear", "runtimeMinutes"])
    df["startYear"] = df["startYear"].astype(int)
    df["runtimeMinutes"] = df["runtimeMinutes"].astype(int)
    return df


def clean_title_ratings(df):
    """Limpieza ligera de ratings (elimina filas con tconst nulo)."""
    return df.dropna(subset=["tconst"])


def merge_movies_ratings(basics_df, ratings_df):
    """Une películas limpias con ratings mediante inner join en tconst."""
    df = basics_df.merge(ratings_df, on="tconst", how="inner")
    return df[KEEP_COLUMNS]
