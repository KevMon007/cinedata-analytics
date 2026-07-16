import pandas as pd

from src.etl.load import load_csv


def test_load_csv_creates_parent_directory(tmp_path):
    df = pd.DataFrame({"tconst": ["tt1"], "primaryTitle": ["Movie A"]})
    output_path = tmp_path / "nested" / "movies_dataset.csv"

    load_csv(df, output_path)

    assert output_path.exists()


def test_load_csv_saves_dataframe_without_index(tmp_path):
    df = pd.DataFrame({
        "tconst": ["tt1", "tt2"],
        "primaryTitle": ["Movie A", "Movie B"],
        "averageRating": [7.5, 8.0],
    })
    output_path = tmp_path / "movies_dataset.csv"

    load_csv(df, output_path)

    result = pd.read_csv(output_path)
    assert list(result.columns) == ["tconst", "primaryTitle", "averageRating"]
    pd.testing.assert_frame_equal(result, df)
