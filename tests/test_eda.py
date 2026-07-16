import pandas as pd
import pytest

from src.analysis.eda import (
    add_derived_columns,
    correlation_matrix,
    dataset_overview,
    decade_summary,
    expand_genres,
    genre_summary,
    most_voted_movies,
    top_rated_movies,
    validate_eda_columns,
)


def sample_movies_df():
    return pd.DataFrame({
        "tconst": ["tt1", "tt2", "tt3"],
        "primaryTitle": ["Movie A", "Movie B", "Movie C"],
        "originalTitle": ["Movie A", "Movie B", "Movie C"],
        "isAdult": [0, 0, 0],
        "startYear": [1999, 2001, 2005],
        "runtimeMinutes": [100, 120, 90],
        "genres": ["Drama,Comedy", "Action", "Drama"],
        "averageRating": [8.5, 7.0, 9.0],
        "numVotes": [5000, 2000, 100],
    })


def test_validate_eda_columns_raises_when_missing_required_column():
    df = sample_movies_df().drop(columns=["genres"])

    with pytest.raises(ValueError, match="genres"):
        validate_eda_columns(df)


def test_add_derived_columns_does_not_modify_original_df():
    df = sample_movies_df()
    result = add_derived_columns(df)

    assert "decade" not in df.columns
    assert list(result["decade"]) == [1990, 2000, 2000]
    assert list(result["mainGenre"]) == ["Drama", "Action", "Drama"]
    assert list(result["genreCount"]) == [2, 1, 1]
    assert "logNumVotes" in result.columns


def test_dataset_overview_returns_expected_metrics():
    result = dataset_overview(sample_movies_df())
    metrics = dict(zip(result["metric"], result["value"]))

    assert metrics["rows"] == 3
    assert metrics["columns"] == 9
    assert metrics["min_year"] == 1999
    assert metrics["max_year"] == 2005


def test_expand_genres_creates_one_row_per_genre():
    result = expand_genres(sample_movies_df())

    assert len(result) == 4
    assert set(result["genre"]) == {"Drama", "Comedy", "Action"}
    assert "genres" not in result.columns


def test_genre_summary_filters_by_min_movies():
    result = genre_summary(sample_movies_df(), min_movies=2)

    assert list(result["genre"]) == ["Drama"]
    assert result.iloc[0]["movies"] == 2


def test_decade_summary_groups_by_decade():
    result = decade_summary(sample_movies_df())

    counts = dict(zip(result["decade"], result["movies"]))

    assert counts[1990] == 1
    assert counts[2000] == 2


def test_top_rated_movies_uses_min_votes_and_rating_order():
    result = top_rated_movies(sample_movies_df(), top_n=2, min_votes=1000)

    assert list(result["tconst"]) == ["tt1", "tt2"]


def test_most_voted_movies_sorts_by_votes():
    result = most_voted_movies(sample_movies_df(), top_n=2)

    assert list(result["tconst"]) == ["tt1", "tt2"]


def test_correlation_matrix_uses_numeric_eda_columns():
    result = correlation_matrix(sample_movies_df())

    assert list(result.columns) == ["startYear", "runtimeMinutes", "averageRating", "numVotes"]
    assert list(result.index) == ["startYear", "runtimeMinutes", "averageRating", "numVotes"]
