"""
Pregunta 4 - Generador de archivos docker-compose de prueba.

Genera N archivos docker-compose*.yml (N=10, dentro del rango 5 < n < 20
pedido por el enunciado) con secciones "services" y "networks" de tamano
creciente, para poder graficar tiempo de ejecucion del lexer/parser en
funcion del tamano de la entrada (numero de redes/servicios) y del lenguaje
de implementacion.

Cada archivo respeta SIEMPRE una indentacion fija de 2 espacios por nivel
(sin tabs), condicion que asumen los 3 lexers (Python/Java/C) de esta
carpeta para simplificar el analisis de indentacion (equivalente a como
Flex/ANTLR asumirian un formato de entrada bien definido por la gramatica).
"""
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "samples")
os.makedirs(OUT_DIR, exist_ok=True)

N_FILES = 10  # 5 < n < 20


def build_compose(n_services: int, n_networks: int) -> str:
    lines = []
    lines.append('version: "3.8"')
    lines.append("services:")
    for s in range(n_services):
        name = f"svc{s+1}"
        lines.append(f"  {name}:")
        lines.append(f"    image: demo/{name}:1.0")
        lines.append("    networks:")
        # cada servicio se conecta a 1-3 redes (rotando)
        k = 1 + (s % min(3, n_networks))
        for j in range(k):
            net_idx = (s + j) % n_networks
            lines.append(f"      - net{net_idx+1}")
    lines.append("networks:")
    for net in range(n_networks):
        name = f"net{net+1}"
        lines.append(f"  {name}:")
        driver = "bridge" if net % 2 == 0 else "overlay"
        lines.append(f"    driver: {driver}")
        if net % 3 == 0:
            lines.append("    driver_opts:")
            lines.append(f"      com.docker.network.bridge.name: br-{name}")
        if net % 2 == 1:
            lines.append("    external: true")
            lines.append("    attachable: true")
        else:
            lines.append("    ipam:")
            lines.append("      driver: default")
            lines.append("      config:")
            lines.append(f"        - subnet: 172.{20+net}.0.0/16")
            lines.append(f"          gateway: 172.{20+net}.0.1")
    return "\n".join(lines) + "\n"


def main():
    for i in range(1, N_FILES + 1):
        n_services = 2 * i          # 2,4,...,20
        n_networks = max(2, i)      # 2,3,...,10
        content = build_compose(n_services, n_networks)
        path = os.path.join(OUT_DIR, f"docker-compose-{i:02d}.yml")
        with open(path, "w") as f:
            f.write(content)
        print(f"Generado {path}  (services={n_services}, networks={n_networks})")


if __name__ == "__main__":
    main()
