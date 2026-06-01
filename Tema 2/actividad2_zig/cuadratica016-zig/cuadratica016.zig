// =============================================================================
//  ECUACIÓN DE SEGUNDO GRADO SOBRE VECTORES  -  Implementación en Zig
//  Tema 2 (Lenguajes y Compiladores) - Actividad II - Ejercicio 2
//
//  Adaptado para Zig 0.16.0 (API de I/O y tiempo cambió desde 0.14.0).
//  Compilar:  zig build-exe cuadratica_016.zig -O ReleaseFast
//  Ejecutar:  ./cuadratica_016
// =============================================================================

const std = @import("std");
const c = std.c;

const N: usize = 200;
const REPS: usize = 100_000;
const SEED: u64 = 1234567;

pub fn main() void {
    var a: [N]f64 = undefined;
    var b: [N]f64 = undefined;
    var cc: [N]f64 = undefined;

    var prng = std.Random.DefaultPrng.init(SEED);
    const rand = prng.random();

    var i: usize = 0;
    while (i < N) : (i += 1) {
        a[i]  =  1.0 + rand.float(f64) * 9.0;
        b[i]  = -10.0 + rand.float(f64) * 20.0;
        cc[i] = -10.0 + rand.float(f64) * 20.0;
    }

    var reales:   usize = 0;
    var dobles:   usize = 0;
    var complejas: usize = 0;
    var checksum: f64 = 0.0;

    // Warm-up
    checksum += solveAll(&a, &b, &cc, &reales, &dobles, &complejas);
    reales = 0; dobles = 0; complejas = 0; checksum = 0.0;

    // Medición
    var ts_start: c.timespec = undefined;
    var ts_end:   c.timespec = undefined;
    _ = c.clock_gettime(c.CLOCK.MONOTONIC_RAW, &ts_start);

    var r: usize = 0;
    while (r < REPS) : (r += 1) {
        if (r == REPS - 1) {
            reales = 0; dobles = 0; complejas = 0;
            checksum += solveAll(&a, &b, &cc, &reales, &dobles, &complejas);
        } else {
            var dr: usize = 0;
            var dd: usize = 0;
            var dc: usize = 0;
            checksum += solveAll(&a, &b, &cc, &dr, &dd, &dc);
        }
    }

    _ = c.clock_gettime(c.CLOCK.MONOTONIC_RAW, &ts_end);

    const elapsed_ns: i64 = (ts_end.sec - ts_start.sec) * 1_000_000_000 +
                             (ts_end.nsec - ts_start.nsec);
    const elapsed_ms: f64  = @as(f64, @floatFromInt(elapsed_ns)) / 1_000_000.0;
    const avg_ms: f64       = elapsed_ms / @as(f64, @floatFromInt(REPS));
    const mem_bytes: usize  = 3 * N * @sizeOf(f64);

    std.debug.print("==== Benchmark Ecuacion 2do grado (Zig 0.16) ====\n", .{});
    std.debug.print("N                       : {d}\n", .{N});
    std.debug.print("REPS                    : {d}\n", .{REPS});
    std.debug.print("Total de ecuaciones     : {d}\n", .{N * REPS});
    std.debug.print("--------------------------------------------\n", .{});
    std.debug.print("Raices reales (2)       : {d}\n", .{reales});
    std.debug.print("Raiz doble (1)          : {d}\n", .{dobles});
    std.debug.print("Raices complejas        : {d}\n", .{complejas});
    std.debug.print("Checksum                : {d:.6}\n", .{checksum});
    std.debug.print("--------------------------------------------\n", .{});
    std.debug.print("Memoria vectores trabajo: {d} bytes\n", .{mem_bytes});
    std.debug.print("Tiempo TOTAL            : {d:.3} ms\n", .{elapsed_ms});
    std.debug.print("Tiempo PROMEDIO por rep : {d:.6} ms\n", .{avg_ms});
}

fn solveAll(
    a:        *const [N]f64,
    b:        *const [N]f64,
    cc:       *const [N]f64,
    reales:   *usize,
    dobles:   *usize,
    complejas: *usize,
) f64 {
    var acc: f64 = 0.0;
    var i: usize = 0;
    while (i < N) : (i += 1) {
        const disc:  f64 = b[i] * b[i] - 4.0 * a[i] * cc[i];
        const denom: f64 = 2.0 * a[i];

        if (disc > 0.0) {
            const sq: f64 = @sqrt(disc);
            const x1: f64 = (-b[i] + sq) / denom;
            const x2: f64 = (-b[i] - sq) / denom;
            reales.* += 1;
            acc += x1 + x2;
        } else if (disc == 0.0) {
            const x1: f64 = -b[i] / denom;
            dobles.* += 1;
            acc += x1;
        } else {
            const re: f64 = -b[i] / denom;
            const im: f64 = @sqrt(-disc) / denom;
            complejas.* += 1;
            acc += re + im;
        }
    }
    return acc;
}
