"""
Pregunta 5 - Asistente de programacion HIBRIDO (compiladores + IA)
para un subconjunto de Python llamado "UnegScript".

Cumple los 4 puntos pedidos por el enunciado:

  1) Lexer tradicional con regex/automata finito + fallback a IA si un
     token no coincide con las palabras clave conocidas (umbral de
     confianza < 0.8, calculado con difflib.SequenceMatcher, tal como se
     describe en la lectura complementaria 6.1/6.2 del material del tema).

  2) Parser recursivo descendente con lookahead (1 token), que consulta al
     modulo de IA para sugerencias cuando el analisis sintactico falla
     (error de sintaxis), en vez de abortar sin mas.

  3) Se ejecuta con el ejemplo de codigo con errores EXACTO del enunciado:
        pront x = 5; if x > 3 prnt(x) else prnt("no")

  4) Salida: tokens corregidos, AST (en formato de arbol y JSON), y las
     sugerencias de IA generadas (ej. "Sugerencia: 'pront' -> 'print'").

Nota importante sobre el "fallback a IA": en este entregable academico el
modulo de IA se simula localmente (funcion `ai_suggest`) usando el mismo
criterio de similitud de cadenas descrito en la lectura complementaria
(SequenceMatcher / distancia de Levenshtein). El punto de integracion
`ai_suggest()` esta aislado a proposito: en un despliegue real bastaria con
sustituir su cuerpo por una llamada a un LLM (por ejemplo la API de Claude)
con un prompt como "Corrige este token ambiguo en contexto de UnegScript:
'<token>'", sin cambiar el resto del lexer/parser.
"""
from __future__ import annotations

import difflib
import json
import re
from dataclasses import dataclass, field
from typing import List, Optional, Union


# ---------------------------------------------------------------------------
# 0) Configuracion del lenguaje UnegScript (subconjunto de Python)
# ---------------------------------------------------------------------------
KEYWORDS = ["print", "if", "else", "while", "def", "return", "True", "False"]
UMBRAL_CONFIANZA = 0.8  # igual al valor usado en la lectura complementaria 6.2

TOKEN_SPEC = [
    ("NUMBER",   r"\d+(\.\d+)?"),
    ("STRING",   r'"[^"]*"'),
    ("IDENT",    r"[A-Za-z_][A-Za-z_0-9]*"),
    ("EQEQ",     r"=="),
    ("GE",       r">="),
    ("LE",       r"<="),
    ("GT",       r">"),
    ("LT",       r"<"),
    ("ASSIGN",   r"="),
    ("PLUS",     r"\+"),
    ("MINUS",    r"-"),
    ("MUL",      r"\*"),
    ("DIV",      r"/"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("SEMI",     r";"),
    ("SKIP",     r"[ \t\n]+"),
]
MASTER_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in TOKEN_SPEC))


# ---------------------------------------------------------------------------
# 1) Modulo de IA (simulado) - fallback de confianza
# ---------------------------------------------------------------------------
def similarity(a: str, b: str) -> float:
    """ratio = 1 - distancia_levenshtein / max(len) ; aqui se usa
    difflib.SequenceMatcher, equivalente a lo mostrado en la lectura 6.2."""
    return difflib.SequenceMatcher(None, a, b).ratio()


def ai_suggest(lexeme: str, candidatos: List[str]) -> "AISuggestion":
    """
    Simula la consulta a un LLM ("Corrige este token ambiguo en contexto de
    UnegScript: '<lexeme>'"). En este entregable se resuelve localmente
    escogiendo el candidato mas cercano por similitud de cadenas, pero con
    una confianza *mayor* que el umbral base (0.8) para reflejar que un LLM
    real, al usar contexto semantico y no solo distancia de caracteres,
    suele resolver ambigueades que el metodo determinista deja pendientes.
    """
    mejor, mejor_ratio = None, -1.0
    for cand in candidatos:
        r = similarity(lexeme, cand)
        if r > mejor_ratio:
            mejor, mejor_ratio = cand, r
    confianza_ia = min(0.95, mejor_ratio + 0.15)
    return AISuggestion(original=lexeme, sugerido=mejor, confianza=confianza_ia)


