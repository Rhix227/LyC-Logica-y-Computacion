import time
import tracemalloc
import random

def generar_vectores(n):
    """Genera coeficientes aleatorios para simular la carga de datos."""
    # Se evitan ceros en 'a' para garantizar que sea de segundo grado
    a = [random.uniform(1.0, 10.0) for _ in range(n)]
    b = [random.uniform(-50.0, 50.0) for _ in range(n)]
    c = [random.uniform(-50.0, 50.0) for _ in range(n)]
    return a, b, c

def calcular_ecuacion_segundo_grado(a, b, c, n):
    """Calcula las raíces de la ecuación ax^2 + bx + c = 0 para vectores."""
    resultados = []
    for i in range(n):
        discriminante = b[i]**2 - 4 * a[i] * c[i]
        
        # Al trabajar con números reales, el discriminante puede ser negativo (raíces complejas)
        if discriminante >= 0:
            raiz_desc = discriminante ** 0.5
            x1 = (-b[i] + raiz_desc) / (2 * a[i])
            x2 = (-b[i] - raiz_desc) / (2 * a[i])
            resultados.append((x1, x2))
        else:
            # Raíces complejas/imaginarias
            parte_real = -b[i] / (2 * a[i])
            parte_imaginaria = (abs(discriminante) ** 0.5) / (2 * a[i])
            resultados.append((complex(parte_real, parte_imaginaria), complex(parte_real, -parte_imaginaria)))
    return resultados

if __name__ == "__main__":
    # 1. Configuración de la carga (Requisito del PDF: n = 200)
    N = 200
    a, b, c = generar_vectores(N)
    
    # 2. Iniciar el monitoreo de memoria pico
    tracemalloc.start()
    
    # 3. Iniciar el monitoreo de tiempo de ejecución (Alta precisión)
    inicio_tiempo = time.perf_counter()
    
    # 4. Ejecución del algoritmo principal
    soluciones = calcular_ecuacion_segundo_grado(a, b, c, N)
    
    # 5. Captura de métricas finales
    fin_tiempo = time.perf_counter()
    memoria_actual, memoria_pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # 6. Conversión de unidades para la tabla del informe
    tiempo_ejecucion_ms = (fin_tiempo - inicio_tiempo) * 1000
    memoria_pico_mb = memoria_pico / (1024 * 1024)
    
    # 7. Despliegue de resultados en consola
    print("=" * 50)
    print(" BENCHMARKING PYTHON - ACTIVIDAD II ".center(50, "="))
    print("=" * 50)
    print(f"Tamaño del vector (n): {N}")
    print(f"Tiempo de Ejecución Promedio: {tiempo_ejecucion_ms:.4f} ms")
    print(f"Consumo de Memoria Pico: {memoria_pico_mb:.6f} MB")
    print("=" * 50)
    
    # Muestra de cortesía de los primeros 3 resultados para verificar consistencia
    print("\nMuestra de las primeras 3 soluciones calculadas:")
    for idx in range(3):
        print(f"Índice {idx} -> Coeficientes: a={a[idx]:.2f}, b={b[idx]:.2f}, c={c[idx]:.2f}")
        print(f"         Raíces: x1={soluciones[idx][0]}, x2={soluciones[idx][1]}")
