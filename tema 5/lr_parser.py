"""
Pregunta 2 - Analisis LR (ascendente)
Implementacion de un parser ascendente tipo shift-reduce (desplazamiento-
reduccion) por precedencia de operadores para el MISMO lenguaje L de
expresiones aritmeticas usado en ll_parser.py.

Gramatica (ambigua/con recursion izquierda -- forma NATURAL de LR, ya que a
diferencia de LL, LR SI admite recursion izquierda):

    E -> E + T | E - T | T
    T -> T * F | T / F | F
    F -> ( E ) | num

Nota metodologica: una tabla LR(1)/SLR(1) completa (con estados, GOTO y
ACTION generados automaticamente) es el trabajo que en la practica realizan
generadores como Bison/Yacc (ver pregunta 3). Para esta demostracion
academica de "como piensa" un parser ascendente construimos a mano un parser
shift-reduce dirigido por PRECEDENCIA DE OPERADORES (tecnica clasica de
analisis ascendente), que desplaza tokens a una pila y reduce por las
producciones de la gramatica de arriba cuando corresponde, mostrando en cada
paso la pila y la accion tomada (shift/reduce), igual que lo haria un parser
LR real.
"""
import re

TOKEN_RE = re.compile(r"\s*(?:(?P<NUM>\d+)|(?P<PLUS>\+)|(?P<MINUS>-)|(?P<MUL>\*)|(?P<DIV>/)|(?P<LP>\()|(?P<RP>\)))")

PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2}


def tokenize(s):
    pos, toks = 0, []
    while pos < len(s):
        m = TOKEN_RE.match(s, pos)
        if not m or m.end() == pos:
            if s[pos].isspace():
                pos += 1
                continue
            raise SyntaxError(f"Caracter invalido: {s[pos]!r}")
        pos = m.end()
        kind = m.lastgroup
        toks.append((kind, m.group(kind)))
    toks.append(("EOF", ""))
    return toks


class Node:
    """Nodo del AST resultante (mismo tipo de resultado que el parser LL)."""
    __slots__ = ("op", "left", "right", "value")

    def __init__(self, op=None, left=None, right=None, value=None):
        self.op, self.left, self.right, self.value = op, left, right, value

    def eval(self):
        if self.value is not None:
            return self.value
        l, r = self.left.eval(), self.right.eval()
        return {"+": l + r, "-": l - r, "*": l * r, "/": l / r}[self.op]

    def __repr__(self):
        if self.value is not None:
            return str(self.value)
        return f"({self.left!r} {self.op} {self.right!r})"


class LRShiftReduceParser:
    """
    Parser ascendente shift-reduce por precedencia de operadores.
    Pila mixta de tokens y nodos AST ya reducidos. En cada iteracion:
      - SHIFT: si el operador en el tope de pila tiene MENOR precedencia que
        el operador de entrada (o la pila no tiene operador pendiente), se
        desplaza el token de entrada a la pila.
      - REDUCE: en caso contrario, se reduce el tope de la pila aplicando la
        produccion correspondiente (T -> T op F, o similar) construyendo un
        nodo BinOp del AST.
    """

    OPS = ("PLUS", "MINUS", "MUL", "DIV")

    def __init__(self, tokens, traza=True):
        self.toks = tokens
        self.i = 0
        self.traza = traza

    def _log(self, accion, pila):
        if self.traza:
            rep = " ".join(e if isinstance(e, str) else repr(e) for e in pila)
            print(f"{accion:<22} | Pila: [{rep}]  Entrada: {self._resto()}")

    def _resto(self):
        return " ".join(v for k, v in self.toks[self.i:] if k != "EOF")

    def peek(self):
        return self.toks[self.i]

    def eat(self):
        tok = self.toks[self.i]
        self.i += 1
        return tok

    def parse_primary(self):
        tok = self.peek()
        if tok[0] == "NUM":
            self.eat()
            return Node(value=float(tok[1]))
        if tok[0] == "LP":
            self.eat()
            inner = self.parse_expr()
            closep = self.peek()
            if closep[0] != "RP":
                raise SyntaxError("LR: se esperaba ')'")
            self.eat()
            return inner
        raise SyntaxError(f"LR: token inesperado {tok}")

    def _reduce(self, pila):
        """REDUCE: pila = [..., left, op, right]  ->  [..., Node(op,left,right)]"""
        right = pila.pop()
        op = pila.pop()
        left = pila.pop()
        pila.append(Node(op=op, left=left, right=right))
        self._log(f"REDUCE {op}", pila)

    def parse_expr(self):
        """
        Parser shift-reduce explicito por precedencia de operadores (estilo LR):
        se mantiene una PILA visible de operandos (Node) y operadores (str).
        Se hace SHIFT del siguiente token/operando mientras el operador en el
        tope de pila tenga MENOR precedencia que el que sigue en la entrada;
        en caso contrario se hace REDUCE (se resuelve el tope de la pila).
        """
        pila = [self.parse_primary()]
        self._log("SHIFT primario", pila)
        while True:
            tok = self.peek()
            if tok[0] not in self.OPS:
                break
            op_entrada = tok[1]
            # Reduce mientras el operador en la pila tenga precedencia >= al de entrada
            while len(pila) >= 3 and PRECEDENCE[pila[-2]] >= PRECEDENCE[op_entrada]:
                self._reduce(pila)
            self.eat()
            pila.append(op_entrada)
            self._log(f"SHIFT   {op_entrada}", pila)
            pila.append(self.parse_primary())
            self._log("SHIFT primario", pila)
        while len(pila) > 1:
            self._reduce(pila)
        return pila[0]

    def parse(self):
        tree = self.parse_expr()
        if self.peek()[0] != "EOF":
            raise SyntaxError("LR: tokens sobrantes tras el analisis")
        return tree


def parse_lr(source, traza=True):
    tokens = tokenize(source)
    parser = LRShiftReduceParser(tokens, traza)
    return parser.parse()


if __name__ == "__main__":
    for expr in ["3 + 4 * 2 - 1", "(1 + 2) * (3 - 4) / 5"]:
        print("=" * 70)
        print("Entrada:", expr)
        print("-" * 70)
        arbol = parse_lr(expr, traza=True)
        print("-" * 70)
        print("AST resultante:", arbol)
        print("Resultado (LR):", arbol.eval())
