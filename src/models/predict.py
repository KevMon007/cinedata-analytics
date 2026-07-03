import numpy as np


def predict(model, X):
    """Realiza predicciones con el modelo entrenado."""
    return model.predict(X)


def predict_proba(model, X):
    """Retorna probabilidades si el modelo lo soporta."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)
    raise AttributeError("El modelo no soporta predict_proba")
