# 2.4 — De la Expresión al Autómata (Caso Práctico: Ajedrez)

**Tema 3 — Lenguajes y Gramáticas Formales** · Lenguaje y Compiladores 2026-I

Este directorio resuelve **íntegramente** el punto 2.4 del enunciado:

| Sub-punto | Requisito | Dónde se resuelve |
|-----------|-----------|-------------------|
| **2.4.1** | Plantear y **ejecutar** autómatas finitos para reconocer un subconjunto de PGN | [`afd_ajedrez.py`](afd_ajedrez.py) — AFD implementado y ejecutable |
| **2.4.2** | Definir un **subconjunto simplificado** del PGN para movimientos básicos | Sección 2 de este README |
| **2.4.3** | Diseñar la **Regex** y el **AFD equivalente** | Secciones 3 y 4 de este README |

---

## 1. ¿Qué es PGN y SAN?

**PGN (Portable Game Notation)** es el formato estándar de texto plano para registrar
partidas de ajedrez. Una partida PGN tiene dos partes:

1. **Tag pairs** (metadatos): `[Event "..."]`, `[Site "..."]`, `[Date "..."]`, etc.
2. **Movetext**: la secuencia de jugadas más el resultado, p. ej.:
   `1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0`

Cada jugada se escribe en **SAN (Standard Algebraic Notation)**:

| Tipo de jugada | Ejemplo | Lectura |
|----------------|---------|---------|
| Peón | `e4` | el peón va a la casilla e4 |
| Pieza | `Nf3` | el caballo (**N**) va a f3 |
| Captura | `exd5`, `Nxe4` | la `x` indica captura |
| Enroque corto | `O-O` | enroque del flanco de rey |
| Enroque largo | `O-O-O` | enroque del flanco de dama |
| Jaque / mate | `Qh5+`, `Qh7#` | sufijo `+` (jaque) o `#` (mate) |

Letras de pieza: **K**=Rey, **Q**=Dama, **R**=Torre, **B**=Alfil, **N**=Caballo.
*(Como el peón es la pieza más común, no lleva letra.)*

---

## 2. (2.4.2) Subconjunto simplificado del PGN

Reconocer **todo** el PGN excede a un lenguaje regular (los comentarios anidados
`{ ... ( ... ) ... }` y las variantes requieren una Gramática Libre de Contexto).
Por eso definimos un **subconjunto regular** centrado en una **jugada SAN básica**.

### Lo que SÍ acepta nuestro lenguaje L

| # | Patrón | Ejemplos válidos |
|---|--------|------------------|
| 1 | Movimiento de peón | `e4`, `d5`, `a6` |
| 2 | Captura de peón | `exd5`, `gxf6` |
| 3 | Movimiento de pieza | `Nf3`, `Bb5`, `Qd1`, `Kg1` |
| 4 | Captura de pieza | `Nxe4`, `Rxe5` |
| 5 | Enroque corto / largo | `O-O`, `O-O-O` |
| 6 | Cualquiera de los anteriores + jaque/mate | `Qh5+`, `Qh7#`, `O-O+` |

### Lo que NO acepta (para mantenerlo regular y simple)

- Desambiguación: `Nbd2`, `R1e2`
- Coronación de peón: `e8=Q`
- Comentarios, variantes y anotaciones: `{...}`, `(...)`, `!`, `?`
- Los *tag pairs* del encabezado.

### Alfabeto formal

```
Σ = { K, Q, R, B, N,          (piezas)
      a, b, c, d, e, f, g, h, (columnas / files)
      1, 2, 3, 4, 5, 6, 7, 8, (filas / ranks)
      x,                       (captura)
      O, -,                    (enroque)
      +, # }                   (jaque, mate)
```

En el código, para que la tabla de transición sea legible, esos caracteres se
agrupan en **categorías**: `P` (pieza), `F` (columna), `R` (fila), `x`, `O`, `-`,
`J` (jaque/mate `+` o `#`).

---

## 3. (2.4.3) Expresión Regular

```
^( (?:[KQRBN]x? | [a-h]x)? [a-h][1-8]  |  O-O(?:-O)? ) [+#]? $
```

Descompuesta por partes:

| Fragmento | Significado |
|-----------|-------------|
| `[KQRBN]x?` | una pieza, con captura opcional → `N`, `Nx` |
| `[a-h]x` | columna de origen del peón + captura → `ex` |
| `(?:[KQRBN]x? \| [a-h]x)?` | **prefijo opcional** (si no aparece, es un peón) |
| `[a-h][1-8]` | **casilla destino obligatoria** (columna + fila) |
| `O-O(?:-O)?` | enroque corto `O-O`, o largo `O-O-O` |
| `[+#]?` | sufijo opcional de jaque (`+`) o mate (`#`) |

Esta regex es exactamente la implementada en `REGEX` dentro de
[`afd_ajedrez.py`](afd_ajedrez.py).

---

## 4. (2.4.3) AFD equivalente

### Definición formal — M = (Q, Σ, δ, q₀, F)

- **Q** = { q0, qP, qpf, qf, qr, qA, qO1, qO2, qC1, qO3, qC2, qS, qdead }
- **Σ** = el alfabeto de la sección 2 (categorías P, F, R, x, O, -, J)
- **q₀** = `q0` (estado inicial)
- **F** = { `qA`, `qC1`, `qC2`, `qS` } (estados de aceptación)
- **δ** = la tabla de transición siguiente

### Tabla de transición δ

