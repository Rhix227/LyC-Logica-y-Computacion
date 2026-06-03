# Lenguaje L — ECO-GRID | Escenario Operativo A

> **** — Prevención de Fuga Térmica y Gestión de Alivio de Carga

---

## 1. Palabras Clave del Lenguaje L

### Control de flujo

| Keyword | Descripción |
|---------|-------------|
| `init_grid` | Primera sentencia obligatoria — inicializa el sistema ECO-GRID |
| `terminar` | Última sentencia obligatoria — cierra la ejecución del programa |
| `si_verdadero … entonces … sino … fin_si` | Estructura condicional (la rama `sino` es opcional) |
| `mientras … ejecutar … fin_mientras` | Estructura de repetición iterativa |
| `esperar(segundos)` | Pausa temporizada entre ciclos de evaluación |

### Sensores — lectura de dispositivos físicos

| Keyword | Retorna | Descripción |
|---------|---------|-------------|
| `leer_temperatura(bateria_id)` | DECIMAL (°C) | Temperatura actual del sensor de celda de un banco de baterías |

### Actuadores — acción sobre dispositivos físicos

| Keyword | Descripción |
|---------|-------------|
| `activar_refrigeracion(bateria_id)` | Enciende el sistema de refrigeración auxiliar sobre el banco indicado |
| `conmutar_linea(sector_id, estado)` | Conecta (`CONECTADO`) o aísla (`AISLADO`) un sector o línea de la red |
| `emitir_alerta("mensaje")` | Notifica al operador del sistema con un mensaje de estado o emergencia |

### Literales y operadores

| Categoría | Valores / Ejemplos |
|-----------|--------------------|
| Booleanos | `VERDADERO`, `FALSO` |
| Estados de actuador | `CONECTADO`, `AISLADO`, `ENCENDIDO`, `APAGADO` |
| Operadores relacionales | `>` `<` `>=` `<=` `==` `!=` |
| Operadores lógicos | `Y` (AND), `O` (OR), `NO` (NOT) |
| Operadores aritméticos | `+` `-` `*` `/` |
| Comentarios | `# texto` — ignorado por el analizador léxico |

---

## 2. Estructura Sintáctica del Lenguaje L

Notación EBNF simplificada de las construcciones usadas en el Escenario A:

```ebnf
Programa     ::= "init_grid" Sentencia* "terminar"

Sentencia    ::= Condicional
              |  Bucle
              |  Accion ";"
              |  Asignacion ";"

Asignacion   ::= IDENT "=" Expr

Condicional  ::= "si_verdadero" Cond "entonces" Sentencia*
                 [ "sino" Sentencia* ] "fin_si"

Bucle        ::= "mientras" Cond "ejecutar" Sentencia* "fin_mientras"

Cond         ::= Expr OPREL Expr
              |  Cond OPLOG Cond
              |  "NO" Cond
              |  "(" Cond ")"

Accion       ::= Llamada
Llamada      ::= IDENT "(" [ Args ] ")"
Args         ::= Expr { "," Expr }

Expr         ::= Termino { OPARIT Termino }
Termino      ::= IDENT | ENTERO | DECIMAL | BOOLEANO | ESTADO | CADENA
              |  Llamada | "(" Expr ")"
```

**Regla de no ambigüedad:** toda estructura de control abre con su palabra clave
(`si_verdadero`, `mientras`) y cierra con su marca explícita (`fin_si`, `fin_mientras`).
Las acciones y asignaciones terminan en `;`. Los bloques no dependen de la indentación.

---

## 3. Programa de Ejemplo — Escenario Operativo A

