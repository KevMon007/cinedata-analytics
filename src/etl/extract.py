from pathlib import Path

import pandas as pd

from src.utils.paths import get_title_basics_path, get_title_ratings_path


class DataFileNotFoundError(FileNotFoundError):
    """Error personalizado cuando un archivo de datos no existe."""


class EmptyDataFileError(ValueError):
    """Error personalizado cuando un archivo de datos está vacío."""


class MissingColumnsError(ValueError):
    """Error personalizado cuando faltan columnas esperadas."""


TITLE_BASICS_COLUMNS = [
    "tconst",
    "titleType",
    "primaryTitle",
    "originalTitle",
    "isAdult",
    "startYear",
    "endYear",
    "runtimeMinutes",
    "genres",
]

TITLE_RATINGS_COLUMNS = [
    "tconst",
    "averageRating",
    "numVotes",
]


def _validate_file_exists(file_path: Path) -> None:
    if not file_path.exists():
        raise DataFileNotFoundError(
            f"No se encontró el archivo: {file_path}\n"
            "Verifica que el archivo exista dentro de data/raw/."
        )


def _validate_file_not_empty(file_path: Path) -> None:
    if file_path.stat().st_size == 0:
        raise EmptyDataFileError(f"El archivo está vacío: {file_path}")


def validate_expected_columns(df: pd.DataFrame, expected_columns: list[str]) -> None:
    """Valida que un DataFrame contenga las columnas esperadas."""
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        raise MissingColumnsError(f"Faltan columnas esperadas: {missing_columns}")


def extract_csv(filepath):
    """Extrae datos desde un archivo CSV."""
    file_path = Path(filepath)
    _validate_file_exists(file_path)
    _validate_file_not_empty(file_path)

    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError as exc:
        raise EmptyDataFileError(f"El archivo está vacío: {file_path}") from exc


def extract_tsv_gz(filepath, expected_columns=None):
    """Extrae datos desde un archivo TSV comprimido (.tsv.gz) estilo IMDb."""
    file_path = Path(filepath)
    _validate_file_exists(file_path)
    _validate_file_not_empty(file_path)

    try:
        df = pd.read_csv(file_path, sep="\t", na_values="\\N", low_memory=False)
    except pd.errors.EmptyDataError as exc:
        raise EmptyDataFileError(f"El archivo está vacío: {file_path}") from exc

    if expected_columns is not None:
        validate_expected_columns(df, expected_columns)

    return df


def extract_from_api(url, params=None):
    """Extrae datos desde una API REST."""
    import requests
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def load_title_basics():
    """Carga el archivo title.basics.tsv.gz desde data/raw/."""
    return extract_tsv_gz(get_title_basics_path(), expected_columns=TITLE_BASICS_COLUMNS)


def load_title_ratings():
    """Carga el archivo title.ratings.tsv.gz desde data/raw/."""
    return extract_tsv_gz(get_title_ratings_path(), expected_columns=TITLE_RATINGS_COLUMNS)
