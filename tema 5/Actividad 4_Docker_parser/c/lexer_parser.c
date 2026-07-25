/*
 * Pregunta 4 - Lexer y Parser para la seccion "networks" de docker-compose.yml
 * Implementacion en C. Replica el MISMO algoritmo que python/lexer_parser.py
 * y java/LexerParser.java (mismo lexer basado en lineas + indentacion, mismo
 * parser recursivo descendente dirigido por nivel), para que el experimento
 * de carga compare el costo de EJECUCION en distintos lenguajes sobre el
 * mismo trabajo, no algoritmos distintos.
 *
 * Compilar:  gcc -O2 -o lexer_parser lexer_parser.c
 * Ejecutar:  ./lexer_parser archivo.yml [--json]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

#define MAX_LINES 4096
#define MAX_LINE_LEN 512

typedef struct {
    int level;
    int is_list;
    char key[128];   /* "" si no hay clave */
    char value[256];  /* "" si no hay valor */
    int has_key;
    int has_value;
} LineToken;

static LineToken tokens[MAX_LINES];
static int n_tokens = 0;

static void rstrip(char *s) {
    int len = (int)strlen(s);
    while (len > 0 && isspace((unsigned char)s[len - 1])) {
        s[--len] = '\0';
    }
}

/* ------------------------- LEXER ------------------------------------- */
static void tokenize_lines(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) {
        fprintf(stderr, "No se pudo abrir %s\n", path);
        exit(1);
    }
    char raw[MAX_LINE_LEN];
    n_tokens = 0;
    while (fgets(raw, sizeof(raw), f)) {
        /* quitar salto de linea */
        raw[strcspn(raw, "\n")] = '\0';

        /* linea vacia (solo espacios) -> ignorar */
        int only_ws = 1;
        for (char *p = raw; *p; p++) if (!isspace((unsigned char)*p)) { only_ws = 0; break; }
        if (only_ws) continue;

        int indent = 0;
        while (raw[indent] == ' ') indent++;
        if (indent % 2 != 0) {
            fprintf(stderr, "Indentacion invalida (no multiplo de 2): %s\n", raw);
            exit(1);
        }
        int level = indent / 2;
        char content[MAX_LINE_LEN];
        strcpy(content, raw + indent);
        rstrip(content);

        int is_list = 0;
        char *cp = content;
        if (strncmp(cp, "- ", 2) == 0) {
            is_list = 1;
            cp += 2;
        } else if (strcmp(cp, "-") == 0) {
            is_list = 1;
            cp += 1;
        }

        LineToken tok;
        memset(&tok, 0, sizeof(tok));
        tok.level = level;
        tok.is_list = is_list;

        char *colon = strchr(cp, ':');
        if (colon) {
            int klen = (int)(colon - cp);
            strncpy(tok.key, cp, klen);
            tok.key[klen] = '\0';
            /* trim key derecha */
            rstrip(tok.key);
            tok.has_key = (strlen(tok.key) > 0);

            char *v = colon + 1;
            while (*v == ' ') v++;
            strcpy(tok.value, v);
            rstrip(tok.value);
            tok.has_value = (strlen(tok.value) > 0);
        } else {
            char v[MAX_LINE_LEN];
            strcpy(v, cp);
            /* trim izquierda */
            char *vp = v;
            while (*vp == ' ') vp++;
            strcpy(tok.value, vp);
            rstrip(tok.value);
            tok.has_value = (strlen(tok.value) > 0);
        }

        if (n_tokens >= MAX_LINES) {
            fprintf(stderr, "Demasiadas lineas (limite %d)\n", MAX_LINES);
            exit(1);
        }
        tokens[n_tokens++] = tok;
    }
    fclose(f);
}

/* ------------------------- Resultado (resumen) ------------------------ */
typedef struct {
    char name[128];
    char driver[64];
    int external;
    int attachable;
    char subnets[8][64];
    int n_subnets;
} NetworkEntry;

static NetworkEntry networks_out[64];
static int n_networks_out = 0;
static int n_services_out = 0;

/* ------------------------- PARSER -------------------------------------
 * Parser recursivo descendente dirigido por nivel de indentacion.
 * En lugar de construir un arbol generico dinamico (como en Python/Java),
 * en C recorremos directamente reconociendo las claves de interes
 * ("services" y "networks" y sus subclaves), lo cual es equivalente en
 * poder de reconocimiento pero mas simple/eficiente en un lenguaje sin
 * recoleccion de basura ni contenedores genericos incorporados.
 * ---------------------------------------------------------------------- */
static int pos = 0;

static LineToken *peek(void) {
    return (pos < n_tokens) ? &tokens[pos] : NULL;
}

/* Salta (consume) un bloque completo de nivel >= min_level (usado para
 * ignorar subarboles que no nos interesan, ej. "image:", "driver_opts:"). */
static void skip_block(int min_level) {
    while (peek() && peek()->level >= min_level) pos++;
}

static void parse_service_networks(int level) {
    while (peek() && peek()->level >= level) {
        if (!peek()->is_list) break;
        pos++; /* consumimos "- netX" */
    }
}

