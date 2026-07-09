import pytest
import pandas as pd
import numpy as np
from src.etl.validation import check_duplicates, validate_schema, validate_movies_dataset, DataValidationError


def test_check_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [4, 4, 5]})
    assert check_duplicates(df) == 1


def test_validate_schema():
    df = pd.DataFrame({"a": [1], "b": [2]})
    result = validate_schema(df, ["a", "b", "c"])
    assert result["missing"] == ["c"]
    assert result["extra"] == []


def test_validate_movies_dataset_passes():
    df = pd.DataFrame({
        "tconst": ["tt1", "tt2"],
        "startYear": pd.array([2000, 2001], dtype="int64"),
        "runtimeMinutes": pd.array([120, 90], dtype="int64"),
        "averageRating": [7.5, 8.0],
        "numVotes": [100, 200]
    })
    assert validate_movies_dataset(df) is True


def test_validate_movies_dataset_null_tconst():
    df = pd.DataFrame({
        "tconst": ["tt1", None],
        "startYear": pd.array([2000, 2001], dtype="int64"),
        "runtimeMinutes": pd.array([120, 90], dtype="int64"),
        "averageRating": [7.5, 8.0],
        "numVotes": [100, 200]
    })
    with pytest.raises(DataValidationError, match="tconst nulo encontrado"):
        validate_movies_dataset(df)


def test_validate_movies_dataset_rating_out_of_range():
    df = pd.DataFrame({
        "tconst": ["tt1", "tt2"],
        "startYear": pd.array([2000, 2001], dtype="int64"),
        "runtimeMinutes": pd.array([120, 90], dtype="int64"),
        "averageRating": [7.5, 11.0],
        "numVotes": [100, 200]
    })
    with pytest.raises(DataValidationError, match="averageRating fuera del rango 0-10"):
        validate_movies_dataset(df)


def test_validate_movies_dataset_negative_votes():
    df = pd.DataFrame({
        "tconst": ["tt1", "tt2"],
        "startYear": pd.array([2000, 2001], dtype="int64"),
        "runtimeMinutes": pd.array([120, 90], dtype="int64"),
        "averageRating": [7.5, 8.0],
        "numVotes": [100, -5]
    })
    with pytest.raises(DataValidationError, match="numVotes negativo"):
        validate_movies_dataset(df)
