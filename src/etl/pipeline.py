from src.etl.extract import TITLE_BASICS_COLUMNS, TITLE_RATINGS_COLUMNS, extract_tsv_gz
from src.etl.transform import clean_title_basics, clean_title_ratings, merge_movies_ratings
from src.etl.validation import validate_movies_dataset, validate_schema
from src.etl.load import load_csv
from src.utils.paths import get_title_basics_path, get_title_ratings_path, get_final_dataset_path


EXPECTED_COLUMNS = [
    "tconst", "primaryTitle", "originalTitle", "isAdult",
    "startYear", "runtimeMinutes", "genres",
    "averageRating", "numVotes"
]


def run_pipeline(basics_path=None, ratings_path=None, output_path=None):
    """Ejecuta el pipeline ETL completo de IMDb.

    Si no se proporcionan rutas, usa las definidas en .env o los valores por defecto.
    """
    if basics_path is None:
        basics_path = get_title_basics_path()
    if ratings_path is None:
        ratings_path = get_title_ratings_path()
    if output_path is None:
        output_path = get_final_dataset_path()

    basics = extract_tsv_gz(basics_path, expected_columns=TITLE_BASICS_COLUMNS)
    ratings = extract_tsv_gz(ratings_path, expected_columns=TITLE_RATINGS_COLUMNS)

    basics = clean_title_basics(basics)
    ratings = clean_title_ratings(ratings)
    df = merge_movies_ratings(basics, ratings)

    schema_errors = validate_schema(df, EXPECTED_COLUMNS)
    if schema_errors["missing"]:
        raise ValueError(f"Columnas faltantes: {schema_errors['missing']}")

    validate_movies_dataset(df)

    load_csv(df, output_path)
    return df


def run_pipeline_with_defaults():
    """Ejecuta el pipeline usando rutas por defecto (desde .env o configuración interna)."""
    return run_pipeline()


if __name__ == "__main__":
    run_pipeline_with_defaults()
