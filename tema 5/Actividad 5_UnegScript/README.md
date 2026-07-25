# Actividad 5 — Asistente híbrido UnegScript

**Universidad Nacional Experimental de Guayana**  
**Lenguaje y Compiladores – Tema 5 (Análisis Sintáctico) – 2026-I**  
**Punto 5:** Desarrollar un asistente de programación híbrido (técnicas de compilador tradicionales + IA) para un subconjunto de Python llamado **UnegScript**.

## 1. Objetivo

Implementar un asistente que combine:

1. **Lexer tradicional** (regex / autómata finito) + **fallback a IA** si el token no coincide (umbral de confianza **menor a 0.8**).
2. **Parser recursivo descendente con lookahead**, consultando IA para sugerencias si falla.
3. Prueba con el ejemplo del enunciado:  
   `pront x = 5; if x > 3 prnt(x) else prnt("no")`
4. **Salida:** tokens corregidos, AST y sugerencias de IA  
   (ej. `Sugerencia: 'pront' → 'print'`).

## 2. Contenido de esta carpeta

| Archivo | Descripción |
|---------|-------------|
| `uneg_assistant.py` | Programa principal: lexer híbrido + parser híbrido + demo |
| `README.md` | Este archivo (instrucciones de ejecución) |

## 3. Requisitos

- Python **3.9+** (probado con 3.10)
- Solo usa la biblioteca estándar (`re`, `difflib`, `json`, `dataclasses`). **No** hace falta `pip install`.

## 4. Cómo ejecutar

Abre una terminal y corre:

```bash
cd "/Users/ronniel/UNIVERSIDAD/LyC-Logica-y-Computacion/tema 5/Actividad 5_UnegScript"
python3 uneg_assistant.py
```

Si ya estás dentro de la carpeta:

```bash
python3 uneg_assistant.py
```

El programa ejecuta automáticamente el ejemplo con errores del enunciado e imprime:

1. Tokens corregidos  
2. Sugerencias de IA (nivel léxico)  
3. AST (árbol de sintaxis abstracta en JSON)  
4. Sugerencias de IA (nivel sintáctico / parser)

## 5. Qué hace el programa (resumen)

- **Lexer:** tokeniza con regex. Si un identificador se parece a una keyword:
  - ratio **mayor a 0.8** → corrección automática (`prnt` → `print`)
  - ratio **menor o igual a 0.8** (zona ambigua) → **fallback a IA** (`pront` → `print`)
- **Parser:** recursivo descendente con 1 token de lookahead. Si falla, recupera en modo pánico y genera sugerencias.
- **IA:** simulada localmente con `difflib.SequenceMatcher` (lectura complementaria 6.1/6.2 del tema). La función `ai_suggest()` es el punto de integración para un LLM real.

## 6. Ejemplo de salida esperada

```text
Codigo fuente (con errores):
  pront x = 5; if x > 3 prnt(x) else prnt("no")

1) TOKENS CORREGIDOS
  PRINT    'print'   (corregido de 'pront', confianza=0.95)
  ...
  PRINT    'print'   (corregido de 'prnt', confianza=0.89)

2) SUGERENCIAS DE IA (nivel LEXICO)
  Sugerencia: 'pront' -> 'print'   (fallback a IA)
  Sugerencia: 'prnt' -> 'print'    (corrección automática)

3) AST ...
4) SUGERENCIAS DE IA (nivel SINTACTICO, parser)
  Sugerencia: 'print x = 5' -> separar en dos sentencias...
```
