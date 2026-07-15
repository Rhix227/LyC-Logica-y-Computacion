# LexerRust — Analizador léxico para el lenguaje L (subconjunto de Rust)

Analizador léxico construido con el metacompilador **Flex 2.5.4 (GnuWin32)** para el
lenguaje **L**, un subconjunto reducido del lenguaje de programación **Rust**.

Proyecto desarrollado para la Actividad 3 del Tema 4 (Análisis Léxico) de la
asignatura **Lenguaje y Compiladores**, UNEG, periodo 2026-I.

## Descripción del lenguaje L

L admite:

- **Palabras reservadas:** `let`, `mut`, `fn`, `if`, `else`, `while`, `for`, `return`, `true`, `false`
- **Tipos:** `i32`, `f64`, `bool`, `String`
- **Macro:** `println!`
- **Literales:** enteros, flotantes, cadenas
- **Operadores:** `+ - * / == != >= <= > < =`
- **Puntuadores:** `{ } ( ) ; : ,`
- **Identificadores:** `[a-zA-Z_][a-zA-Z0-9_]*`
- **Comentarios de línea:** `//`
- **Errores léxicos** reportados para cualquier carácter no reconocido, sin detener la ejecución

## Estructura del repositorio

```
LexerRust/
├── lex.yy.c              # (generado por flex, no versionar si se prefiere)
├── lexer_rust.exe        # (generado por gcc, no versionar si se prefiere)
├── lexer_rust.l          # Especificación Flex del lexer
├── programa_prueba.rs    # Programa de ejemplo escrito en L
└── README.md
```
## Requisitos previos

| Herramienta | Versión usada | Notas |
|---|---|---|
| Flex | 2.5.4 (GnuWin32) | Instalado en `C:\Program Files (x86)\GnuWin32\bin` |
| GCC | 10.3.0 (TDM64-GCC) | Debe estar accesible en el PATH |
| Sistema operativo | Windows 8.1 | Probado en este entorno; aplicable a otras versiones de Windows |

## Instalación (Windows 8.1)

1. Descargar e instalar **GnuWin32 Flex 2.5.4**, usando la ruta de instalación por
   defecto: `C:\Program Files (x86)\GnuWin32`.
2. Descargar e instalar **TDM-GCC 10.3.0 (64 bits)**, verificando que `gcc.exe`
   quede disponible en el PATH del sistema.
3. Crear la carpeta de trabajo `C:\LexerRust` y colocar allí `lexer_rust.l` y
   `programa_prueba.rs`.
4. Abrir el **Símbolo del sistema (cmd)** y agregar Flex al PATH de la sesión actual:

   ```cmd
   set PATH=%PATH%;C:\Program Files (x86)\GnuWin32\bin
   ```

5. Verificar la instalación:

   ```cmd
   flex --version
   gcc --version
   ```

## Compilación

Desde la carpeta `C:\LexerRust`:

```cmd
flex lexer_rust.l
gcc lex.yy.c -o lexer_rust.exe
```

- `flex lexer_rust.l` genera `lex.yy.c` a partir de la especificación.
- `gcc lex.yy.c -o lexer_rust.exe` compila el código C generado y produce el ejecutable.

## Ejecución

```cmd
lexer_rust.exe programa_prueba.rs
```

El programa recibe como argumento la ruta del archivo fuente en L y despliega en
consola, línea por línea, cada token reconocido con el formato:

```
[LINEA N] TOKEN: TIPO_DE_TOKEN | Lexema: valor_reconocido
```

### Ejemplo de entrada (`programa_prueba.rs`)

```rust
fn suma(a: i32, b: i32) -> i32 {
    let resultado = a + b;
    return resultado;
}

fn main() {
    let x: i32 = 10;
    let mut y: f64 = 3.14;
    if x > 5 {
        println!("x es mayor que 5");
    } else {
        y = y + 1.0;
    }
}
```

### Ejemplo de salida

```
[LINEA 1] TOKEN: KW_FN          | Lexema: fn
[LINEA 1] TOKEN: IDENTIFICADOR  | Lexema: suma
[LINEA 1] TOKEN: PAREN_ABR      | Lexema: (
[LINEA 1] TOKEN: IDENTIFICADOR  | Lexema: a
[LINEA 1] TOKEN: DOS_PUNTOS     | Lexema: :
[LINEA 1] TOKEN: TIPO_I32       | Lexema: i32
...
[LINEA 10] TOKEN: MACRO_PRINTLN | Lexema: println!
[LINEA 10] TOKEN: LIT_CADENA    | Lexema: "x es mayor que 5"
```

## Manejo de errores léxicos

Cualquier carácter que no coincida con ninguna regla del lenguaje L es reportado
sin detener la ejecución, con el formato:

```
[LINEA N] ERROR LEXICO: caracter no reconocido 'X'
```

## Autoría

Proyecto elaborado para la asignatura Lenguaje y Compiladores (Sección 01),
Msc. Félix Márquez, UNEG, periodo lectivo 2026-I.
