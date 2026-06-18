# =============================================================================
# TEMA 3 – Lenguajes y Gramáticas Formales
# Sección 2.2 – Derivación y Modelado (Caso Práctico: Genoma)
#
# Librerías usadas: turtle (estándar), time (estándar)
# =============================================================================

import turtle
import time

# =============================================================================
# DEFINICIÓN DE LA GRAMÁTICA LIBRE DE CONTEXTO (GLC)
# G = (V, Σ, S, P)
# =============================================================================

GRAMATICA = """
╔══════════════════════════════════════════════════════════════════╗
║         GRAMÁTICA LIBRE DE CONTEXTO – CASO GENOMA                ║
╠══════════════════════════════════════════════════════════════════╣
║  Variables (V) : { S, F, L, G, D, R, B, H }                      ║
║  Terminales (Σ): { a, c, d, g, t, h }                            ║
║  Símbolo inicial: S                                              ║
╠══════════════════════════════════════════════════════════════════╣
║  PRODUCCIONES (P):                                               ║
║    S  →  F                                                       ║
║    F  →  F L | F G | F D | F R | F H | L | G | D | R | H         ║
║    L  →  a L | a          (avance simple o repetido)             ║
║    G  →  c                (giro 90° a la derecha)                ║
║    D  →  d                (giro 120° a la derecha — isometría)   ║
║    R  →  g B t            (rama: push – cuerpo – pop)            ║
║    B  →  F B | F          (cuerpo de rama)                       ║
║    H  →  h                (dibuja una hoja en posición actual)   ║ 
╠══════════════════════════════════════════════════════════════════╣
║  SEMÁNTICA DE TERMINALES:                                        ║
║    a → avanzar una unidad en la dirección actual                 ║
║    c → girar 90° a la derecha                                    ║
║    d → girar 120° a la derecha (isometría / ramas divergentes)   ║
║    g → guardar posición y dirección (push / abrir rama)          ║
║    t → restaurar posición y dirección (pop  / cerrar rama)       ║
║    h → dibujar una hoja en la posición actual (sin avanzar)      ║
╚══════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# DERIVACIONES PASO A PASO
# =============================================================================

DERIVACIONES = {
    "cuadrado": {
        "nombre": "Figura 1 – Cuadrado",
        "descripcion": "Avanzar y girar 90° cuatro veces consecutivas (avanza-gira-avanza-gira-avanza-gira-avanza-gira).",
        "pasos": [
            "S",
            "=> F",
            "=> F L G",
            "=> F L G L G",
            "=> F L G L G L G",
            "=> L G L G L G L G",
            "=> a G L G L G L G",
            "=> a c L G L G L G",
            "=> a c a G L G L G",
            "=> a c a c L G L G",
            "=> a c a c a G L G",
            "=> a c a c a c L G",
            "=> a c a c a c a G",
            "=> a c a c a c a c",
        ],
        "cadena": "acacacac",
    },
    "arbol": {
        "nombre": "Figura 2 – Árbol con dos ramas y hojas",
        "descripcion": "Tronco largo (aaa), dos ramas divergentes giradas 120° (d), cada una con hoja (h) al final.",
        "pasos": [
            "S",
            "=> F",
            "=> F L",
            "=> F L L",
            "=> F L L L",
            "=> F L L L D R",
            "=> F L L L D R D R",
            "=> L L L L D R D R",
            "=> a L L L D R D R",
            "=> a a L L D R D R",
            "=> a a a L D R D R",
            "=> a a a a D R D R",
            "=> a a a a d R D R",
            "=> a a a a d g B t D R",
            "=> a a a a d g F t D R",
            "=> a a a a d g L t D R",
            "=> a a a a d g a t D R",
            "=> a a a a d g a H t D R",
            "=> a a a a d g a h t D R",
            "=> a a a a d g a h t d R",
            "=> a a a a d g a h t d g B t",
            "=> a a a a d g a h t d g F t",
            "=> a a a a d g a h t d g L t",
            "=> a a a a d g a h t d g a t",
            "=> a a a a d g a h t d g a H t",
            "=> a a a a d g a h t d g a h t",
        ],
        "cadena": "aaaadgahtdgaht",
        # Tronco: 4 avances hacia Norte; luego dos ramas simétricas con hojas
    },
    "triangulo": {
        "nombre": "Figura 3 – Triángulo equilátero",
        "descripcion": "Tres avances separados por giros de 120° (d) trazan un triángulo equilátero cerrado.",
        "pasos": [
            "S",
            "=> F",
            "=> F D F",
            "=> F D F D F",
            "=> L D F D F",
            "=> a D F D F",
            "=> a d F D F",
            "=> a d L D F",
            "=> a d a D F",
            "=> a d a d F",
            "=> a d a d L",
            "=> a d a d a",
        ],
        "cadena": "adadad",
    },
    "linea_giro": {
        "nombre": "Figura 4 – Línea con giro (forma en L invertida)",
        "descripcion": "Avanzar, girar 90° y avanzar de nuevo produce una figura en L.",
        "pasos": [
            "S",
            "=> F",
            "=> F G L",
            "=> L G L",
            "=> a G L",
            "=> a c L",
            "=> a c a",
        ],
        "cadena": "aca",
    },
    "escalera": {
        "nombre": "Figura 5 – Escalera (tres peldaños)",
        "descripcion": "Cada peldaño se forma con: sube (a), avanza (c→a), regresa al Norte (ccc). Repetido tres veces produce una escalera ascendente.",
        "pasos": [
            "S",
            "=> F",
            "=> F G",
            "=> F G L",
            "=> F G L G",
            "=> F G L G G",
            "=> F G L G G G",
            "=> F G L G G G L",
            "=> L G L G G G L G G G L G G G",
            "=> a G L G G G L G G G L G G G",
            "=> a c L G G G L G G G L G G G",
            "=> a c a G G G L G G G L G G G",
            "=> a c a c G G L G G G L G G G",
            "=> a c a c c G L G G G L G G G",
            "=> a c a c c c L G G G L G G G",
            "=> a c a c c c a G G G L G G G",
            "=> ... (patrón se repite para los tres peldaños)",
            "=> a c a c c c a c a c c c a c a c",
        ],
        "cadena": "acacccacacccacac",
    },
}

# =============================================================================
# INTÉRPRETE DE CADENAS SOBRE EL ALFABETO {a, c, d, g, t, h}
# Usa turtle para dibujar la figura
# =============================================================================

def interpretar_cadena(cadena, t, paso=60, angulo=90):
    """
    Interpreta una cadena del alfabeto {a, c, d, g, t, h} y dibuja la figura.

    Parámetros:
        cadena : str  – cadena a interpretar
        t      : turtle.Turtle – objeto tortuga
        paso   : int  – longitud de cada avance en píxeles
        angulo : int  – grados de giro para 'c' (90°); 'd' usa siempre 120°
    """
    pila = []  # pila para guardar/restaurar posiciones (g y t)

    for simbolo in cadena:
        if simbolo == 'a':
            # Avanzar una unidad en la dirección actual
            t.pendown()
            t.forward(paso)

        elif simbolo == 'c':
            # Girar 90° a la derecha
            t.right(angulo)

        elif simbolo == 'd':
            # Girar 120° a la derecha (terminal ampliado – isometría / ramas)
            t.right(120)

        elif simbolo == 'g':
            # Guardar (push) posición y dirección actuales — solo apila, no mueve
            estado = (t.pos(), t.heading())
            pila.append(estado)

        elif simbolo == 't':
            # Restaurar (pop) la última posición guardada
            if pila:
                pos, heading = pila.pop()
                t.penup()
                t.goto(pos)
                t.setheading(heading)
            # Si la pila está vacía se ignora el 't' (cadena mal formada)

        elif simbolo == 'h':
            # Dibujar una hoja en la posición actual (sin desplazar la tortuga)
            color_orig = t.pencolor()
            t.penup()
            t.dot(8, "green")   # punto verde como marca de hoja
            t.pencolor(color_orig)

        # Cualquier símbolo no reconocido se ignora silenciosamente


def mostrar_derivacion(figura_key):
    """
    Imprime en consola la derivación completa y dibuja la figura con turtle.
    """
    datos = DERIVACIONES[figura_key]

    print("\n" + "=" * 66)
    print(f"  {datos['nombre']}")
    print("=" * 66)
    print(f"  Descripción : {datos['descripcion']}")
    print(f"  Cadena final: {datos['cadena']}")
    print("-" * 66)
    print("  DERIVACIÓN PASO A PASO:")
    for paso in datos["pasos"]:
        print(f"    {paso}")
    print(f"\n  >>> Cadena a interpretar: \"{datos['cadena']}\"")
    print("=" * 66)

    # ── Configurar ventana turtle ──
    pantalla = turtle.Screen()
    pantalla.title(f"UNEG 2026-I | {datos['nombre']}")
    pantalla.bgcolor("white")
    pantalla.setup(width=700, height=600)

    # ── Parámetros específicos por figura ──
    # (pos_x, pos_y, heading_inicial, paso_px, angulo_c)
    # Calculados simulando cada cadena símbolo a símbolo.
    cfg = {
        # Cuadrado: arranca abajo-izquierda apuntando Este → cuadrado sube-derecha ✓
        "cuadrado":   (-130, -50,   0,   80,  90),
        # Árbol: arranca abajo-centro apuntando Norte → tronco sube, ramas divergen ✓
        # Simulación: tronco a (0,1); rama1 → (0.9,0.5); rama2 → (-0.9,0.5)
        "arbol":      (   0, -80,  90,   90,  90),
        # Triángulo: arranca izq-centro apuntando Este, gira 120° entre lados ✓
        "triangulo":  (-120, -60,   0,  150,  90),
        # Línea en L: Norte→sube, gira Este→avanza derecha → L correcta ✓
        "linea_giro": (-100, -50,  90,  120,  90),
        # Escalera: arranca abajo-izquierda apuntando Norte, 3 peldaños suben-derecha ✓
        "escalera":   (-200, -120,  90,   80,  90),
    }
    pos_x, pos_y, heading_ini, paso_px, angulo_c = cfg.get(
        figura_key, (-100, 0, 0, 60, 90)
    )

    # ── Configurar tortuga ──
    t = turtle.Turtle()
    t.speed(5)          # velocidad: 1 (lento) – 10 (rápido); 0 = máximo
    t.pensize(2)
    t.color("navy")
    t.penup()
    t.goto(pos_x, pos_y)
    t.setheading(heading_ini)
    t.pendown()

    # ── Dibujar ──
    interpretar_cadena(datos["cadena"], t, paso=paso_px, angulo=angulo_c)

    # ── Leyenda ──
    t.penup()
    t.goto(-320, -260)
    t.color("gray")
    t.write(f"Cadena: {datos['cadena']}   |   {datos['nombre']}",
            font=("Arial", 9, "normal"))

    t.hideturtle()
    print("\n  [Figura dibujada. Cierre la ventana para continuar.]\n")
    pantalla.mainloop()


# =============================================================================
# MENÚ PRINCIPAL
# =============================================================================

def menu():
    print(GRAMATICA)

    opciones = {
        "1": "cuadrado",
        "2": "arbol",
        "3": "triangulo",
        "4": "linea_giro",
        "5": "escalera",
    }

    print("  SELECCIONE UNA FIGURA PARA DERIVAR Y DIBUJAR:")
    print("  [1] Cuadrado")
    print("  [2] Árbol con dos ramas y hojas")
    print("  [3] Triángulo equilátero")
    print("  [4] Línea con giro (forma en L invertida)")
    print("  [5] Escalera (tres peldaños)")
    print("  [0] Salir")

    while True:
        eleccion = input("\n  Ingrese el número de la figura: ").strip()
        if eleccion == "0":
            print("\n  Programa terminado.\n")
            break
        elif eleccion in opciones:
            mostrar_derivacion(opciones[eleccion])
            # Después de cerrar la ventana, volver al menú
            print("\n  Desea dibujar otra figura? (s/n): ", end="")
            resp = input().strip().lower()
            if resp != "s":
                print("\n  Programa terminado.\n")
                break
            # Limpiar la pantalla turtle para la siguiente figura
            try:
                turtle.bye()
            except Exception:
                pass
        else:
            print("  Opción no válida. Intente de nuevo.")


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    menu()