> Toda celda vacía representa una transición al **estado muerto** `qdead`
> (estado trampa: una vez dentro, no se sale y la cadena se rechaza).

| Estado \ Cat. | **P** | **F** | **R** | **x** | **O** | **-** | **J** | Descripción |
|---------------|-------|-------|-------|-------|-------|-------|-------|-------------|
| → **q0**      | qP    | qpf   |       |       | qO1   |       |       | inicial |
| **qP**        |       | qr    |       | qf    |       |       |       | leída una pieza |
| **qpf**       |       |       | qA    | qf    |       |       |       | leída columna de peón |
| **qf**        |       | qr    |       |       |       |       |       | espera columna destino |
| **qr**        |       |       | qA    |       |       |       |       | espera fila destino |
| **\*qA**      |       |       |       |       |       |       | qS    | jugada completa |
| **qO1**       |       |       |       |       |       | qO2   |       | leída `O` |
| **qO2**       |       |       |       |       | qC1   |       |       | leída `O-` |
| **\*qC1**     |       |       |       |       |       | qO3   | qS    | enroque corto `O-O` |
| **qO3**       |       |       |       |       | qC2   |       |       | leída `O-O-` |
| **\*qC2**     |       |       |       |       |       |       | qS    | enroque largo `O-O-O` |
| **\*qS**      |       |       |       |       |       |       |       | con jaque/mate |

`→` = estado inicial · `*` = estado de aceptación.

### Diagrama de estados

```
                  P                F                R
        ┌────────────────► qP ──────────► qr ──────────────┐
        │                  │                               │
        │                  │ x                             ▼
   ┌──► q0                 └──────────┐               ┌──────────┐   J
   │    │  F                          ▼               │   *qA    ├──────► *qS
 (inicio)│         ┌──────────────►  qf  ──── F ────► (acepta)   │      (acepta)
        │          │ x                                └──────────┘
        │  F       │                R
        └────────► qpf ─────────────────────────────────► *qA
        │
        │  O          -          O           -          O
        └──► qO1 ───► qO2 ───► *qC1 ───► qO3 ───► *qC2 ──┐
                               (O-O)      │     (O-O-O)  │ J
                                 │ J      │              ▼
                                 └────────┴───────────► *qS
```

*(Las transiciones a `qdead` se omiten del diagrama por claridad, como es
convención: cualquier símbolo no dibujado lleva al estado trampa.)*

Una versión renderizable está en [`afd_diagrama.dot`](afd_diagrama.dot)
(ver sección "Cómo generar el diagrama").

### Equivalencia Regex ↔ AFD (Teorema de Kleene)

El **Teorema de Kleene** garantiza que todo lenguaje descrito por una expresión
regular puede ser reconocido por un autómata finito, y viceversa. El programa
**demuestra empíricamente** esta equivalencia: valida cada cadena de prueba con
el AFD y con la Regex de Python y comprueba que **coinciden en el 100 % de los
casos** (0 discrepancias en la sección 3 de la salida).

---

## 5. (2.4.1) Cómo ejecutar el reconocedor

```bash
# 1) Demo completa (jugadas válidas, inválidas, equivalencia y movetext):
python3 afd_ajedrez.py

# 2) Validar jugadas sueltas (muestra la traza estado a estado del AFD):
python3 afd_ajedrez.py e4 Nf3 O-O Qh5+ e9 Pe4

# 3) Validar una línea de movetext PGN completa:
python3 afd_ajedrez.py --movetext "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0"
```

Ejemplo de traza que imprime el programa para `Nxe4`:

```
  Entrada: 'Nxe4'
       q0  --N(P)-->  qP    leida una pieza [KQRBN]
       qP  --x(x)-->  qf    esperando columna destino tras captura
       qf  --e(F)-->  qr    esperando fila destino
       qr  --4(R)-->  qA    ACEPTA: jugada completa
    [OK] ACEPTADA (jugada valida)   estado final = qA
```

### Cómo generar el diagrama (opcional, para el informe)

Si tienes Graphviz instalado:

```bash
dot -Tpng afd_diagrama.dot -o afd_diagrama.png
```

(o pega el contenido de `afd_diagrama.dot` en https://dreampuf.github.io/GraphvizOnline)

---

## 6. Puntos clave para la defensa individual

1. **Por qué es regular (y por qué importa):** una jugada SAN básica no tiene
   estructura anidada, así que un AFD (memoria finita) basta. El PGN *completo*
   (con variantes y comentarios anidados) **no** lo es → necesitaría una GLC.
   Esto conecta directamente con la **Jerarquía de Chomsky**: Tipo 3 (regular)
   vs. Tipo 2 (libre de contexto).
2. **Estado muerto `qdead`:** modela el rechazo. Hace al autómata *completo*
   (δ está definida para todo par estado–símbolo).
3. **Relación con el compilador:** este AFD es exactamente lo que hace el
   **analizador léxico (scanner/tokenizer)** de un compilador: reconocer tokens
   válidos mediante expresiones regulares implementadas como autómatas finitos.
4. **Equivalencia Regex ↔ AFD:** sustento teórico = **Teorema de Kleene**;
   el código lo verifica con 0 discrepancias.

---

## 7. Archivos de este directorio

| Archivo | Contenido |
|---------|-----------|
| [`afd_ajedrez.py`](afd_ajedrez.py) | AFD ejecutable + Regex + reconocedor de movetext |
| [`afd_diagrama.dot`](afd_diagrama.dot) | Diagrama del AFD en formato Graphviz |
| `README.md` | Esta documentación (base para la sección 2.4 del informe) |