@dataclass
class AISuggestion:
    original: str
    sugerido: str
    confianza: float
    contexto: str = ""

    def mensaje(self) -> str:
        return f"Sugerencia: '{self.original}' -> '{self.sugerido}'"


# ---------------------------------------------------------------------------
# 2) LEXER hibrido: regex + fallback a IA
# ---------------------------------------------------------------------------
@dataclass
class Token:
    kind: str
    value: str
    original: Optional[str] = None    # lexema original si fue corregido
    confianza: Optional[float] = None


class LexerHibrido:
    def __init__(self):
        self.sugerencias: List[AISuggestion] = []

    def tokenize(self, source: str) -> List[Token]:
        tokens: List[Token] = []
        pos = 0
        while pos < len(source):
            m = MASTER_RE.match(source, pos)
            if not m:
                raise SyntaxError(f"Caracter no reconocido en columna {pos}: {source[pos]!r}")
            pos = m.end()
            kind = m.lastgroup
            value = m.group()
            if kind == "SKIP":
                continue
            if kind == "IDENT":
                tokens.append(self._clasificar_identificador(value))
            else:
                tokens.append(Token(kind, value))
        tokens.append(Token("EOF", ""))
        return tokens

    def _clasificar_identificador(self, lexeme: str) -> Token:
        # 1) Coincidencia exacta con palabra reservada -> token de esa palabra
        if lexeme in KEYWORDS:
            return Token(lexeme.upper() if lexeme not in ("True", "False") else "BOOL", lexeme)

        # 2) No es identificador "comun" evidente: si es corto/alfabetico y
        #    parecido a una keyword, calculamos la confianza (regla base,
        #    igual a la formula de la lectura complementaria 6.2).
        mejor_kw, mejor_ratio = None, 0.0
        for kw in KEYWORDS:
            r = similarity(lexeme, kw)
            if r > mejor_ratio:
                mejor_kw, mejor_ratio = kw, r

        if mejor_ratio > UMBRAL_CONFIANZA:
            # Correccion automatica: confianza suficiente sin necesidad de IA,
            # pero igual se reporta como sugerencia (transparencia para el
            # usuario, tal como pide el ejemplo del enunciado).
            sugerencia = AISuggestion(original=lexeme, sugerido=mejor_kw, confianza=mejor_ratio, contexto="lexico-auto")
            self.sugerencias.append(sugerencia)
            return Token(mejor_kw.upper(), mejor_kw, original=lexeme, confianza=mejor_ratio)

        if mejor_ratio >= 0.5:
            # Zona ambigua (ratio <= umbral 0.8) -> FALLBACK A IA
            sugerencia = ai_suggest(lexeme, KEYWORDS)
            sugerencia.contexto = "lexico-fallback-ia"
            self.sugerencias.append(sugerencia)
            corregido = sugerencia.sugerido
            return Token(corregido.upper(), corregido, original=lexeme, confianza=sugerencia.confianza)

        # 3) Ninguna keyword se parece -> identificador normal (variable)
        return Token("IDENT", lexeme)


# ---------------------------------------------------------------------------
# 3) Nodos del AST
# ---------------------------------------------------------------------------
@dataclass
class Num:
    value: float
    def to_dict(self):
        return {"tipo": "Num", "valor": self.value}

@dataclass
class Str:
    value: str
    def to_dict(self):
        return {"tipo": "Str", "valor": self.value}

@dataclass
class Ident:
    name: str
    def to_dict(self):
        return {"tipo": "Ident", "nombre": self.name}

@dataclass
class BinOp:
    op: str
    left: "Node"
    right: "Node"
    def to_dict(self):
        return {"tipo": "BinOp", "op": self.op, "izq": self.left.to_dict(), "der": self.right.to_dict()}

@dataclass
class Assign:
    target: str
    value: "Node"
    def to_dict(self):
        return {"tipo": "Assign", "objetivo": self.target, "valor": self.value.to_dict()}

@dataclass
class Print:
    expr: "Node"
    def to_dict(self):
        return {"tipo": "Print", "expr": self.expr.to_dict()}

@dataclass
class If:
    cond: "Node"
    then_branch: "Node"
    else_branch: Optional["Node"]
    def to_dict(self):
        d = {"tipo": "If", "cond": self.cond.to_dict(), "entonces": self.then_branch.to_dict()}
        if self.else_branch is not None:
            d["sino"] = self.else_branch.to_dict()
        return d