```
# ============================================================
#  PROGRAMA A  -  ECO-GRID  -  Prevencion de Fuga Termica y Gestion de Alivio de Carga
#  Lenguaje L  |  Ronniel e Yvanna
#  Escenario Operativo A: Monitoreo termico critico y proteccion del banco de baterias
# ============================================================

init_grid

    # --- Umbrales y parametros de seguridad termica ---
    UMBRAL_CRITICO_TEMP = 55          # grados Celsius: temperatura de peligro termico
    UMBRAL_TEMP_NORMAL  = 40          # grados Celsius: temperatura de retorno a operacion normal
    MAX_CICLOS_PELIGRO  = 5           # ciclos maximos tolerados antes de emitir emergencia total
    banco               = banco_1     # banco de baterias principal bajo monitoreo
    ciclos_en_peligro   = 0           # contador de ciclos consecutivos con temperatura critica

    activo = VERDADERO

    # --- Lazo de monitoreo termico continuo ---
    mientras activo == VERDADERO ejecutar

        temp = leer_temperatura(banco);       # lectura del sensor termico de celda del banco

        # CASO CRITICO: temperatura supera el umbral de seguridad -> riesgo de fuga termica
        si_verdadero temp > UMBRAL_CRITICO_TEMP entonces

            ciclos_en_peligro = ciclos_en_peligro + 1;

            # Acciones inmediatas de proteccion (orden determinista)
            activar_refrigeracion(banco);                            # 1. encender sistema de refrigeracion auxiliar
            conmutar_linea(linea_solar_carga, AISLADO);              # 2. desconectar ingreso de carga solar
            conmutar_linea(sector_industrial, AISLADO);              # 3. aislar sector industrial de la microred
            conmutar_linea(sector_industrial_respaldo, CONECTADO);   # 4. desviar consumo a red comercial de respaldo

            emitir_alerta("ALERTA TERMICA: temperatura critica detectada en banco de baterias");

            # Verificar si el peligro persiste tras el periodo maximo tolerado
            si_verdadero ciclos_en_peligro >= MAX_CICLOS_PELIGRO entonces
                emitir_alerta("EMERGENCIA CRITICA: fuga termica persistente - intervencion manual requerida");
                activo = FALSO;      # detener el ciclo automatico para forzar intervencion humana
            fin_si

        sino

            # Temperatura dentro del rango operativo seguro
            si_verdadero ciclos_en_peligro > 0 entonces

                # La temperatura bajo: restituir estado normal de la planta
                conmutar_linea(linea_solar_carga, CONECTADO);            # reconectar carga solar
                conmutar_linea(sector_industrial, CONECTADO);            # restituir sector industrial a microred
                conmutar_linea(sector_industrial_respaldo, AISLADO);     # desconectar respaldo comercial
                ciclos_en_peligro = 0;
                emitir_alerta("Temperatura normalizada: planta restituida a operacion normal");

            sino
                emitir_alerta("Monitoreo activo: temperatura en rango seguro");
            fin_si

        fin_si

        esperar(60);                # re-evaluar el estado termico cada 60 segundos

    fin_mientras

terminar
```

### Explicación lógico-sintáctica

1. `init_grid` … `terminar` delimitan el programa (regla raíz de la gramática).
2. El **bucle `mientras … ejecutar … fin_mientras`** modela el carácter continuo e iterativo del monitoreo térmico: re-evalúa cada 60 s mientras `activo == VERDADERO`.
3. Cada iteración lee el **sensor térmico** `leer_temperatura(banco)` y asigna el resultado a la variable `temp`.
4. **Condicional principal** `temp > UMBRAL_CRITICO_TEMP`: si la temperatura supera 55 °C, se incrementa `ciclos_en_peligro` y se disparan cuatro actuadores en orden determinista — primero refrigeración, luego el aislamiento de la fuente solar, el sector industrial y la conexión al respaldo comercial.
5. **Condicional anidado** `ciclos_en_peligro >= MAX_CICLOS_PELIGRO`: si el peligro persiste cinco ciclos consecutivos (≈ 5 minutos), se emite la alerta de emergencia máxima y se asigna `activo = FALSO`, terminando el lazo para forzar intervención humana.
6. La rama `sino` del condicional principal comprueba si el sistema estaba en estado de alerta (`ciclos_en_peligro > 0`). De ser así, restituye todos los actuadores a su estado normal y reinicia el contador; de lo contrario, simplemente confirma que la operación es segura.
