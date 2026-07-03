import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def summary_stats(df):
    """Retorna estadísticas descriptivas del DataFrame."""
    return df.describe()


def plot_distribution(df, column):
    """Grafica la distribución de una columna numérica."""
    plt.figure(figsize=(8, 5))
    sns.histplot(df[column], kde=True)
    plt.title(f"Distribución de {column}")
    plt.show()


def plot_correlation_matrix(df):
    """Grafica la matriz de correlación."""
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.select_dtypes(include="number").corr(), annot=True, cmap="coolwarm")
    plt.title("Matriz de correlación")
    plt.show()
