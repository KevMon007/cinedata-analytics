import pandas as pd

from src.etl.extract import extract_tsv_gz, DataFileNotFoundError
from src.utils.paths import get_title_basics_path, get_title_ratings_path


def summarize_dataframe(df: pd.DataFrame, name: str = "Dataset") -> dict:
    """Analiza un DataFrame y retorna un dict con la información estructurada.

    No imprime nada. El consumidor (CLI, web, etc.) decide cómo presentarlo.
    """
    missing = df.isnull().sum()
    missing_nonzero = missing[missing > 0]

    return {
        "name": name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {
            col: int(count) for col, count in missing_nonzero.items()
        },
        "duplicates": int(df.duplicated().sum()),
        "head": df.head(5).to_dict(orient="records"),
    }


def summarize_imdb_file(file_path: str) -> dict:
    """Lee un archivo IMDb TSV.GZ y retorna su resumen estructurado."""
    df = extract_tsv_gz(file_path)
    return summarize_dataframe(df, name=file_path)
