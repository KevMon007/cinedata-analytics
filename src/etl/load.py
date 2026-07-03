import pandas as pd


def load_csv(df, filepath):
    """Guarda un DataFrame en CSV."""
    df.to_csv(filepath, index=False)


def load_parquet(df, filepath):
    """Guarda un DataFrame en formato Parquet."""
    df.to_parquet(filepath, index=False)
