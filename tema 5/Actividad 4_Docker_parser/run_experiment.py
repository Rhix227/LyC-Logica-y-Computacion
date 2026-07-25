"""
Pregunta 4 - Experimento de carga.

Ejecuta los TRES lexer-parser (Python, Java, C) sobre los N=10 archivos
docker-compose generados por gen_samples.py, mide el TIEMPO DE EJECUCION
(wall-clock, medido externamente con subprocess para que sea comparable
entre lenguajes) repitiendo cada corrida REPS veces para reducir ruido, y
genera:
  - results/tiempos.csv            (todas las mediciones individuales)
  - results/resumen.csv             (promedio/min/max por lenguaje y archivo)
  - results/grafico_escalabilidad.png  (tiempo vs tamano de archivo, 1 linea x lenguaje)
  - results/grafico_promedio.png       (barras: tiempo promedio total por lenguaje)

Antes de ejecutar el experimento se valida que los 3 parsers produzcan
EXACTAMENTE el mismo resultado (--json) en cada archivo, para asegurar que
las diferencias medidas son de tiempo de ejecucion y no de correctitud.
"""
import csv
import json
import os
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(HERE, "samples")
RESULTS_DIR = os.path.join(HERE, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

REPS = 5  # repeticiones por archivo/lenguaje

COMMANDS = {
    "python": lambda f: ["python3", os.path.join(HERE, "python", "lexer_parser.py"), f, "--json"],
    "java":   lambda f: ["java", os.path.join(HERE, "java", "LexerParser.java"), f, "--json"],
    "c":      lambda f: [os.path.join(HERE, "c", "lexer_parser"), f, "--json"],
}


def run_once(cmd):
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    t1 = time.perf_counter()
    if proc.returncode != 0:
        raise RuntimeError(f"Fallo {cmd}: {proc.stderr}")
    return (t1 - t0) * 1000.0, proc.stdout.strip()


def validar_consistencia(files):
    print("Validando que los 3 parsers produzcan el mismo resultado...")
    for f in files:
        salidas = {}
        for lang, build in COMMANDS.items():
            _, out = run_once(build(f))
            salidas[lang] = json.loads(out)
        base = salidas["python"]
        for lang in ("java", "c"):
            if salidas[lang] != base:
                print(f"  [DIFERENCIA] {os.path.basename(f)}  python vs {lang}")
                print("   python:", base)
                print(f"   {lang}:", salidas[lang])
                raise RuntimeError("Los parsers no son consistentes entre si")
        # tamano de referencia (para graficar escalabilidad)
        yield os.path.basename(f), base["n_services"], base["n_networks"]
    print("OK: los 3 parsers son consistentes en todos los archivos.\n")


def main():
    files = sorted(
        os.path.join(SAMPLES_DIR, f) for f in os.listdir(SAMPLES_DIR) if f.endswith(".yml")
    )
    if not files:
        print("No hay archivos de muestra. Ejecute primero gen_samples.py")
        sys.exit(1)

    tamanos = list(validar_consistencia(files))

    filas = []
    print(f"Ejecutando experimento ({REPS} repeticiones por archivo/lenguaje)...")
    for f in files:
        base = os.path.basename(f)
        for lang, build in COMMANDS.items():
            cmd = build(f)
            for rep in range(REPS):
                ms, _ = run_once(cmd)
                filas.append({"lenguaje": lang, "archivo": base, "rep": rep, "tiempo_ms": ms})
            print(f"  {base:28s} {lang:8s} listo")

    # ------- CSV detallado -------
    csv_detalle = os.path.join(RESULTS_DIR, "tiempos.csv")
    with open(csv_detalle, "w", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=["lenguaje", "archivo", "rep", "tiempo_ms"])
        w.writeheader()
        w.writerows(filas)
    print(f"\nGuardado: {csv_detalle}")

    # ------- CSV resumen (promedio/min/max por lenguaje+archivo) -------
    resumen = {}
    for fila in filas:
        key = (fila["lenguaje"], fila["archivo"])
        resumen.setdefault(key, []).append(fila["tiempo_ms"])

    tam_por_archivo = {nombre: (n_serv, n_net) for nombre, n_serv, n_net in tamanos}

    csv_resumen = os.path.join(RESULTS_DIR, "resumen.csv")
    filas_resumen = []
    for (lang, archivo), valores in sorted(resumen.items()):
        n_serv, n_net = tam_por_archivo[archivo]
        filas_resumen.append({
            "lenguaje": lang,
            "archivo": archivo,
            "n_servicios": n_serv,
            "n_redes": n_net,
            "promedio_ms": round(statistics.mean(valores), 4),
            "min_ms": round(min(valores), 4),
            "max_ms": round(max(valores), 4),
        })
    with open(csv_resumen, "w", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=list(filas_resumen[0].keys()))
        w.writeheader()
        w.writerows(filas_resumen)
    print(f"Guardado: {csv_resumen}")

    graficar(filas_resumen)


def graficar(filas_resumen):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    langs = ["python", "java", "c"]
    colores = {"python": "#3776AB", "java": "#f89820", "c": "#555555"}

    # ---- Grafico 1: escalabilidad (tiempo vs numero de redes) ----
    plt.figure(figsize=(8, 5))
    for lang in langs:
        puntos = sorted(
            ((f["n_redes"], f["promedio_ms"]) for f in filas_resumen if f["lenguaje"] == lang),
            key=lambda p: p[0],
        )
        xs = [p[0] for p in puntos]
        ys = [p[1] for p in puntos]
        plt.plot(xs, ys, marker="o", label=lang, color=colores[lang])
    plt.xlabel("Numero de redes definidas en el archivo docker-compose")
    plt.ylabel("Tiempo de ejecucion promedio (ms)")
    plt.title("Experimento de carga: tiempo de ejecucion vs tamano de entrada")
    plt.legend(title="Lenguaje")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    out1 = os.path.join(RESULTS_DIR, "grafico_escalabilidad.png")
    plt.savefig(out1, dpi=150)
    plt.close()
    print(f"Guardado: {out1}")

    # ---- Grafico 2: promedio general por lenguaje (barras) ----
    plt.figure(figsize=(6, 5))
    promedios = []
    for lang in langs:
        vals = [f["promedio_ms"] for f in filas_resumen if f["lenguaje"] == lang]
        promedios.append(statistics.mean(vals))
    plt.bar(langs, promedios, color=[colores[l] for l in langs])
    for i, v in enumerate(promedios):
        plt.text(i, v, f"{v:.2f} ms", ha="center", va="bottom")
    plt.ylabel("Tiempo de ejecucion promedio (ms), todos los archivos")
    plt.title("Tiempo promedio por lenguaje (10 archivos, 5 repeticiones c/u)")
    plt.tight_layout()
    out2 = os.path.join(RESULTS_DIR, "grafico_promedio.png")
    plt.savefig(out2, dpi=150)
    plt.close()
    print(f"Guardado: {out2}")


if __name__ == "__main__":
    main()
