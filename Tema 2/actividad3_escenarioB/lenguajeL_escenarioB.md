# Lenguaje L — ECO-GRID | Escenario Operativo B

> **** — Balance de Carga y Optimización Energética Autónoma

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
| `leer_temperatura(bateria_id)` | DECIMAL (°C) | Temperatura actual de un banco de baterías |
| `estado_carga(bateria_id)` | ENTERO (%) | Nivel de carga actual de la batería |
| `flujo_generacion()` | DECIMAL (kW) | Potencia generada por los paneles solares |
| `demanda_actual()` | DECIMAL (kW) | Consumo actual de la planta |
| `hora_actual()` | ENTERO (0–23) | Hora del sistema |

### Actuadores — acción sobre dispositivos físicos

| Keyword | Descripción |
|---------|-------------|
| `conmutar_linea(sector_id, estado)` | Conecta (`CONECTADO`) o aísla (`AISLADO`) un sector de la red |
| `inyectar_red(kW)` | Vende/inyecta excedente energético a la red eléctrica pública |
| `emitir_alerta("mensaje")` | Notifica al operador del sistema |

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

Notación EBNF simplificada de las construcciones usadas en el Escenario B:

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

## 3. Programa de Ejemplo — Escenario Operativo B

```
# ============================================================
#  PROGRAMA B  -  ECO-GRID  -  Balance de Carga y Optimizacion Energetica Autonoma
#  Lenguaje L  |  Ronniel e Yvanna
#  Escenario Operativo B: Gestion autonoma de excedentes y proteccion nocturna
# ============================================================

init_grid

    # --- Umbrales de decision ---
    UMBRAL_OPTIMO      = 90         # % carga para considerar excedente vendible
    UMBRAL_CRITICO     = 20         # % carga minimo de seguridad nocturna
    UMBRAL_TEMP_SEGURA = 45         # grados Celsius: maximo seguro para inyeccion a red
    banco              = banco_1    # banco de baterias principal

    activo = VERDADERO

    # --- Lazo de optimizacion energetica autonoma (evaluacion continua) ---
    mientras activo == VERDADERO ejecutar

        carga      = estado_carga(banco);        # % de carga actual de las baterias
        generacion = flujo_generacion();         # kW generados por los paneles solares
        demanda    = demanda_actual();           # kW demandados por la planta
        hora       = hora_actual();              # hora del sistema (0..23)

        # CASO 1: carga optima Y generacion supera la demanda -> vender excedente a la red
        si_verdadero carga > UMBRAL_OPTIMO Y generacion > demanda entonces

            temp = leer_temperatura(banco);      # verificar temperatura antes de inyectar

            si_verdadero temp < UMBRAL_TEMP_SEGURA entonces
                excedente = generacion - demanda;
                conmutar_linea(rele_venta, CONECTADO);
                inyectar_red(excedente);
                emitir_alerta("Excedente energetico: inyectando kW a la red publica");
            sino
                emitir_alerta("Temperatura elevada en bateria: inyeccion suspendida por seguridad");
            fin_si

        sino

            # CASO 2: carga critica EN horario nocturno de alta demanda
            si_verdadero carga < UMBRAL_CRITICO Y (hora >= 18 O hora <= 6) entonces

                # Preservar suministro critico: aislar sectores no esenciales
                conmutar_linea(sector_no_esencial, AISLADO);
                conmutar_linea(sector_medico, CONECTADO);
                conmutar_linea(sector_servidores, CONECTADO);
                emitir_alerta("Carga critica nocturna: aislando sectores no esenciales");

            sino

                # Estado intermedio: operacion estable, sin accion de balance
                emitir_alerta("Operacion estable: sin accion de balance requerida");

            fin_si

        fin_si

        esperar(60);                 # re-evaluar cada 60 segundos

    fin_mientras

terminar
```

### Explicación lógico-sintáctica

1. `init_grid` … `terminar` delimitan el programa (regla raíz de la gramática).
2. El **bucle `mientras … ejecutar … fin_mientras`** modela el carácter autónomo y continuo del balance: re-evalúa cada 60 s.
3. Cada iteración lee cuatro **sensores** (`estado_carga`, `flujo_generacion`, `demanda_actual`, `hora_actual`) y asigna sus valores a variables locales.
4. **Condicional principal** `carga > UMBRAL_OPTIMO Y generacion > demanda`: el operador lógico `Y` combina dos condiciones relacionales. Si se cumple, se verifica la temperatura con `leer_temperatura` antes de inyectar — protección de seguridad adicional.
5. **Condicional anidado** en la rama `sino`: `carga < UMBRAL_CRITICO Y (hora >= 18 O hora <= 6)`. Los paréntesis agrupan la sub-condición horaria, evitando ambigüedad de precedencia. Aquí se aíslan sectores no esenciales y se mantienen conectados el sector médico y de servidores.
6. La rama `sino` interna cubre el estado intermedio: ni venta ni emergencia, el sistema sigue monitoreando.
