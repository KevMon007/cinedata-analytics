from src.etl.pipeline import run_pipeline
from src.explorer.summary import summarize_imdb_file
from src.utils.paths import get_title_basics_path, get_title_ratings_path


def _print_separator(char="=", width=60):
    print(char * width)


def _print_summary(summary: dict):
    """Imprime el dict resumen formateado en consola."""
    _print_separator()
    print(f"  {summary['name']}")
    _print_separator("-")
    print(f"  Filas:    {summary['rows']:,}")
    print(f"  Columnas: {summary['columns']}")
    _print_separator("-")
    print("  Columnas")
    for col in summary["column_names"]:
        print(f"    {col}")
    _print_separator("-")
    print("  Tipos de datos")
    for col, dtype in summary["dtypes"].items():
        print(f"    {col}: {dtype}")
    if summary["missing_values"]:
        _print_separator("-")
        print("  Valores nulos")
        for col, count in summary["missing_values"].items():
            print(f"    {col}: {count:,}")
    _print_separator("-")
    print(f"  Duplicados: {summary['duplicates']:,}")
    if summary["head"]:
        _print_separator("-")
        print("  Primeros registros")
        for i, row in enumerate(summary["head"], 1):
            print(f"    [{i}] {dict(list(row.items())[:5])}")
    _print_separator()


def main():
    while True:
        print("""
IMDb Movies Project

1. Explorar title.basics
2. Explorar title.ratings
3. Ejecutar ETL
4. Salir
""")
        option = input("Seleccione una opción: ").strip()

        if option == "1":
            summary = summarize_imdb_file(str(get_title_basics_path()))
            _print_summary(summary)

        elif option == "2":
            summary = summarize_imdb_file(str(get_title_ratings_path()))
            _print_summary(summary)

        elif option == "3":
            print("Ejecutando pipeline ETL...")
            df = run_pipeline()
            print(f"Dataset generado con {len(df):,} registros.")

        elif option == "4":
            print("Saliendo...")
            break

        else:
            print("Opción inválida. Intente de nuevo.")


if __name__ == "__main__":
    main()
