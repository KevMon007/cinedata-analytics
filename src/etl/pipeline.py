from pathlib import Path

from src.etl.extract import extract_tsv_gz
from src.etl.transform import clean_title_basics, clean_title_ratings, merge_movies_ratings
from src.etl.validation import validate_movies_dataset, validate_schema
from src.etl.load import load_csv


EXPECTED_COLUMNS = [
    "tconst", "primaryTitle", "originalTitle", "isAdult",
    "startYear", "runtimeMinutes", "genres",
    "averageRating", "numVotes"
]


def run_pipeline(basics_path, ratings_path, output_path):
    """Ejecuta el pipeline ETL completo de IMDb."""
    basics = extract_tsv_gz(basics_path)
    ratings = extract_tsv_gz(ratings_path)

    basics = clean_title_basics(basics)
    ratings = clean_title_ratings(ratings)
    df = merge_movies_ratings(basics, ratings)

    schema_errors = validate_schema(df, EXPECTED_COLUMNS)
    if schema_errors["missing"]:
        raise ValueError(f"Columnas faltantes: {schema_errors['missing']}")

    validation_errors = validate_movies_dataset(df)
    if validation_errors:
        raise ValueError(f"Validación fallida: {validation_errors}")

    load_csv(df, output_path)
    return df
