"""
Pregunta 4 - Lexer y Parser para la seccion "networks" de docker-compose.yml
Implementacion en PYTHON (una de las 3 implementaciones del experimento de
carga; ver tambien java/LexerParser.java y c/lexer_parser.c, que replican EL
MISMO algoritmo para que la comparacion de tiempos sea justa entre lenguajes).

Subconjunto de YAML soportado (indentacion FIJA de 2 espacios, sin tabs):

  version: "<string>"
  services:
    <nombre>:
      image: <string>
      networks:
        - <nombre-red>
        ...
  networks:
    <nombre>:
      driver: <bridge|overlay|...>
      external: <true|false>
      attachable: <true|false>
      driver_opts:
        <clave>: <valor>
      ipam:
        driver: <string>
        config:
          - subnet: <cidr>
            gateway: <ip>

Fases:
  1) LEXER (tokenize_lines): convierte cada linea de texto en un token de
     linea {nivel, es_lista, clave, valor} (equivalente a KEY/COLON/DASH/
     VALUE + INDENT/DEDENT de un lexer sensible a indentacion tipo Python).
  2) PARSER (recursivo descendente dirigido por nivel de indentacion):
     construye un arbol generico (dict/list) y luego se extrae un resumen
     estructurado solo de la seccion "networks".
"""
import sys
import time
import json


class LineToken:
    __slots__ = ("level", "is_list", "key", "value")

    def __init__(self, level, is_list, key, value):
        self.level, self.is_list, self.key, self.value = level, is_list, key, value

    def __repr__(self):
        return f"LineToken(level={self.level}, dash={self.is_list}, key={self.key!r}, value={self.value!r})"


def tokenize_lines(text: str):
    """LEXER: produce un token por cada linea logica (no vacia, sin comentarios)."""
    tokens = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        stripped_left = raw.lstrip(" ")
        indent_spaces = len(raw) - len(stripped_left)
        if indent_spaces % 2 != 0:
            raise SyntaxError(f"Indentacion invalida (no multiplo de 2): {raw!r}")
        level = indent_spaces // 2
        content = stripped_left.rstrip()

        is_list = False
        if content.startswith("- "):
            is_list = True
            content = content[2:]
        elif content == "-":
            is_list = True
            content = ""

        key, value = None, None
        if ":" in content:
            k, _, v = content.partition(":")
            key = k.strip()
            v = v.strip()
            value = v if v != "" else None
        else:
            value = content.strip() if content.strip() else None

        tokens.append(LineToken(level, is_list, key, value))
    return tokens


class Parser:
    """PARSER recursivo descendente dirigido por nivel de indentacion."""

    def __init__(self, tokens):
        self.toks = tokens
        self.i = 0

    def peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else None

    def parse_block(self, level):
        """Parsea todas las lineas consecutivas con indentacion == level."""
        node = {}
        list_acc = None
        while True:
            tok = self.peek()
            if tok is None or tok.level < level:
                break
            if tok.level > level:
                raise SyntaxError(f"Indentacion inesperada en {tok}")

            if tok.is_list:
                if list_acc is None:
                    list_acc = []
                self.i += 1
                if tok.key is not None:
                    item = {tok.key: tok.value}
                    # puede haber mas claves del mismo item de lista a mayor nivel
                    sub = self.parse_block(level + 1)
                    item.update(sub)
                    list_acc.append(item)
                else:
                    list_acc.append(tok.value)
                node.setdefault("__list__", list_acc)
            else:
                self.i += 1
                if tok.value is not None:
                    node[tok.key] = tok.value
                else:
                    # bloque anidado
                    child = self.parse_block(level + 1)
                    node[tok.key] = child
        if list_acc is not None and len(node) == 1:
            return list_acc
        return node

    def parse(self):
        return self.parse_block(0)


def extract_networks_summary(tree: dict):
    """A partir del arbol generico, arma el resumen de la seccion networks."""
    networks = tree.get("networks", {})
    resumen = []
    if isinstance(networks, dict):
        for name, props in networks.items():
            if not isinstance(props, dict):
                continue
            entry = {
                "name": name,
                "driver": props.get("driver"),
                "external": props.get("external") == "true",
                "attachable": props.get("attachable") == "true",
            }
            entry["subnets"] = []
            ipam = props.get("ipam")
            if isinstance(ipam, dict) and isinstance(ipam.get("config"), list):
                entry["subnets"] = [c.get("subnet") for c in ipam["config"] if isinstance(c, dict)]
            resumen.append(entry)
    n_services = 0
    services = tree.get("services", {})
    if isinstance(services, dict):
        n_services = len(services)
    return {"n_services": n_services, "n_networks": len(resumen), "networks": resumen}


def parse_file(path: str):
    with open(path, "r") as f:
        text = f.read()
    tokens = tokenize_lines(text)
    tree = Parser(tokens).parse()
    return extract_networks_summary(tree)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 lexer_parser.py <archivo docker-compose.yml> [--json]")
        sys.exit(1)
    path = sys.argv[1]
    t0 = time.perf_counter()
    resumen = parse_file(path)
    t1 = time.perf_counter()
    if "--json" in sys.argv:
        print(json.dumps(resumen))
    else:
        print(f"Archivo: {path}")
        print(f"  Servicios: {resumen['n_services']}   Redes: {resumen['n_networks']}")
        for net in resumen["networks"]:
            print(f"   - {net}")
        print(f"Tiempo interno de parseo: {(t1 - t0) * 1000:.4f} ms")
