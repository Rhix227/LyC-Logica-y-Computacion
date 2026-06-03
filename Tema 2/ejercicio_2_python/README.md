# 🐍 Actividad II: Benchmarking de Procesamiento Intensivo - Módulo Python

Este módulo contiene la implementación algorítmica en Python diseñada para resolver el **Ejercicio 2**: Cálculo masivo de la ecuación de segundo grado utilizando vectores de coeficientes $a$, $b$ y $c$ con una dimensión estricta de $n = 200$ elementos. 

El script integra de forma nativa instrumentación de alta resolución para capturar el tiempo de ejecución preciso y el consumo de memoria pico, proporcionando las métricas requeridas para la matriz comparativa de la cátedra.

## 🛠️ Requisitos del Entorno
* **Entorno de Ejecución:** Python 3.10 o superior instalado globalmente.
* **Dependencias:** Ninguna (el script utiliza exclusivamente los módulos estándar del núcleo: `time`, `tracemalloc` y `random`).

## 📦 Estructura de Archivos del Módulo
```text
📂 python/
 └── 📄 benchmark_segundo_grado.py  # Código fuente principal instrumentado
🚀 Instrucciones de Configuración y Ejecución
Sigue estos pasos desde tu terminal para clonar, situarte en el directorio y reproducir las pruebas empíricas del entorno:

1. Navegar al directorio del módulo
Bash
cd nombre-del-repositorio/python
2. Ejecutar el script de Benchmarking
Ejecuta el programa utilizando el intérprete de Python estándar:

Bash
python benchmark_segundo_grado.py
(Nota: Si te encuentras en un entorno basado en Unix/Linux o macOS con múltiples versiones, es posible que debas invocarlo como python3 benchmark_segundo_grado.py).

📊 Salida Esperada en Terminal
Al finalizar el procesamiento de los 200 elementos, la consola desplegará las métricas bajo el siguiente formato formal:

Plaintext
==================================================
======= BENCHMARKING PYTHON - ACTIVIDAD II =======
==================================================
Tamaño del vector (n): 200
Tiempo de Ejecución Promedio: X.XXXX ms
Consumo de Memoria Pico: X.XXXXXX MB
==================================================

Muestra de las primeras 3 soluciones calculadas:
Índice 0 -> Coeficientes: a=X.XX, b=X.XX, c=X.XX
         Raíces: x1=(...), x2=(...)
🧠 Resumen de Fundamentos Técnicos 
Mecanismo de Ejecución: El script es procesado por la Máquina Virtual de Python (CPython). Al no compilarse a código de máquina nativo sino a un código intermedio (Bytecode), se produce una sobrecarga de software medible en milisegundos que contrasta con los tiempos en microsegundos de lenguajes compilados de bajo nivel.

Morfología y Sintaxis: El código se rige por la regla del off-side (indentación semántica) eliminando delimitadores explícitos. Durante la ejecución del bucle, el intérprete realiza comprobaciones dinámicas de tipo (type-checking) elemento por elemento.

Gestión de Memoria: Cada número de punto flotante se empaqueta en una estructura PyFloatObject de C, almacenando metadatos para el recolector de basura y conteo de referencias, lo que incrementa el consumo de memoria pico en comparación con arrays primitivos contiguos en memoria física.
