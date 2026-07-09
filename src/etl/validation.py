import pandas as pd
import numpy as np


class DataValidationError(ValueError):
    """Error personalizado cuando los datos no cumplen las reglas de validación."""


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
    """Valida el dataset final de películas con las reglas de negocio.

    Retorna True si todo está correcto. Lanza DataValidationError si algo falla.
    """
    if df["tconst"].isnull().any():
        raise DataValidationError("tconst nulo encontrado")

    if not np.issubdtype(df["startYear"].dtype, np.integer):
        raise DataValidationError("startYear no es numérico")

    if not np.issubdtype(df["runtimeMinutes"].dtype, np.integer):
        raise DataValidationError("runtimeMinutes no es numérico")

    if (df["averageRating"] < 0).any() or (df["averageRating"] > 10).any():
        raise DataValidationError("averageRating fuera del rango 0-10")

    if (df["numVotes"] < 0).any():
        raise DataValidationError("numVotes negativo")

    return True
