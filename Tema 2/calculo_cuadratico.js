// calculo_cuadratico.js
const { performance } = require('perf_hooks');

// Función para generar vectores con valores aleatorios
function generarVector(n, min, max) {
    const vector = [];
    for (let i = 0; i < n; i++) {
        // Evitamos que 'a' sea 0 para que siga siendo una ecuación de 2do grado
        let val = (Math.random() * (max - min) + min);
        if (val === 0) val = 1; 
        vector.push(val);
    }
    return vector;
}

// Función central: Cálculo de la ecuación de segundo grado
function resolverEcuacion(a, b, c) {
    const discriminante = Math.pow(b, 2) - (4 * a * c);
    
    if (discriminante > 0) {
        const raiz = Math.sqrt(discriminante);
        return [
            (-b + raiz) / (2 * a),
            (-b - raiz) / (2 * a)
        ];
    } else if (discriminante === 0) {
        return [-b / (2 * a)];
    } else {
        // Para raíces complejas/imaginarias
        return ["Raíz Compleja", "Raíz Compleja"];
    }
}

// Función de Benchmarking
function ejecutarBenchmarking() {
    const n = 200;
    
    // 1. Inicialización de los vectores a, b, y c
    const vectorA = generarVector(n, -100, 100);
    const vectorB = generarVector(n, -100, 100);
    const vectorC = generarVector(n, -100, 100);
    const resultados = [];

    // 2. Medición de Memoria Inicial
    const memoriaInicial = process.memoryUsage().heapUsed;

    // 3. Inicio del cronómetro (Alta precisión)
    const inicio = performance.now();

    // 4. Procesamiento intensivo
    for (let i = 0; i < n; i++) {
        const raices = resolverEcuacion(vectorA[i], vectorB[i], vectorC[i]);
        resultados.push(raices);
    }

    // 5. Fin del cronómetro
    const fin = performance.now();
    const tiempoEjecucion = fin - inicio;

    // 6. Medición de Memoria Final y cálculo del consumo pico
    const memoriaFinal = process.memoryUsage().heapUsed;
    const consumoMemoria = (memoriaFinal - memoriaInicial) / 1024 / 1024; // Convertir a MB

    // 7. Impresión de resultados para la tabla
    console.log("=========================================");
    console.log(`BENCHMARKING JAVASCRIPT (V8) - n=${n}`);
    console.log("=========================================");
    console.log(`Tiempo de Ejecución: ${tiempoEjecucion.toFixed(4)} ms`);
    console.log(`Consumo de Memoria:  ${Math.abs(consumoMemoria).toFixed(4)} MB`);
    console.log("=========================================");
    
    // (Opcional) Imprimir el primer resultado para verificar que calcula bien
    console.log(`Muestra de cálculo (Iteración 0):`);
    console.log(`a=${vectorA[0].toFixed(2)}, b=${vectorB[0].toFixed(2)}, c=${vectorC[0].toFixed(2)}`);
    console.log(`Raíces:`, resultados[0]);
}

// Ejecutar la prueba
ejecutarBenchmarking();