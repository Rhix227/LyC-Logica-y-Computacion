# Lexer para archivos Dockerfile (expresiones regulares)

**Universidad Nacional Experimental de Guayana**
**Lenguaje y Compiladores – Tema 4 (Análisis Léxico) – 2026-I**
**Actividad 2:** Construya un lexer para la verificación de archivos docker
mediante expresiones regulares.

## 1. Objetivo

Implementar, desde cero y usando el módulo `re` de Python, un analizador
léxico (lexer) capaz de leer un archivo `Dockerfile` y reconocer sus
componentes léxicos (tokens), siguiendo el mismo enfoque explicado en el
Tema 4 para el archivo `/etc/network/interfaces` de Debian.

## 2. Paso a paso de la construcción

### Paso 1 — Identificar el lenguaje L (Dockerfile)

Se analizó la sintaxis de un Dockerfile real y se identificaron sus
componentes léxicos principales:

| Componente léxico   | Ejemplo                                  |
|----------------------|-------------------------------------------|
| Comentario           | `# esto es un comentario`                |
| Instrucción reservada| `FROM`, `RUN`, `CMD`, `COPY`, `ENV`, etc. |
| Flag de instrucción  | `--from=builder`, `--chown=user:group`   |
| Variable ENV/ARG     | `APP_ENV=production`                     |
| Puerto/Número        | `8080/tcp`, `1000`                       |
| Cadena de texto      | `"daemon off;"`                          |
| Arreglo JSON (exec)  | `["python", "app.py"]`                   |
| Imagen con tag/digest| `python:3.12-slim`, `alpine@sha256:...`  |
| Ruta / identificador | `/app`, `requirements.txt`               |

### Paso 2 — Definir un token por cada componente léxico

En `lexer_docker.py`, la lista `tokens` define, en orden de prioridad, el
nombre de cada token y su expresión regular asociada. **El orden es
crítico**: igual que en el ejemplo del Tema 4 (donde `INTERFACE_NAME`
"atrapaba" palabras mal escritas como `ddress`), aquí las reglas más
específicas (instrucciones reservadas, flags, variables ENV, puertos,
cadenas, JSON) se colocan **antes** que la regla genérica `IMAGEN_TAG`/`RUTA`,
para que estas últimas no absorban tokens que deberían reconocerse con un
tipo más preciso.

### Paso 3 — Construir la expresión regular maestra

La función `construir_regex()` concatena todos los patrones usando grupos
con nombre `(?P<NOMBRE>patron)`, exactamente igual a la técnica mostrada
en el material de clase (`token_regex = '|'.join(...)`).

### Paso 4 — Recorrer la entrada con `re.finditer`

La función `lexer(texto_entrada)`:
1. Recorre el texto con `re.finditer` sobre la regex maestra.
2. Detecta `mo.lastgroup` (el token que hizo match).
3. Ignora espacios, tabuladores y comentarios (`SKIP`, `COMMENT`).
4. Lleva la cuenta de línea/columna para reportar errores con precisión.
5. Ante un carácter no reconocido (`MISMATCH`), **no detiene la
   ejecución**: reporta el error léxico (carácter, línea, columna) y
   continúa leyendo el resto del archivo — esto corresponde al concepto
   de "autómata con estados fallidos" explicado en el Tema 4, que permite
   reportar varios errores en una sola pasada en lugar de detenerse en el
   primero.

### Paso 5 — Reportar resultados

Al final se imprime cada token reconocido `(tipo, lexema, línea, columna)`
y, si los hubo, todos los errores léxicos encontrados.

## 3. Requisitos

- Python 3.8 o superior (no requiere librerías externas, solo `re` y `sys`
  de la biblioteca estándar).

## 4. Cómo ejecutarlo

### Opción A — Ejecutar el script Python directamente

```bash
python3 lexer_docker.py <archivo_dockerfile>
```

Ejemplos incluidos en este paquete:

```bash
python3 lexer_docker.py ejemplo1_Dockerfile
python3 lexer_docker.py ejemplo2_Dockerfile
python3 lexer_docker.py ejemplo3_Dockerfile
```

Si no se indica ningún archivo, el programa intentará leer uno llamado
`Dockerfile` en el directorio actual:

```bash
python3 lexer_docker.py
```

### Opción B — Usar el ejecutable ya compilado (sin necesidad de Python instalado)

En la carpeta `dist/` se incluye un ejecutable standalone generado con
PyInstaller para Linux (`lexer_docker`). Para usarlo:

```bash
chmod +x dist/lexer_docker
./dist/lexer_docker ejemplo1_Dockerfile
```

> Nota: el ejecutable fue compilado en Linux x86_64. Si se necesita para
> otro sistema operativo, regenerarlo en esa plataforma con:
> `pip install pyinstaller --break-system-packages`
> `pyinstaller --onefile lexer_docker.py`

## 5. Ejemplos de ejecución (evidencia para el informe)

Ver el archivo `salidas_ejemplos.txt` incluido en este paquete, que contiene
la salida completa de correr el lexer sobre los tres Dockerfiles de prueba:

1. **ejemplo1_Dockerfile** — Dockerfile simple y correcto (app Python).
2. **ejemplo2_Dockerfile** — Dockerfile multi-stage con flags (`--from=`),
   digest `@sha256:...` y variables ARG/ENV.
3. **ejemplo3_Dockerfile** — Dockerfile con errores léxicos intencionales
   (caracteres `@@` sueltos) para demostrar la detección de errores.

## 6. Estructura del entregable (.zip)

```
docker_lexer/
├── lexer_docker.py          # Código fuente del lexer
├── ejemplo1_Dockerfile      # Caso de prueba 1 (correcto)
├── ejemplo2_Dockerfile      # Caso de prueba 2 (correcto, multi-stage)
├── ejemplo3_Dockerfile      # Caso de prueba 3 (con errores léxicos)
├── salidas_ejemplos.txt     # Salida de los 3 ejemplos ya ejecutados
├── README.md                # Este documento (pasos de construcción y uso)
└── dist/
    └── lexer_docker         # Ejecutable standalone (Linux, PyInstaller)
```

## 7. Conclusión

Al igual que en el analizador del archivo `interfaces` de Debian visto en
clase, este lexer demuestra que un lenguaje de configuración (Dockerfile)
puede tratarse como un lenguaje regular: basta con un conjunto de
expresiones regulares —equivalentes a un AFD— para tokenizar la entrada,
reportando errores léxicos sin necesidad de detener el análisis, y dejando
la validación del *orden* de las instrucciones (reglas sintácticas) para
una fase posterior de análisis sintáctico.
