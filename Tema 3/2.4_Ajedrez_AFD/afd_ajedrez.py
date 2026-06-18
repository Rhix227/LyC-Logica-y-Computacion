#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==========================================================================
 Tema 3 - Lenguajes y Gramaticas Formales
 Punto 2.4: De la Expresion al Automata  (Caso Practico: Ajedrez)
==========================================================================

 Este programa implementa un AUTOMATA FINITO DETERMINISTICO (AFD) que
 reconoce un subconjunto simplificado de la notacion PGN / SAN
 (Standard Algebraic Notation) usada para anotar jugadas de ajedrez.

 Cubre los tres sub-puntos del enunciado:

   2.4.1  Plantea y EJECUTA un automata finito para el reconocimiento
          de un subconjunto del lenguaje PGN.
   2.4.2  Define el subconjunto simplificado del PGN (ver README.md).
   2.4.3  Implementa el AFD EQUIVALENTE a la Expresion Regular (Regex).

 El AFD se implementa de forma explicita mediante su FUNCION DE
 TRANSICION (tabla delta), tal como se disena en el papel. Ademas, se
 incluye la Regex equivalente para demostrar, empiricamente, que ambos
 modelos reconocen exactamente el mismo lenguaje (Teorema de Kleene).
==========================================================================
"""

import re
import sys

# --------------------------------------------------------------------------
# 0. EXPRESION REGULAR EQUIVALENTE (2.4.3)
# --------------------------------------------------------------------------
# Una jugada del subconjunto se describe con la siguiente expresion regular.
# Se usa solo para CONTRASTAR contra el AFD (no es el reconocedor principal).
#
#   ^( (?:[KQRBN]x? | [a-h]x)?  [a-h][1-8]   |   O-O(?:-O)? ) [+#]? $
#     \_________________________/ \________/      \________/   \__/
#        prefijo opcional          casilla          enroque    jaque
#        (pieza/captura)           destino          corto/largo /mate
#
REGEX = r"^((?:[KQRBN]x?|[a-h]x)?[a-h][1-8]|O-O(?:-O)?)[+#]?$"
_PATRON = re.compile(REGEX)


# --------------------------------------------------------------------------
# 1. DEFINICION FORMAL DEL AFD  ->  M = (Q, Sigma, delta, q0, F)
# --------------------------------------------------------------------------

# Alfabeto Sigma, agrupado en CATEGORIAS de simbolos para que la tabla de
# transicion sea legible (cada categoria abarca varios caracteres):
PIEZAS   = set("KQRBN")      # categoria 'P' -> Rey, Dama, Torre, Alfil, Caballo
COLUMNAS = set("abcdefgh")   # categoria 'F' -> columnas (files)  a..h
FILAS    = set("12345678")   # categoria 'R' -> filas   (ranks)   1..8
# ademas: 'x' (captura), 'O' (enroque), '-' (guion), 'J' (jaque/mate: + o #)


def categoria(c):
    """Clasifica un caracter de entrada en su categoria del alfabeto Sigma."""
    if c in PIEZAS:   return 'P'
    if c in COLUMNAS: return 'F'
    if c in FILAS:    return 'R'
    if c == 'x':      return 'x'
    if c == 'O':      return 'O'
    if c == '-':      return '-'
    if c in '+#':     return 'J'
    return '?'                       # caracter desconocido -> llevara a qdead


# q0 = estado inicial.  Estado muerto/trampa = 'qdead'.
ESTADO_INICIAL = 'q0'
MUERTO = 'qdead'

# F = conjunto de estados de aceptacion (jugada completa y valida)
ACEPTACION = {'qA', 'qC1', 'qC2', 'qS'}

# delta : Q x Sigma -> Q   (FUNCION DE TRANSICION)
# Toda combinacion (estado, categoria) que NO aparezca aqui va a 'qdead'.
DELTA = {
    'q0':  {'P': 'qP',  'F': 'qpf', 'O': 'qO1'},  # inicio
    'qP':  {'x': 'qf',  'F': 'qr'},               # se leyo una pieza (ej. N)
    'qpf': {'R': 'qA',  'x': 'qf'},               # se leyo columna inicial (peon)
    'qf':  {'F': 'qr'},                           # se espera columna destino
    'qr':  {'R': 'qA'},                           # se espera fila destino
    'qA':  {'J': 'qS'},                           # jugada aceptada (+ jaque/mate?)
    'qO1': {'-': 'qO2'},                          # se leyo  O
    'qO2': {'O': 'qC1'},                          # se leyo  O-
    'qC1': {'-': 'qO3', 'J': 'qS'},               # se leyo  O-O   (enroque corto)
    'qO3': {'O': 'qC2'},                          # se leyo  O-O-
    'qC2': {'J': 'qS'},                           # se leyo  O-O-O (enroque largo)
    'qS':  {},                                    # se leyo el sufijo + o #
}

# Descripcion legible de cada estado (util para la defensa / depuracion)
DESCRIPCION = {
    'q0':   'inicial',
    'qP':   'leida una pieza [KQRBN]',
    'qpf':  'leida columna inicial de peon [a-h]',
    'qf':   'esperando columna destino tras captura',
    'qr':   'esperando fila destino',
    'qA':   'ACEPTA: jugada completa',
    'qO1':  'leida  O',
    'qO2':  'leida  O-',
    'qC1':  'ACEPTA: enroque corto  O-O',
    'qO3':  'leida  O-O-',
    'qC2':  'ACEPTA: enroque largo  O-O-O',
    'qS':   'ACEPTA: con jaque (+) o mate (#)',
    'qdead':'estado muerto (trampa)',
}


# --------------------------------------------------------------------------
# 2. EJECUCION DEL AFD (2.4.1)  ->  el reconocedor propiamente dicho
# --------------------------------------------------------------------------

def validar_movimiento(cadena):
    """
    Ejecuta el AFD sobre 'cadena' (una sola jugada).
    Devuelve: (aceptado:bool, estado_final:str, traza:list)
    La traza es la secuencia de pasos (estado, caracter, categoria, siguiente).
    """
    estado = ESTADO_INICIAL
    traza = []
    for c in cadena:
        cat = categoria(c)
        siguiente = DELTA.get(estado, {}).get(cat, MUERTO)
        traza.append((estado, c, cat, siguiente))
        estado = siguiente
        if estado == MUERTO:        # estado trampa: no hay vuelta atras
            break
    aceptado = (estado in ACEPTACION)
    return aceptado, estado, traza


def validar_con_regex(cadena):
    """Valida la misma jugada usando la Regex equivalente (para contraste)."""
    return _PATRON.match(cadena) is not None


# --------------------------------------------------------------------------
# 3. EXTENSION: reconocimiento de una linea de MOVETEXT del PGN
# --------------------------------------------------------------------------
# Una linea de PGN combina numeros de jugada, jugadas y, al final, el
# resultado.  Ej:  "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0"
# Aqui se descomponen los tokens y se valida CADA jugada con el AFD anterior.

_RESULTADOS = {"1-0", "0-1", "1/2-1/2", "*"}


def validar_movetext(linea):
    """
    Reconoce una linea de movetext PGN: separa numeros de jugada y resultado,
    y valida cada jugada con el AFD. Devuelve (todo_valido, detalle:list).
    """
    detalle = []
    todo_valido = True
    for token in linea.split():
        if token in _RESULTADOS:
            detalle.append((token, True, "resultado de la partida"))
            continue
        # quita el prefijo de numero de jugada:  "1." , "12." , "1.e4"
        jugada = re.sub(r"^\d+\.*", "", token)
        if jugada == "":
            detalle.append((token, True, "numero de jugada"))
            continue
        ok, _, _ = validar_movimiento(jugada)
        detalle.append((jugada, ok, "jugada valida" if ok else "JUGADA INVALIDA"))
        todo_valido = todo_valido and ok
    return todo_valido, detalle


# --------------------------------------------------------------------------
# 4. PRESENTACION POR CONSOLA
# --------------------------------------------------------------------------

def imprimir_traza(cadena):
    """Muestra paso a paso el recorrido del AFD para una jugada."""
    aceptado, estado_final, traza = validar_movimiento(cadena)
    print(f"\n  Entrada: '{cadena}'")
    if not traza:
        print("    (cadena vacia)")
    for (orig, c, cat, dest) in traza:
        flecha = f"{orig:>5}  --{c}({cat})-->  {dest}"
        print(f"    {flecha:<34} {DESCRIPCION.get(dest,'')}")
    veredicto = "ACEPTADA  (jugada valida)" if aceptado else "RECHAZADA (jugada invalida)"
    marca = "[OK]" if aceptado else "[X ]"
    print(f"    {marca} {veredicto}   estado final = {estado_final}")
    return aceptado


def demo():
    """Bateria de ejemplos: valida con el AFD y contrasta con la Regex."""
    print("=" * 70)
    print(" AFD para el subconjunto simplificado de PGN/SAN (Ajedrez)")
    print(" Punto 2.4 - De la Expresion al Automata")
    print("=" * 70)
    print(f"\n Regex equivalente:\n   {REGEX}")

    validas = ["e4", "d5", "exd5", "Nf3", "Nc6", "Bb5", "Qh5+", "Qh7#",
               "Nxe4", "Rxe5+", "Kg1", "O-O", "O-O-O", "O-O+", "O-O-O#"]
    invalidas = ["e9", "Pe4", "Ne", "xe4", "e44", "OO", "O-O-O-O",
                 "Nf3++", "9e", "", "Z1", "e4#x"]

    print("\n" + "-" * 70)
    print(" 1) JUGADAS QUE DEBEN ACEPTARSE")
    print("-" * 70)
    for m in validas:
        imprimir_traza(m)

    print("\n" + "-" * 70)
    print(" 2) JUGADAS QUE DEBEN RECHAZARSE")
    print("-" * 70)
    for m in invalidas:
        imprimir_traza(m)

    # Demostracion de EQUIVALENCIA AFD <-> Regex (Teorema de Kleene)
    print("\n" + "-" * 70)
    print(" 3) EQUIVALENCIA  AFD  <->  REGEX  (deben coincidir en todo caso)")
    print("-" * 70)
    discrepancias = 0
    for m in validas + invalidas:
        afd = validar_movimiento(m)[0]
        rgx = validar_con_regex(m)
        estado = "coinciden" if afd == rgx else ">>> DISCREPANCIA <<<"
        if afd != rgx:
            discrepancias += 1
        print(f"    '{m:<8}'  AFD={str(afd):<5}  Regex={str(rgx):<5}  {estado}")
    print(f"\n    Total de discrepancias: {discrepancias}  "
          f"({'EQUIVALENTES' if discrepancias == 0 else 'REVISAR'})")

    # Ejemplo de reconocimiento de una linea de movetext PGN completa
    print("\n" + "-" * 70)
    print(" 4) RECONOCIMIENTO DE UNA LINEA DE MOVETEXT PGN")
    print("-" * 70)
    linea = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. O-O Nxe4 1-0"
    ok, detalle = validar_movetext(linea)
    print(f"\n  Linea: {linea}")
    for (tok, valido, nota) in detalle:
        marca = "[OK]" if valido else "[X ]"
        print(f"    {marca} {tok:<8} -> {nota}")
    print(f"\n  Resultado global: {'LINEA VALIDA' if ok else 'LINEA INVALIDA'}")


# --------------------------------------------------------------------------
# 5. PUNTO DE ENTRADA / CLI
# --------------------------------------------------------------------------

def main(argv):
    if not argv:
        demo()
        print("\nUso:")
        print("  python3 afd_ajedrez.py                 -> ejecuta la demo")
        print("  python3 afd_ajedrez.py e4 Nf3 O-O e9   -> valida cada jugada")
        print('  python3 afd_ajedrez.py --movetext "1. e4 e5 2. Nf3"')
        return

    if argv[0] == "--movetext":
        linea = " ".join(argv[1:])
        ok, detalle = validar_movetext(linea)
        print(f"Linea: {linea}")
        for (tok, valido, nota) in detalle:
            marca = "[OK]" if valido else "[X ]"
            print(f"  {marca} {tok:<8} -> {nota}")
        print(f"Resultado: {'VALIDA' if ok else 'INVALIDA'}")
        return

    for jugada in argv:
        imprimir_traza(jugada)


if __name__ == "__main__":
    main(sys.argv[1:])
