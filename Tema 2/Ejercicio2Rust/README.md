# Ejercicio 2 - Benchmark Ecuación de Segundo Grado (Rust)

## Descripción
Benchmark del algoritmo de resolución de ecuaciones de segundo grado implementado en **Rust 1.96**, usando los vectores `a`, `b`, `c` de tamaño N=200 con REPS=100,000 repeticiones para obtener tiempos medibles y comparables.

## Requisitos previos

### Windows (8.1 / 10 / 11)
1. Instalar **Rust** desde: https://rustup.rs
   - Ejecutar `rustup-init.exe`
   - Si tienes Windows 8.1: elegir opción **3** (Don't install prerequisites), luego opción **2** (Customize) y cambiar el host triple a `x86_64-pc-windows-gnu`
   - Si tienes Windows 10/11: elegir opción **1** (instalación estándar)
2. Verificar instalación:
   ```
   rustc --version
   cargo --version
   ```

### Linux / macOS
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
rustc --version
```

## Cómo compilar y ejecutar

### Desde la terminal (CMD / PowerShell / bash)
```bash
# 1. Clonar el repositorio
git clone https://github.com/Rhix227/LyC-Logica-y-Computacion.git
cd LyC-Logica-y-Computacion

# 2. Entrar a la carpeta del ejercicio
cd "Tema 2/Ejercicio2Rust"

# 3. Compilar en modo release (optimizado)
cargo build --release

# 4. Ejecutar
cargo run --release
```

> ⚠️ Usar siempre `--release` para obtener tiempos reales de benchmark. Sin esta flag el compilador no aplica optimizaciones y los tiempos serán mucho mayores.

## Parámetros del benchmark

| Parámetro | Valor |
|-----------|-------|
| N (tamaño vectores) | 200 |
| REPS (repeticiones) | 100,000 |
| SEED (generador LCG) | 1,234,567 |
| Total de ecuaciones | 20,000,000 |

## Resultados obtenidos

Ejecutado en: **Windows 8.1 / Intel**

| Métrica | Valor |
|---------|-------|
| Raíces reales (2) | 51 |
| Raíz doble (1) | 0 |
| Raíces complejas | 149 |
| Memoria vectores | 4,800 bytes |
| Tiempo TOTAL | ~72.32 ms |
| Tiempo PROMEDIO/rep | ~0.000723 ms |

## Estructura del proyecto
```
Ejercicio2Rust/
├── src/
│   └── main.rs       # Código fuente principal
├── Cargo.toml        # Configuración del proyecto
└── Cargo.lock        # Versiones exactas de dependencias
```