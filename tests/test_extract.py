import pytest
import pandas as pd
import numpy as np
from src.etl.extract import extract_csv, extract_tsv_gz


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
