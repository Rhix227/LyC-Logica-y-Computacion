"""
Pregunta 2 - Analisis LL (descendente)
Implementacion de un parser LL(1) recursivo descendente para el lenguaje L
de expresiones aritmeticas (mismo lenguaje L usado en lr_parser.py para poder
comparar ambas estrategias sobre las mismas entradas).

Gramatica LL(1) (sin recursion izquierda, forma requerida por LL):

    E  -> T E'
    E' -> + T E' | - T E' | eps
    T  -> F T'
    T' -> * F T' | / F T' | eps
    F  -> ( E ) | num

Se imprime la traza de llamadas (derivacion) para evidenciar el
funcionamiento "de arriba hacia abajo, con derivacion mas a la izquierda"
propio de LL (Left-to-right, Leftmost derivation).
"""
import re

TOKEN_RE = re.compile(r"\s*(?:(?P<NUM>\d+)|(?P<PLUS>\+)|(?P<MINUS>-)|(?P<MUL>\*)|(?P<DIV>/)|(?P<LP>\()|(?P<RP>\)))")


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


class LLParser:
    """Parser recursivo descendente = implementacion directa de la gramatica LL(1)."""

    def __init__(self, tokens, traza=True):
        self.toks = tokens
        self.i = 0
        self.traza = traza
        self.profundidad = 0

    def _log(self, regla):
        if self.traza:
            print("  " * self.profundidad + regla)

    def peek(self):
        return self.toks[self.i]

    def eat(self, kind):
        tok = self.toks[self.i]
        if tok[0] != kind:
            raise SyntaxError(f"LL: se esperaba {kind}, se obtuvo {tok}")
        self.i += 1
        return tok

    def parse(self):
        val = self.E()
        self.eat("EOF")
        return val

    def E(self):
        self._log("E -> T E'")
        self.profundidad += 1
        v = self.T()
        v = self.Eprime(v)
        self.profundidad -= 1
        return v

    def Eprime(self, acc):
        tok = self.peek()
        if tok[0] == "PLUS":
            self._log("E' -> + T E'")
            self.eat("PLUS")
            self.profundidad += 1
            v = self.T()
            self.profundidad -= 1
            return self.Eprime(acc + v)
        if tok[0] == "MINUS":
            self._log("E' -> - T E'")
            self.eat("MINUS")
            self.profundidad += 1
            v = self.T()
            self.profundidad -= 1
            return self.Eprime(acc - v)
        self._log("E' -> epsilon")
        return acc

    def T(self):
        self._log("T -> F T'")
        self.profundidad += 1
        v = self.F()
        v = self.Tprime(v)
        self.profundidad -= 1
        return v

    def Tprime(self, acc):
        tok = self.peek()
        if tok[0] == "MUL":
            self._log("T' -> * F T'")
            self.eat("MUL")
            self.profundidad += 1
            v = self.F()
            self.profundidad -= 1
            return self.Tprime(acc * v)
        if tok[0] == "DIV":
            self._log("T' -> / F T'")
            self.eat("DIV")
            self.profundidad += 1
            v = self.F()
            self.profundidad -= 1
            return self.Tprime(acc / v)
        self._log("T' -> epsilon")
        return acc

    def F(self):
        tok = self.peek()
        if tok[0] == "NUM":
            self._log(f"F -> num ({tok[1]})")
            self.eat("NUM")
            return float(tok[1])
        if tok[0] == "LP":
            self._log("F -> ( E )")
            self.eat("LP")
            self.profundidad += 1
            v = self.E()
            self.profundidad -= 1
            self.eat("RP")
            return v
        raise SyntaxError(f"LL: token inesperado en F: {tok}")


def parse_ll(source, traza=True):
    tokens = tokenize(source)
    return LLParser(tokens, traza).parse()


if __name__ == "__main__":
    for expr in ["3 + 4 * 2 - 1", "(1 + 2) * (3 - 4) / 5"]:
        print("=" * 60)
        print("Entrada:", expr)
        print("-" * 60)
        resultado = parse_ll(expr, traza=True)
        print("-" * 60)
        print("Resultado (LL):", resultado)
