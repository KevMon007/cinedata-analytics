from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report


def evaluate_regression(y_true, y_pred):
    """Evalúa un modelo de regresión."""
    return {
        "mse": mean_squared_error(y_true, y_pred),
        "r2": r2_score(y_true, y_pred)
    }


def evaluate_classification(y_true, y_pred):
    """Evalúa un modelo de clasificación."""
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "report": classification_report(y_true, y_pred, output_dict=True)
    }
