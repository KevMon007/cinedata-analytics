import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.utils.paths import REPORTS_FIGURES


def plot_title_types(df: pd.DataFrame, output_dir=REPORTS_FIGURES) -> str:
    """Guarda gráfica de distribución de tipos de título."""
    raise NotImplementedError("Disponible en próxima fase.")


def plot_genres_distribution(df: pd.DataFrame, output_dir=REPORTS_FIGURES) -> str:
    """Guarda gráfica de distribución de géneros."""
    raise NotImplementedError("Disponible en próxima fase.")


def plot_ratings_distribution(df: pd.DataFrame, output_dir=REPORTS_FIGURES) -> str:
    """Guarda histograma de calificaciones."""
    raise NotImplementedError("Disponible en próxima fase.")
