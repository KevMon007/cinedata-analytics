import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_RAW = PROJECT_ROOT / os.getenv("RAW_DATA_PATH", "data/raw")
DATA_INTERIM = PROJECT_ROOT / os.getenv("INTERIM_DATA_PATH", "data/interim")
DATA_PROCESSED = PROJECT_ROOT / os.getenv("PROCESSED_DATA_PATH", "data/processed")
DATA_FINAL = PROJECT_ROOT / os.getenv("FINAL_DATA_PATH", "data/final")

REPORTS_FIGURES = PROJECT_ROOT / os.getenv("REPORTS_FIGURES_PATH", "reports/figures")
REPORTS_TABLES = PROJECT_ROOT / os.getenv("REPORTS_TABLES_PATH", "reports/tables")

TITLE_BASICS_FILE = os.getenv("TITLE_BASICS_FILE", "title.basics.tsv.gz")
TITLE_RATINGS_FILE = os.getenv("TITLE_RATINGS_FILE", "title.ratings.tsv.gz")
FINAL_DATASET_FILE = os.getenv("FINAL_DATASET_FILE", "movies_dataset.csv")

MIN_YEAR = int(os.getenv("MIN_YEAR", "1900"))
MAX_YEAR = int(os.getenv("MAX_YEAR", "2030"))
MIN_RUNTIME = int(os.getenv("MIN_RUNTIME", "1"))
MAX_RUNTIME = int(os.getenv("MAX_RUNTIME", "500"))
MIN_NUM_VOTES = int(os.getenv("MIN_NUM_VOTES", "0"))


def get_data_path(subdir, filename):
    """Retorna la ruta completa dentro de data/<subdir>."""
    return PROJECT_ROOT / "data" / subdir / filename


def get_title_basics_path():
    """Retorna la ruta al archivo title.basics.tsv.gz."""
    return DATA_RAW / TITLE_BASICS_FILE


def get_title_ratings_path():
    """Retorna la ruta al archivo title.ratings.tsv.gz."""
    return DATA_RAW / TITLE_RATINGS_FILE


def get_final_dataset_path():
    """Retorna la ruta al archivo movies_dataset.csv."""
    return DATA_FINAL / FINAL_DATASET_FILE