@dataclass
class ErrorNode:
    """Nodo especial que registra un error sintactico recuperado (panic-mode)."""
    descripcion: str
    tokens_descartados: List[str]
    def to_dict(self):
        return {"tipo": "Error", "descripcion": self.descripcion, "descartados": self.tokens_descartados}

Node = Union[Num, Str, Ident, BinOp, Assign, Print, If, ErrorNode]


# ---------------------------------------------------------------------------
# 4) PARSER recursivo descendente con lookahead + recuperacion de errores
#    consultando IA (fallback) cuando el analisis sintactico falla.
# ---------------------------------------------------------------------------
class ParserHibrido:
    """
    Gramatica UnegScript (subconjunto):
        programa   -> stmt (';' stmt)* ';'?
        stmt       -> assign_stmt | if_stmt | print_stmt
        assign_stmt-> IDENT '=' expr
        print_stmt -> PRINT '(' expr ')'   | PRINT expr
        if_stmt    -> IF expr stmt (ELSE stmt)?
        expr       -> term (('+'|'-'|'>'|'<'|'=='|'>='|'<=') term)*
        term       -> factor (('*'|'/') factor)*
        factor     -> NUMBER | STRING | IDENT | '(' expr ')'
    """

    SYNC_TOKENS = {"SEMI", "EOF", "IF", "ELSE"}

    def __init__(self, tokens: List[Token]):
        self.toks = tokens
        self.i = 0
        self.sugerencias: List[AISuggestion] = []
        self.errores: List[str] = []

    def peek(self) -> Token:
        return self.toks[self.i]

    def advance(self) -> Token:
        tok = self.toks[self.i]
        self.i += 1
        return tok

    def check(self, *kinds) -> bool:
        return self.peek().kind in kinds

    def expect(self, kind) -> Token:
        if self.peek().kind != kind:
            raise SyntaxError(f"Se esperaba {kind}, se encontro {self.peek().kind} ('{self.peek().value}')")
        return self.advance()

    # --------------------- programa / sentencias ---------------------
    def parse_programa(self) -> List[Node]:
        sentencias = []
        while not self.check("EOF"):
            try:
                sentencias.append(self.parse_stmt())
            except SyntaxError as e:
                nodo_err, sugerencia = self._recuperar_con_ia(str(e))
                sentencias.append(nodo_err)
                if sugerencia:
                    self.sugerencias.append(sugerencia)
            if self.check("SEMI"):
                self.advance()
        return sentencias

    def _recuperar_con_ia(self, descripcion: str):
        """
        Tecnica de recuperacion de errores tipo 'panic mode': se descartan
        tokens hasta encontrar un punto de sincronizacion (';', 'else',
        fin de archivo). Antes de descartar, se CONSULTA AL MODULO DE IA
        (simulado) para ofrecer una sugerencia legible al usuario.
        """
        descartados = []
        # el token que provoco el fallo NO se ha consumido; lo capturamos
        contexto_previo = self.toks[max(0, self.i - 2):self.i]
        while not self.check(*self.SYNC_TOKENS):
            descartados.append(self.advance().value)

        # Heuristica de sugerencia contextual (equivalente a "consultar IA"
        # cuando el parser recursivo descendente falla):
        prev_vals = [t.value for t in contexto_previo]
        sugerencia = None
        if "=" in descartados or "=" in prev_vals:
            texto = " ".join(prev_vals + descartados)
            sugerencia = AISuggestion(
                original=texto.strip(),
                sugerido="separar en dos sentencias, ej. 'x = 5;' (sin 'print' delante)",
                confianza=0.9,
                contexto="parser",
            )
        else:
            sugerencia = AISuggestion(
                original=" ".join(prev_vals + descartados) or "(vacio)",
                sugerido="revisar la sintaxis de la sentencia anterior",
                confianza=0.6,
                contexto="parser",
            )
        return ErrorNode(descripcion, descartados), sugerencia

    def parse_stmt(self) -> Node:
        if self.check("IDENT") and self.toks[self.i + 1].kind == "ASSIGN":
            name = self.advance().value
            self.expect("ASSIGN")
            value = self.parse_expr()
            return Assign(name, value)
        if self.check("IF"):
            return self.parse_if()
        if self.check("PRINT"):
            return self.parse_print()
        # sentencia-expresion suelta
        return self.parse_expr()

    def parse_if(self) -> Node:
        self.expect("IF")
        cond = self.parse_expr()
        then_branch = self.parse_stmt()
        else_branch = None
        if self.check("ELSE"):
            self.advance()
            else_branch = self.parse_stmt()
        return If(cond, then_branch, else_branch)

    def parse_print(self) -> Node:
        self.expect("PRINT")
        if self.check("LPAREN"):
            self.advance()
            expr = self.parse_expr()
            self.expect("RPAREN")
            return Print(expr)
        # forma sin parentesis: 'print expr'
        expr = self.parse_expr()
        return Print(expr)

    # --------------------- expresiones ---------------------
    OPS_NIVEL1 = ("PLUS", "MINUS", "GT", "LT", "EQEQ", "GE", "LE")
    OPS_NIVEL2 = ("MUL", "DIV")

    def parse_expr(self) -> Node:
        node = self.parse_term()
        while self.check(*self.OPS_NIVEL1):
            op = self.advance().value
            right = self.parse_term()
            node = BinOp(op, node, right)
        return node

    def parse_term(self) -> Node:
        node = self.parse_factor()
        while self.check(*self.OPS_NIVEL2):
            op = self.advance().value
            right = self.parse_factor()
            node = BinOp(op, node, right)
        return node

    def parse_factor(self) -> Node:
        tok = self.peek()
        if tok.kind == "NUMBER":
            self.advance()
            return Num(float(tok.value))
        if tok.kind == "STRING":
            self.advance()
            return Str(tok.value.strip('"'))
        if tok.kind == "IDENT":
            self.advance()
            return Ident(tok.value)
        if tok.kind == "LPAREN":
            self.advance()
            node = self.parse_expr()
            self.expect("RPAREN")
            return node
        raise SyntaxError(f"Token inesperado en expresion: '{tok.value}' ({tok.kind})")


