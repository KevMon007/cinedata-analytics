import pytest
import pandas as pd
from src.etl.extract import (
    DataFileNotFoundError,
    EmptyDataFileError,
    MissingColumnsError,
    TITLE_BASICS_COLUMNS,
    TITLE_RATINGS_COLUMNS,
    extract_csv,
    extract_tsv_gz,
    load_title_basics,
    load_title_ratings,
    validate_expected_columns,
)


def test_extract_csv(tmp_path):
    df_expected = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    filepath = tmp_path / "test.csv"
    df_expected.to_csv(filepath, index=False)
    df_result = extract_csv(filepath)
    pd.testing.assert_frame_equal(df_result, df_expected)


def test_extract_tsv_gz_parses_backslash_n_as_nan(tmp_path):
    import gzip
    content = b"tconst\tstartYear\truntimeMinutes\n"
    content += b"tt0000001\t1894\t1\n"
    content += b"tt0000002\t\\N\t5\n"
    filepath = tmp_path / "test.tsv.gz"
    with gzip.open(filepath, "wb") as f:
        f.write(content)
    df = extract_tsv_gz(filepath)
    assert df["startYear"].iloc[1] is None or pd.isna(df["startYear"].iloc[1])
    assert df["runtimeMinutes"].iloc[1] == 5


def test_extract_tsv_gz_missing_file_raises_clear_error(tmp_path):
    filepath = tmp_path / "missing.tsv.gz"

    with pytest.raises(DataFileNotFoundError, match="No se encontró el archivo"):
        extract_tsv_gz(filepath)


def test_extract_tsv_gz_empty_file_raises_clear_error(tmp_path):
    filepath = tmp_path / "empty.tsv.gz"
    filepath.write_bytes(b"")

    with pytest.raises(EmptyDataFileError, match="El archivo está vacío"):
        extract_tsv_gz(filepath)


def test_validate_expected_columns_passes_with_required_columns():
    df = pd.DataFrame({"tconst": ["tt1"], "averageRating": [8.0], "numVotes": [100]})

    assert validate_expected_columns(df, TITLE_RATINGS_COLUMNS) is None


def test_validate_expected_columns_raises_when_columns_are_missing():
    df = pd.DataFrame({"tconst": ["tt1"], "averageRating": [8.0]})

    with pytest.raises(MissingColumnsError, match="Faltan columnas esperadas"):
        validate_expected_columns(df, TITLE_RATINGS_COLUMNS)


def test_load_title_basics_uses_expected_columns(tmp_path, monkeypatch):
    import gzip

    filepath = tmp_path / "title.basics.tsv.gz"
    content = "\t".join(TITLE_BASICS_COLUMNS) + "\n"
    content += "tt1\tmovie\tMovie A\tMovie A\t0\t2000\t\\N\t90\tDrama\n"
    with gzip.open(filepath, "wb") as f:
        f.write(content.encode("utf-8"))

    monkeypatch.setattr("src.etl.extract.get_title_basics_path", lambda: filepath)

    df = load_title_basics()

    assert list(df.columns) == TITLE_BASICS_COLUMNS
    assert len(df) == 1


def test_load_title_ratings_uses_expected_columns(tmp_path, monkeypatch):
    import gzip

    filepath = tmp_path / "title.ratings.tsv.gz"
    content = "\t".join(TITLE_RATINGS_COLUMNS) + "\n"
    content += "tt1\t8.0\t100\n"
    with gzip.open(filepath, "wb") as f:
        f.write(content.encode("utf-8"))

    monkeypatch.setattr("src.etl.extract.get_title_ratings_path", lambda: filepath)

    df = load_title_ratings()

    assert list(df.columns) == TITLE_RATINGS_COLUMNS
    assert len(df) == 1
