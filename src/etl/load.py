from pathlib import Path

import pandas as pd


def load_csv(df, filepath):
    """Guarda un DataFrame en CSV creando la carpeta si no existe."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False, encoding="utf-8")


def load_parquet(df, filepath):
    """Guarda un DataFrame en formato Parquet creando la carpeta si no existe."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(filepath, index=False)
