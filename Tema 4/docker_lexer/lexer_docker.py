#!/usr/bin/env python3
"""
lexer_docker.py
----------------
Analizador léxico (lexer) para archivos Dockerfile, implementado
"desde cero" en Python utilizando expresiones regulares (módulo re).

Tema 4 - Lenguaje y Compiladores (2026-I)
Actividad 2: Construya un lexer para la verificación de archivos
docker mediante expresiones regulares.

Uso:
    python3 lexer_docker.py <archivo_dockerfile>

Si no se pasa ningún argumento, intenta leer un archivo llamado
"Dockerfile" en el directorio actual.
"""

import re
import sys


# ---------------------------------------------------------------------------
# 1. DEFINICIÓN DE TOKENS (patrones regex)
# ---------------------------------------------------------------------------
# El orden importa: re.finditer prueba las reglas en el orden en que
# aparecen en la lista, por lo que las palabras clave (instrucciones)
# deben ir ANTES que la regla genérica de palabra (WORD), tal como se
# explica en el material del Tema 4 (ver ejemplo "ddress" -> INTERFACE_NAME).

INSTRUCCIONES = [
    "FROM", "RUN", "CMD", "LABEL", "MAINTAINER", "EXPOSE", "ENV",
    "ADD", "COPY", "ENTRYPOINT", "VOLUME", "USER", "WORKDIR", "ARG",
    "ONBUILD", "STOPSIGNAL", "HEALTHCHECK", "SHELL",
]

# Construimos la alternancia de instrucciones válidas de Docker,
# solo al inicio de línea (permitiendo indentación previa), sin
# distinguir mayúsculas/minúsculas (Docker las acepta en minúscula
# también, aunque la convención es usarlas en mayúscula).
_instr_alt = "|".join(INSTRUCCIONES)

tokens = [
    # Comentarios: línea que inicia con '#'
    ("COMMENT",        r"\#.*"),

    # Instrucciones reservadas de Dockerfile (FROM, RUN, CMD, etc.)
    ("INSTRUCCION",    rf"\b(?:{_instr_alt})\b"),

    # Flags de línea de comandos: --from=builder, --chown=user:group, --platform=linux/amd64
    ("FLAG",           r"--[a-zA-Z][a-zA-Z0-9_-]*(=[^\s]+)?"),

    # Variable de entorno estilo KEY=VALUE (usado en ENV / ARG)
    ("ENV_VAR",        r"[A-Za-z_][A-Za-z0-9_]*=[^\s]+"),

    # Puertos con protocolo, o número suelto (usado en EXPOSE/USER): 8080/tcp, 53/udp, 1000
    ("NUMERO",         r"\b\d{1,5}(/(tcp|udp))?\b"),

    # Cadenas de texto entre comillas dobles o simples
    ("STRING",         r'"([^"\\]|\\.)*"' + r"|'([^'\\]|\\.)*'"),

    # Arreglos JSON (forma exec): ["executable","param1","param2"]
    ("JSON_ARRAY",     r"\[[^\]]*\]"),

    # Imagen con tag y/o digest: python:3.12-slim , nginx@sha256:abcd1234...
    ("IMAGEN_TAG",     r"[a-zA-Z0-9_.\-/]+(:[a-zA-Z0-9_.\-]+)?(@sha256:[a-fA-F0-9]{6,64})?"
                       r"(?=\s|$)",),

    # Rutas / nombres genéricos (identificadores, paths, nombres de archivo)
    ("RUTA",           r"[a-zA-Z0-9_./\-\*\$\{\}]+"),

    # Operador de continuación de línea (backslash al final de línea)
    ("CONTINUACION",   r"\\\s*$"),

    # Fin de línea
    ("NEWLINE",        r"\n"),

    # Espacios y tabuladores (se ignoran)
    ("SKIP",           r"[ \t]+"),

    # Cualquier otro carácter no reconocido -> error léxico
    ("MISMATCH",       r"."),
]


def construir_regex():
    """Compila la expresión regular maestra combinando todos los tokens."""
    return "|".join(f"(?P<{nombre}>{patron})" for nombre, patron in tokens)


def lexer(texto_entrada):
    """
    Generador que recorre 'texto_entrada' carácter a carácter (mediante
    finditer) y va emitiendo tuplas (token, lexema, num_linea, columna).

    Lanza RuntimeError con detalle de línea/columna si encuentra un
    carácter que no calza con ningún patrón léxico definido (MISMATCH),
    de forma equivalente al "estado fallido" descrito en la teoría de
    autómatas del Tema 4.
    """
    regex_maestra = construir_regex()
    num_linea = 1
    inicio_linea = 0
    errores = []

    for mo in re.finditer(regex_maestra, texto_entrada, re.MULTILINE):
        tipo = mo.lastgroup
        valor = mo.group(tipo)

        if tipo == "NEWLINE":
            inicio_linea = mo.end()
            num_linea += 1
            continue
        if tipo in ("SKIP", "COMMENT", "CONTINUACION"):
            continue
        if tipo == "MISMATCH":
            columna = mo.start() - inicio_linea
            errores.append((valor, num_linea, columna))
            # Autómata con "estado fallido": se informa el error y se
            # continúa leyendo el resto de la entrada (no se detiene
            # en el primer error, según lo señalado en el Tema 4).
            continue

        columna = mo.start() - inicio_linea
        yield (tipo, valor, num_linea, columna)

    # Al final del recorrido, si hubo errores léxicos los reportamos.
    if errores:
        for valor, linea, columna in errores:
            print(f"  [ERROR LÉXICO] Carácter/lexema no reconocido: "
                  f"{valor!r} en línea {linea}, columna {columna}")


def cargar_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: el archivo '{nombre_archivo}' no fue encontrado.")
        return None
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return None


def analizar(nombre_archivo):
    print(f"\n=== Analizando: {nombre_archivo} ===\n")
    texto = cargar_archivo(nombre_archivo)
    if texto is None:
        return

    total_tokens = 0
    for tok in lexer(texto):
        print(tok)
        total_tokens += 1

    print(f"\nTotal de tokens reconocidos: {total_tokens}")
    print("=== Fin del análisis ===\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    else:
        archivo = "Dockerfile"
    analizar(archivo)