static void parse_service(int level) {
    /* level = nivel de las propiedades del servicio (image:, networks:) */
    while (peek() && peek()->level == level) {
        LineToken *t = peek();
        if (t->has_key && strcmp(t->key, "networks") == 0 && !t->has_value) {
            pos++;
            parse_service_networks(level + 1);
        } else {
            pos++;
            if (!t->has_value) skip_block(level + 1);
        }
    }
}

static void parse_services(int level) {
    /* level = nivel de "svcN:" */
    while (peek() && peek()->level == level && !peek()->is_list) {
        pos++; /* nombre del servicio */
        n_services_out++;
        parse_service(level + 1);
    }
}

static void parse_ipam(int level, NetworkEntry *net) {
    while (peek() && peek()->level >= level) {
        LineToken *t = peek();
        if (t->level == level && t->has_key && strcmp(t->key, "config") == 0 && !t->has_value) {
            pos++;
            /* lista de mapas: cada item "- subnet: ... / gateway: ..." */
            while (peek() && peek()->level >= level + 1 && peek()->is_list) {
                LineToken *item = peek();
                if (item->has_key && strcmp(item->key, "subnet") == 0 && net->n_subnets < 8) {
                    strcpy(net->subnets[net->n_subnets++], item->value);
                }
                pos++;
                /* posibles claves adicionales del mismo item (ej. gateway) a nivel+2 */
                while (peek() && peek()->level >= level + 2) pos++;
            }
        } else if (t->level >= level) {
            pos++;
        } else {
            break;
        }
    }
}

static void parse_network_props(int level, NetworkEntry *net) {
    while (peek() && peek()->level == level) {
        LineToken *t = peek();
        if (t->has_key && strcmp(t->key, "driver") == 0 && t->has_value) {
            strcpy(net->driver, t->value);
            pos++;
        } else if (t->has_key && strcmp(t->key, "external") == 0 && t->has_value) {
            net->external = (strcmp(t->value, "true") == 0);
            pos++;
        } else if (t->has_key && strcmp(t->key, "attachable") == 0 && t->has_value) {
            net->attachable = (strcmp(t->value, "true") == 0);
            pos++;
        } else if (t->has_key && strcmp(t->key, "ipam") == 0 && !t->has_value) {
            pos++;
            parse_ipam(level + 1, net);
        } else {
            pos++;
            if (!t->has_value) skip_block(level + 1);
        }
    }
}

static void parse_networks(int level) {
    /* level = nivel de "netN:" */
    while (peek() && peek()->level == level && !peek()->is_list) {
        NetworkEntry net;
        memset(&net, 0, sizeof(net));
        strcpy(net.name, peek()->key[0] ? peek()->key : peek()->value);
        pos++;
        parse_network_props(level + 1, &net);
        if (n_networks_out < 64) networks_out[n_networks_out++] = net;
    }
}

static void parse_root(void) {
    while (peek()) {
        LineToken *t = peek();
        if (t->level == 0 && t->has_key && strcmp(t->key, "services") == 0 && !t->has_value) {
            pos++;
            parse_services(1);
        } else if (t->level == 0 && t->has_key && strcmp(t->key, "networks") == 0 && !t->has_value) {
            pos++;
            parse_networks(1);
        } else {
            pos++;
        }
    }
}

/* ------------------------- Salida -------------------------------------- */
static void print_text(const char *path) {
    printf("Archivo: %s\n", path);
    printf("  Servicios: %d   Redes: %d\n", n_services_out, n_networks_out);
    for (int i = 0; i < n_networks_out; i++) {
        NetworkEntry *n = &networks_out[i];
        printf("   - name=%s driver=%s external=%s attachable=%s subnets=[",
               n->name, n->driver, n->external ? "true" : "false", n->attachable ? "true" : "false");
        for (int j = 0; j < n->n_subnets; j++) {
            printf("%s%s", j ? ", " : "", n->subnets[j]);
        }
        printf("]\n");
    }
}

static void print_json(void) {
    printf("{\"n_services\": %d, \"n_networks\": %d, \"networks\": [", n_services_out, n_networks_out);
    for (int i = 0; i < n_networks_out; i++) {
        NetworkEntry *n = &networks_out[i];
        printf("%s{\"name\": \"%s\", \"driver\": \"%s\", \"external\": %s, \"attachable\": %s, \"subnets\": [",
               i ? ", " : "", n->name, n->driver, n->external ? "true" : "false", n->attachable ? "true" : "false");
        for (int j = 0; j < n->n_subnets; j++) {
            printf("%s\"%s\"", j ? ", " : "", n->subnets[j]);
        }
        printf("]}");
    }
    printf("]}\n");
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Uso: %s <archivo docker-compose.yml> [--json]\n", argv[0]);
        return 1;
    }
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    tokenize_lines(argv[1]);
    pos = 0;
    n_networks_out = 0;
    n_services_out = 0;
    parse_root();

    clock_gettime(CLOCK_MONOTONIC, &t1);
    double ms = (t1.tv_sec - t0.tv_sec) * 1000.0 + (t1.tv_nsec - t0.tv_nsec) / 1e6;

    int json = (argc > 2 && strcmp(argv[2], "--json") == 0);
    if (json) {
        print_json();
    } else {
        print_text(argv[1]);
        printf("Tiempo interno de parseo: %.4f ms\n", ms);
    }
    return 0;
}