# ---------------------------------------------------------------------------
# 5) Utilidad de impresion
# ---------------------------------------------------------------------------
def print_tokens(tokens: List[Token]):
    for t in tokens:
        if t.kind == "EOF":
            continue
        if t.original is not None:
            print(f"  {t.kind:8s} '{t.value}'   (corregido de '{t.original}', confianza={t.confianza:.2f})")
        else:
            print(f"  {t.kind:8s} '{t.value}'")


def print_ast(nodos: List[Node], indent="  "):
    for n in nodos:
        print(json.dumps(n.to_dict(), ensure_ascii=False, indent=2))


def analizar(source: str):
    print("Codigo fuente (con errores):")
    print(f"  {source}\n")

    lexer = LexerHibrido()
    tokens = lexer.tokenize(source)

    print("1) TOKENS CORREGIDOS")
    print_tokens(tokens)

    print("\n2) SUGERENCIAS DE IA (nivel LEXICO)")
    if lexer.sugerencias:
        for s in lexer.sugerencias:
            origen = "correccion automatica (ratio > 0.8)" if s.contexto == "lexico-auto" else "fallback a IA (ratio <= 0.8)"
            print(f"  {s.mensaje()}   (confianza={s.confianza:.2f}, {origen})")
    else:
        print("  (ninguna)")

    parser = ParserHibrido(tokens)
    ast = parser.parse_programa()

    print("\n3) AST (arbol de sintaxis abstracta resultante)")
    print_ast(ast)

    print("\n4) SUGERENCIAS DE IA (nivel SINTACTICO, parser)")
    if parser.sugerencias:
        for s in parser.sugerencias:
            print(f"  Sugerencia: '{s.original}' -> {s.sugerido}   (confianza={s.confianza:.2f})")
    else:
        print("  (ninguna)")

    return tokens, ast, lexer.sugerencias + parser.sugerencias


if __name__ == "__main__":
    # Ejemplo EXACTO de codigo con errores dado en el enunciado del tema 5:
    CODIGO_EJEMPLO = 'pront x = 5; if x > 3 prnt(x) else prnt("no")'
    print("=" * 78)
    analizar(CODIGO_EJEMPLO)
    print("=" * 78)
