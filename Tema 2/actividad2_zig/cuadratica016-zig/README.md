# Ecuación de segundo grado — Zig 0.16.x

Implementación del benchmark `a·x² + b·x + c = 0` sobre vectores de `N = 200`
elementos, repetida `REPS = 100 000` veces. Archivo fuente: `cuadratica016.zig`.

---

## 1. Configuración del entorno

### macOS

```bash
brew install zig
```

### Linux (Debian / Ubuntu)

```bash
# Descargar el tarball oficial para tu arquitectura desde https://ziglang.org/download/
wget https://ziglang.org/download/0.16.0/zig-linux-x86_64-0.16.0.tar.xz
tar -xf zig-linux-x86_64-0.16.0.tar.xz
# Agregar al PATH (ajustar la ruta si es necesario)
export PATH="$PWD/zig-linux-x86_64-0.16.0:$PATH"
```

### Windows

Descargar el instalador `.zip` desde https://ziglang.org/download/, extraer y
agregar la carpeta al PATH del sistema.

### Verificar instalación

```bash
zig version
# Salida esperada: 0.16.0  (o superior)
```

---

## 2. Compilar

Situarse en esta carpeta y ejecutar:

```bash
zig build-exe cuadratica016.zig -O ReleaseFast
```

Esto genera el ejecutable `cuadratica016` (Linux/macOS) o `cuadratica016.exe`
(Windows) en el mismo directorio. No requiere dependencias externas ni gestor
de paquetes.

---

## 3. Ejecutar

```bash
./cuadratica016
```

---

## 4. Reproducir el escenario de pruebas empíricas

### 4.1 Parámetros fijos del benchmark

| Parámetro | Valor   | Descripción                             |
|-----------|---------|-----------------------------------------|
| `N`       | 200     | Elementos por vector                    |
| `REPS`    | 100 000 | Repeticiones del cálculo completo       |
| `SEED`    | 1234567 | Semilla del PRNG — resultados reproducibles |

Estos valores están definidos como constantes al inicio de `cuadratica016.zig`
y son idénticos en las implementaciones Python / Rust / JavaScript del equipo.

### 4.2 Pasos exactos para reproducir

```bash
# 1. Compilar en modo ReleaseFast (obligatorio para el benchmark)
zig build-exe cuadratica016.zig -O ReleaseFast

# 2. Ejecutar al menos 3 veces y anotar "Tiempo TOTAL"
./cuadratica016
./cuadratica016
./cuadratica016

# 3. Medir memoria pico (elegir según SO)

# macOS:
/usr/bin/time -l ./cuadratica016 2>&1 | grep "maximum resident"

# Linux:
/usr/bin/time -v ./cuadratica016 2>&1 | grep "Maximum resident"
```

### 4.3 Salida esperada

```
==== Benchmark Ecuacion 2do grado (Zig 0.16) ====
N                       : 200
REPS                    : 100000
Total de ecuaciones     : 20000000
--------------------------------------------
Raices reales (2)       : 123
Raiz doble (1)          : 0
Raices complejas        : 77
Checksum                : 9207065.501368
--------------------------------------------
Memoria vectores trabajo: 4800 bytes
Tiempo TOTAL            : ~66 ms
Tiempo PROMEDIO por rep : ~0.000660 ms
```

Los valores de clasificación y checksum son deterministas (dependen de `SEED`).
Los tiempos varían según el hardware.

### 4.4 Resultados obtenidos (hardware de referencia)

| Parámetro             | Valor                         |
|-----------------------|-------------------------------|
| CPU                   | Apple M1 Pro                  |
| RAM                   | 16 GB LPDDR5                  |
| Sistema Operativo     | macOS 15.5 (Sequoia)          |
| Compilador            | Zig 0.16.0, `-O ReleaseFast`  |
| Tiempo total (3 runs) | 64 ms / 66 ms / 70 ms         |
| Tiempo promedio/rep   | ~0.000660 ms                  |
| Memoria pico (RSS)    | ~1.23 MB (1 294 336 bytes)    |

> Para que la comparación entre lenguajes sea válida, todos los programas
> deben ejecutarse en la **misma máquina** y sin cargas pesadas en segundo plano.
