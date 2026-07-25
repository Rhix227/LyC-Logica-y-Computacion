"""
Pregunta 1 - Arbol de Sintaxis Abstracta (AST)
Lenguaje y Compiladores - Tema 5 (Analisis Sintactico)

Este programa implementa un lexer + parser recursivo descendente para un
subconjunto de expresiones aritmeticas y sentencias de asignacion, y construye
un Arbol de Sintaxis Abstracta (AST) explicito (no un arbol de analisis / parse
tree completo: se descartan parentesis, comas y palabras reservadas que no
aportan significado, conservando solo la jerarquia semantica).

Gramatica soportada (no ambigua, sin recursion izquierda para permitir
tambien su uso en el analisis LL de la pregunta 2):

    stmt        -> IDENT '=' expr
                 | expr

    expr        -> term ( ('+'|'-') term )*
    term        -> factor ( ('*'|'/') factor )*
    factor      -> NUMBER
                 | IDENT
                 | '(' expr ')'
                 | ('-') factor            # menos unario

Se incluyen DOS ejemplos de entrada distintos, tal como pide el enunciado:
  Ejemplo A: "3 + 4 * 2 - 1"
  Ejemplo B: "x = (1 + 2) * (3 - 4) / 5"
"""

from dataclasses import dataclass, field
from typing import List, Union


# ---------------------------------------------------------------------------
# 1) Definicion de los nodos del AST
# ---------------------------------------------------------------------------
@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class UnaryOp:
    op: str
    operand: "Node"

@dataclass
class BinOp:
    op: str
    left: "Node"
    right: "Node"

@dataclass
class Assign:
    target: str
    value: "Node"

Node = Union[Num, Var, UnaryOp, BinOp, Assign]


# ---------------------------------------------------------------------------
# 2) Lexer (Analizador Lexico) muy simple basado en expresiones regulares
# ---------------------------------------------------------------------------
import re

TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("IDENT",    r"[A-Za-z_][A-Za-z_0-9]*"),
    ("ASSIGN",   r"="),
    ("PLUS",     r"\+"),
    ("MINUS",    r"-"),
    ("MUL",      r"\*"),
    ("DIV",      r"/"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("SKIP",     r"[ \t]+"),
]
MASTER_RE = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in TOKEN_SPEC))


@dataclass
class Token:
    kind: str
    value: str


def tokenize(source: str) -> List[Token]:
    tokens = []
    for m in MASTER_RE.finditer(source):
        kind = m.lastgroup
        value = m.group()
        if kind == "SKIP":
            continue
        tokens.append(Token(kind, value))
    tokens.append(Token("EOF", ""))
    return tokens


# ---------------------------------------------------------------------------
# 3) Parser recursivo descendente (LL) que construye el AST
# ---------------------------------------------------------------------------
class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, kind: str) -> Token:
        tok = self.peek()
        if tok.kind != kind:
            raise ParseError(f"Se esperaba {kind} pero se encontro {tok.kind} ('{tok.value}')")
        return self.advance()

    def parse_stmt(self) -> Node:
        if self.peek().kind == "IDENT" and self.tokens[self.pos + 1].kind == "ASSIGN":
            name = self.advance().value
            self.expect("ASSIGN")
            value = self.parse_expr()
            return Assign(name, value)
        return self.parse_expr()

    def parse_expr(self) -> Node:
        node = self.parse_term()
        while self.peek().kind in ("PLUS", "MINUS"):
            op = self.advance().value
            right = self.parse_term()
            node = BinOp(op, node, right)
        return node

    def parse_term(self) -> Node:
        node = self.parse_factor()
        while self.peek().kind in ("MUL", "DIV"):
            op = self.advance().value
            right = self.parse_factor()
            node = BinOp(op, node, right)
        return node

    def parse_factor(self) -> Node:
        tok = self.peek()
        if tok.kind == "MINUS":
            self.advance()
            return UnaryOp("-", self.parse_factor())
        if tok.kind == "NUMBER":
            self.advance()
            return Num(float(tok.value))
        if tok.kind == "IDENT":
            self.advance()
            return Var(tok.value)
        if tok.kind == "LPAREN":
            self.advance()
            node = self.parse_expr()
            self.expect("RPAREN")
            return node
        raise ParseError(f"Token inesperado '{tok.value}' ({tok.kind})")


def parse(source: str) -> Node:
    tokens = tokenize(source)
    parser = Parser(tokens)
    tree = parser.parse_stmt()
    parser.expect("EOF")
    return tree


# ---------------------------------------------------------------------------
# 4) Utilidades para imprimir el AST (como arbol y evaluarlo)
# ---------------------------------------------------------------------------
def print_ast(node: Node, indent: str = "") -> None:
    if isinstance(node, Num):
        print(f"{indent}Num({node.value})")
    elif isinstance(node, Var):
        print(f"{indent}Var({node.name})")
    elif isinstance(node, UnaryOp):
        print(f"{indent}UnaryOp('{node.op}')")
        print_ast(node.operand, indent + "  ")
    elif isinstance(node, BinOp):
        print(f"{indent}BinOp('{node.op}')")
        print_ast(node.left, indent + "  ")
        print_ast(node.right, indent + "  ")
    elif isinstance(node, Assign):
        print(f"{indent}Assign('{node.target}')")
        print_ast(node.value, indent + "  ")


def evaluate(node: Node, env: dict) -> float:
    if isinstance(node, Num):
        return node.value
    if isinstance(node, Var):
        if node.name not in env:
            raise NameError(f"Variable no definida: {node.name}")
        return env[node.name]
    if isinstance(node, UnaryOp):
        val = evaluate(node.operand, env)
        return -val if node.op == "-" else val
    if isinstance(node, BinOp):
        l, r = evaluate(node.left, env), evaluate(node.right, env)
        return {"+": l + r, "-": l - r, "*": l * r, "/": l / r}[node.op]
    if isinstance(node, Assign):
        val = evaluate(node.value, env)
        env[node.target] = val
        return val
    raise TypeError(f"Nodo AST desconocido: {node}")


# ---------------------------------------------------------------------------
# 5) Demostracion con los DOS ejemplos requeridos
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    ejemplos = [
        "3 + 4 * 2 - 1",
        "x = (1 + 2) * (3 - 4) / 5",
    ]

    env = {}
    for i, fuente in enumerate(ejemplos, start=1):
        print("=" * 70)
        print(f"Ejemplo {chr(64+i)}: entrada -> {fuente}")
        print("-" * 70)
        tokens = tokenize(fuente)
        print("Tokens:", [(t.kind, t.value) for t in tokens if t.kind != 'EOF'])
        arbol = parse(fuente)
        print("\nAST:")
        print_ast(arbol)
        resultado = evaluate(arbol, env)
        print(f"\nResultado de evaluar el AST: {resultado}")
    print("=" * 70)
