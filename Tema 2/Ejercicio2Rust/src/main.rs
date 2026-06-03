use std::time::Instant;

const N: usize = 200;
const REPS: u64 = 100_000;
const SEED: u64 = 1_234_567;

/// Generador LCG simple (mismo que Zig) para reproducibilidad
fn lcg(state: &mut u64) -> f64 {
    *state = state.wrapping_mul(6_364_136_223_846_793_005)
        .wrapping_add(1_442_695_040_888_963_407);
    // Mapear a rango [-10.0, 10.0]
    let bits = (*state >> 33) as f64;
    (bits / (u32::MAX as f64)) * 20.0 - 10.0
}

fn solve_all(a: &[f64; N], b: &[f64; N], c: &[f64; N]) -> f64 {
    let mut checksum = 0.0f64;
    let mut reales = 0u32;
    let mut dobles = 0u32;
    let mut complejas = 0u32;

    for i in 0..N {
        let disc = b[i] * b[i] - 4.0 * a[i] * c[i];
        if disc > 0.0 {
            let x1 = (-b[i] + disc.sqrt()) / (2.0 * a[i]);
            let x2 = (-b[i] - disc.sqrt()) / (2.0 * a[i]);
            checksum += x1 + x2;
            reales += 1;
        } else if disc == 0.0 {
            let x = -b[i] / (2.0 * a[i]);
            checksum += x;
            dobles += 1;
        } else {
            // Raíces complejas: parte real
            let real = -b[i] / (2.0 * a[i]);
            checksum += real;
            complejas += 1;
        }
    }
    // Retornar checksum + conteos codificados para evitar dead-code elimination
    checksum + reales as f64 * 0.0 + dobles as f64 * 0.0 + complejas as f64 * 0.0
}

fn main() {
    // Generar vectores con el mismo LCG y SEED que Zig
    let mut state = SEED;
    let mut a = [0.0f64; N];
    let mut b = [0.0f64; N];
    let mut c = [0.0f64; N];

    for i in 0..N {
        // Asegurar a[i] != 0
        loop {
            a[i] = lcg(&mut state);
            if a[i].abs() > 0.001 { break; }
        }
        b[i] = lcg(&mut state);
        c[i] = lcg(&mut state);
    }

    // Mostrar clasificación (una sola pasada sin medir)
    let mut reales = 0u32;
    let mut dobles = 0u32;
    let mut complejas = 0u32;
    for i in 0..N {
        let disc = b[i] * b[i] - 4.0 * a[i] * c[i];
        if disc > 0.0 { reales += 1; }
        else if disc == 0.0 { dobles += 1; }
        else { complejas += 1; }
    }

    // Warm-up
    let mut checksum = 0.0f64;
    for _ in 0..1000 {
        checksum += solve_all(&a, &b, &c);
    }

    // Benchmark real
    let start = Instant::now();
    for _ in 0..REPS {
        checksum += solve_all(&a, &b, &c);
    }
    let elapsed = start.elapsed();
    let ms = elapsed.as_secs_f64() * 1000.0;

    println!("==== Benchmark Ecuacion 2do grado (Rust 1.96) ====");
    println!("N                       : {}", N);
    println!("REPS                    : {}", REPS);
    println!("Total de ecuaciones     : {}", N as u64 * REPS);
    println!("--------------------------------------------");
    println!("Raices reales (2)       : {}", reales);
    println!("Raiz doble (1)          : {}", dobles);
    println!("Raices complejas        : {}", complejas);
    println!("Checksum                : {:.6}", checksum / (REPS as f64 + 1000.0));
    println!("--------------------------------------------");
    println!("Memoria vectores trabajo: {} bytes", N * 3 * std::mem::size_of::<f64>());
    println!("Tiempo TOTAL            : {:.2} ms", ms);
    println!("Tiempo PROMEDIO por rep : {:.9} ms", ms / REPS as f64);
}