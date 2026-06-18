// 2_2_1_generador.ts

/**
 * Ejemplo Práctico: Relación Gramática-Lenguaje
 * Lenguaje: L = { a^n b^n | n >= 1 } (Cadenas con igual cantidad de 'a' y 'b')
 * Reglas de Producción:
 * 1. S -> aSb
 * 2. S -> ab
 */

class GramaticaGeneradora {
  // Simula el mecanismo de derivación iterativa
  static derivar(pasos: number): string {
    let cadena = "S"; // Símbolo Inicial
    console.log(`[Inicio] Cadena actual: ${cadena}`);

    // Aplicamos la regla recursiva: S -> aSb
    for (let i = 0; i < pasos; i++) {
      cadena = cadena.replace("S", "aSb");
      console.log(`[Derivación Paso ${i + 1}] Aplicando (S -> aSb): ${cadena}`);
    }
    
    // Aplicamos la regla terminal para finalizar: S -> ab
    cadena = cadena.replace("S", "ab");
    console.log(`[Finalización] Aplicando (S -> ab): ${cadena}`);
    
    return cadena;
  }
}

console.log("==================================================");
console.log(" DEMOSTRACIÓN: GENERACIÓN DE LENGUAJE (PARTE 2.2.1)");
console.log("==================================================\n");

// Ejecutamos una derivación de 3 niveles de profundidad
const palabraGenerada = GramaticaGeneradora.derivar(3);

console.log("\n==================================================");
console.log(` Palabra válida generada perteneciente al lenguaje: ${palabraGenerada}`);
console.log("==================================================\n");