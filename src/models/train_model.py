from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


def split_data(df, target_col, test_size=0.2, random_state=42):
    """Divide los datos en entrenamiento y prueba."""
    X = df.drop(columns=[target_col])
    y = df[target_col]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def train_model(df, target_col):
    """Entrena un modelo Random Forest."""
    X_train, X_test, y_train, y_test = split_data(df, target_col)
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)
    return model, X_test, y_test
