import pytest
import pandas as pd
import numpy as np
from src.etl.transform import (
    clean_dataframe, fill_missing_values,
    clean_title_basics, clean_title_ratings, merge_movies_ratings
)


def test_clean_dataframe_removes_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [4, 4, 5]})
    result = clean_dataframe(df)
    assert len(result) == 2


def test_fill_missing_values_median():
    df = pd.DataFrame({"a": [1, None, 3], "b": [4, 5, 6]})
    result = fill_missing_values(df, strategy="median")
    assert result["a"].iloc[1] == 2.0


def test_clean_title_basics_filters_only_movies():
    df = pd.DataFrame({
        "tconst": ["tt1", "tt2"],
        "titleType": ["movie", "short"],
        "startYear": [2000, 2001],
        "runtimeMinutes": [120, 10],
        "primaryTitle": ["A", "B"],
        "originalTitle": ["A", "B"],
        "isAdult": [0, 0],
        "genres": ["Drama", "Comedy"]
    })
    result = clean_title_basics(df)
    assert list(result["tconst"]) == ["tt1"]


def test_clean_title_basics_drops_null_year():
    df = pd.DataFrame({
        "tconst": ["tt1", "tt2"],
        "titleType": ["movie", "movie"],
        "startYear": [2000, None],
        "runtimeMinutes": [120, 90],
        "primaryTitle": ["A", "B"],
        "originalTitle": ["A", "B"],
        "isAdult": [0, 0],
        "genres": ["Drama", "Comedy"]
    })
    result = clean_title_basics(df)
    assert list(result["tconst"]) == ["tt1"]


def test_clean_title_basics_drops_null_runtime():
    df = pd.DataFrame({
        "tconst": ["tt1", "tt2"],
        "titleType": ["movie", "movie"],
        "startYear": [2000, 2001],
        "runtimeMinutes": [120, None],
        "primaryTitle": ["A", "B"],
        "originalTitle": ["A", "B"],
        "isAdult": [0, 0],
        "genres": ["Drama", "Comedy"]
    })
    result = clean_title_basics(df)
    assert list(result["tconst"]) == ["tt1"]


def test_clean_title_basics_converts_types():
    df = pd.DataFrame({
        "tconst": ["tt1"],
        "titleType": ["movie"],
        "startYear": [2000.0],
        "runtimeMinutes": [120.0],
        "primaryTitle": ["A"],
        "originalTitle": ["A"],
        "isAdult": [0],
        "genres": ["Drama"]
    })
    result = clean_title_basics(df)
    assert result["startYear"].dtype == int
    assert result["runtimeMinutes"].dtype == int


def test_clean_title_ratings():
    df = pd.DataFrame({
        "tconst": ["tt1", None, "tt3"],
        "averageRating": [7.0, 6.0, 8.0],
        "numVotes": [100, 50, 200]
    })
    result = clean_title_ratings(df)
    assert list(result["tconst"]) == ["tt1", "tt3"]


def test_merge_movies_ratings():
    basics = pd.DataFrame({
        "tconst": ["tt1", "tt2", "tt3"],
        "titleType": ["movie", "movie", "movie"],
        "startYear": [2000, 2001, 2002],
        "runtimeMinutes": [120, 90, 100],
        "primaryTitle": ["A", "B", "C"],
        "originalTitle": ["A", "B", "C"],
        "isAdult": [0, 0, 0],
        "genres": ["Drama", "Comedy", "Action"]
    })
    ratings = pd.DataFrame({
        "tconst": ["tt1", "tt3"],
        "averageRating": [7.5, 8.0],
        "numVotes": [100, 200]
    })
    result = merge_movies_ratings(basics, ratings)
    assert list(result["tconst"]) == ["tt1", "tt3"]
    expected = {"tconst", "primaryTitle", "originalTitle", "isAdult",
                "startYear", "runtimeMinutes", "genres",
                "averageRating", "numVotes"}
    assert set(result.columns) == expected
