import pandas as pd

from src.etl.pipeline import run_pipeline


def test_run_pipeline_generates_final_csv(tmp_path):
    basics_path = tmp_path / "title.basics.tsv.gz"
    ratings_path = tmp_path / "title.ratings.tsv.gz"
    output_path = tmp_path / "final" / "movies_dataset.csv"

    basics = pd.DataFrame({
        "tconst": ["tt1", "tt2", "tt3"],
        "titleType": ["movie", "short", "movie"],
        "primaryTitle": ["Movie A", "Short B", "Movie C"],
        "originalTitle": ["Movie A", "Short B", "Movie C"],
        "isAdult": [0, 0, 0],
        "startYear": [2000, 2001, 2002],
        "endYear": ["\\N", "\\N", "\\N"],
        "runtimeMinutes": [120, 10, 95],
        "genres": ["Drama", "Comedy", "Action"],
    })
    ratings = pd.DataFrame({
        "tconst": ["tt1", "tt3", "tt99"],
        "averageRating": [7.5, 8.0, 9.0],
        "numVotes": [100, 200, 300],
    })
    basics.to_csv(basics_path, sep="\t", index=False, compression="gzip")
    ratings.to_csv(ratings_path, sep="\t", index=False, compression="gzip")

    result = run_pipeline(basics_path, ratings_path, output_path)

    assert output_path.exists()
    assert list(result["tconst"]) == ["tt1", "tt3"]

    saved = pd.read_csv(output_path)
    pd.testing.assert_frame_equal(saved, result)
