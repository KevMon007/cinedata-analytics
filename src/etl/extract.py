import pandas as pd


def extract_csv(filepath):
    """Extrae datos desde un archivo CSV."""
    return pd.read_csv(filepath)


def extract_tsv_gz(filepath):
    """Extrae datos desde un archivo TSV comprimido (.tsv.gz) estilo IMDb."""
    return pd.read_csv(filepath, sep="\t", na_values="\\N", low_memory=False)


def extract_from_api(url, params=None):
    """Extrae datos desde una API REST."""
    import requests
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
