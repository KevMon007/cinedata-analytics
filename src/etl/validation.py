import pandas as pd
import numpy as np


def check_missing_values(df):
    """Retorna columnas con valores faltantes y su conteo."""
    return df.isnull().sum()[df.isnull().sum() > 0]


def check_duplicates(df):
    """Retorna la cantidad de filas duplicadas."""
    return df.duplicated().sum()


def validate_schema(df, expected_cols):
    """Valida que el DataFrame contenga las columnas esperadas."""
    missing = [col for col in expected_cols if col not in df.columns]
    extra = [col for col in df.columns if col not in expected_cols]
    return {"missing": missing, "extra": extra}


def validate_movies_dataset(df):
    """Valida el dataset final de películas con las reglas de negocio."""
    errors = []

    if df["tconst"].isnull().any():
        errors.append("tconst nulo encontrado")

    if not np.issubdtype(df["startYear"].dtype, np.integer):
        errors.append("startYear no es numérico")

    if not np.issubdtype(df["runtimeMinutes"].dtype, np.integer):
        errors.append("runtimeMinutes no es numérico")

    if (df["averageRating"] < 0).any() or (df["averageRating"] > 10).any():
        errors.append("averageRating fuera del rango 0-10")

    if (df["numVotes"] < 0).any():
        errors.append("numVotes negativo")

    return errors
