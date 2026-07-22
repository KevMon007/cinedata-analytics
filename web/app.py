from flask import Flask, render_template, request

from web import data as web_data

app = Flask(__name__)


CLUSTER_MOVIES = [
    {
        "title": "Blade Runner 2049",
        "year": 2017,
        "genre": "Sci-Fi / Drama",
        "rating": 8.0,
        "votes": 540000,
        "similarity": 94,
        "cluster": 2,
        "description": "Visual, contemplativa y futurista. Explora identidad y memoria en un mundo distopico.",
        "reasons": [
            "Mismo cluster que tu pelicula de referencia (Cluster 2)",
            "Duracion similar: 164 min vs 169 min de Interstellar",
            "Calificacion en el mismo rango: 8.0 vs 8.7",
        ],
    },
    {
        "title": "Arrival",
        "year": 2016,
        "genre": "Sci-Fi / Drama",
        "rating": 7.9,
        "votes": 620000,
        "similarity": 91,
        "cluster": 2,
        "description": "Minimalista, cerebral y atmosferica. Un equipo linguistica descifra el lenguaje alienigena.",
        "reasons": [
            "Comparte cluster con peliculas de ciencia ficcion dramatica",
            "Mismo rango de calificacion: 7.9",
            "Año de estreno cercano al periodo del cluster",
        ],
    },
    {
        "title": "The Martian",
        "year": 2015,
        "genre": "Sci-Fi / Adventure",
        "rating": 8.0,
        "votes": 810000,
        "similarity": 88,
        "cluster": 2,
        "description": "Supervivencia, ciencia y humor. Un astronauta queda varado en Marte y debe encontrar la forma de regresar.",
        "reasons": [
            "Grupo de peliculas de ciencia ficcion con alto rating",
            "Duracion de 144 min dentro del rango del cluster",
            "Popularidad alta con 810K votos",
        ],
    },
    {
        "title": "Ex Machina",
        "year": 2014,
        "genre": "Sci-Fi / Thriller",
        "rating": 7.7,
        "votes": 530000,
        "similarity": 85,
        "cluster": 2,
        "description": "Inteligencia artificial, ética y tensión psicologica en un entorno aislado.",
        "reasons": [
            "Mismo cluster: ciencia ficcion con tematica filosofica",
            "Duracion de 108 min, dentro del rango del cluster",
            "Calificacion consistente con el grupo",
        ],
    },
]


CLUSTER_INFO = {
    "id": 2,
    "name": "Ciencia Ficcion Dramatica",
    "genre": "Sci-Fi / Drama",
    "avg_runtime": "146 min",
    "avg_rating": "7.9",
    "year_range": "2010-2020",
    "movie_count": 342,
}


DASHBOARD_METRICS = [
    {"label": "Peliculas analizadas", "value": "311,989", "detail": "dataset IMDb depurado"},
    {"label": "Clusters formados", "value": "5", "detail": "K-Means optimal"},
    {"label": "Rating promedio", "value": "6.8", "detail": "escala 0-10"},
    {"label": "Periodo cubierto", "value": "1905-2024", "detail": "rango historico"},
]


CLUSTER_DISTRIBUTION = [
    {"label": "Cluster 0", "value": 85, "count": "78,450"},
    {"label": "Cluster 1", "value": 72, "count": "66,200"},
    {"label": "Cluster 2", "value": 60, "count": "55,100"},
    {"label": "Cluster 3", "value": 45, "count": "41,500"},
    {"label": "Cluster 4", "value": 38, "count": "35,000"},
]


RATING_TRENDS = [
    {"label": "1990", "value": 52},
    {"label": "1995", "value": 55},
    {"label": "2000", "value": 58},
    {"label": "2005", "value": 62},
    {"label": "2010", "value": 69},
    {"label": "2015", "value": 73},
    {"label": "2020", "value": 71},
    {"label": "2024", "value": 76},
]


@app.route("/")
def index():
    try:
        cluster_top_df = web_data.load_cluster_top_movies()
        recommendations = web_data.get_preview_recommendations_from_cluster_top(cluster_top_df)
    except web_data.WebDataError:
        recommendations = CLUSTER_MOVIES

    return render_template("index.html", recommendations=recommendations)


@app.route("/dashboard")
def dashboard():
    data_error = None

    try:
        movies_df = web_data.load_clustered_movies()
        cluster_summary_df = web_data.load_cluster_summary()
        evaluation_df = web_data.load_kmeans_evaluation()
        context = web_data.build_dashboard_context(movies_df, cluster_summary_df, evaluation_df)
    except web_data.WebDataError as exc:
        data_error = str(exc)
        context = {
            "metrics": DASHBOARD_METRICS,
            "clusters": CLUSTER_DISTRIBUTION,
            "trends": RATING_TRENDS,
        }

    return render_template(
        "dashboard.html",
        metrics=context["metrics"],
        clusters=context["clusters"],
        trends=context["trends"],
        data_error=data_error,
    )


@app.route("/resultado", methods=["POST"])
def resultado():
    preferences = request.form.to_dict()
    return render_template(
        "resultado.html",
        preferences=preferences,
        recommendations=CLUSTER_MOVIES,
        cluster_info=CLUSTER_INFO,
    )


if __name__ == "__main__":
    app.run(debug=True)
