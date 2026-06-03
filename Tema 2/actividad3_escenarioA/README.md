# Escenario Operativo A — Prevención de Fuga Térmica y Gestión de Alivio de Carga

**Actividad III · Lenguaje L · ECO-GRID**
Pareja: **Ronniel e Yvanna**

---

## Descripción del escenario

El script monitorea de forma continua e iterativa la temperatura del banco de baterías
principal de la planta ECO-GRID y actúa de inmediato ante un riesgo de fuga térmica.

| Situación | Condición | Acción |
|-----------|-----------|--------|
| Temperatura crítica | `temp > 55 °C` | Activa refrigeración auxiliar, aísla la carga solar, desvía el sector industrial al respaldo comercial |
| Peligro persistente | Temperatura crítica durante ≥ 5 ciclos consecutivos | Emite alerta de emergencia máxima y detiene el monitoreo automático para forzar intervención humana |
| Normalización | Temperatura baja tras un evento crítico | Restituye todos los actuadores al estado operativo normal y reinicia el contador |
| Operación estable | Temperatura en rango seguro sin evento previo | Emite aviso de monitoreo activo y re-evalúa en 60 s |

---

## Archivos del escenario

| Archivo | Descripción |
|---------|-------------|
| `escenario_a.lgrid` | Script completo en Lenguaje L |
| `lenguajeL_escenarioA.md` | Especificación léxica, gramática EBNF y análisis lógico-sintáctico |

La extensión `.lgrid` identifica scripts del Lenguaje L para ECO-GRID.

---

## Estructura del programa

```
init_grid
│
└── mientras activo == VERDADERO ejecutar   ← lazo de monitoreo termico continuo
    │
    ├── [lectura de sensor]
    │     leer_temperatura(banco)
    │
    ├── si_verdadero temp > 55              ← CASO CRITICO: fuga termica
    │     activar_refrigeracion(banco)
    │     conmutar_linea(linea_solar_carga, AISLADO)
    │     conmutar_linea(sector_industrial, AISLADO)
    │     conmutar_linea(sector_industrial_respaldo, CONECTADO)
    │     emitir_alerta("ALERTA TERMICA ...")
    │     │
    │     └── si_verdadero ciclos_en_peligro >= 5   ← peligro persistente
    │               emitir_alerta("EMERGENCIA CRITICA ...")
    │               activo = FALSO          ← termina el lazo automatico
    │           fin_si
    │
    └── sino
          si_verdadero ciclos_en_peligro > 0        ← recuperacion post-alerta
                conmutar_linea(linea_solar_carga, CONECTADO)
                conmutar_linea(sector_industrial, CONECTADO)
                conmutar_linea(sector_industrial_respaldo, AISLADO)
                ciclos_en_peligro = 0
                emitir_alerta("Temperatura normalizada ...")
          sino
                emitir_alerta("Monitoreo activo: temperatura en rango seguro")
          fin_si
    fin_si
    │
    └── esperar(60)
terminar
```

---

## Primitivas del Lenguaje L usadas

### Sensores (lectura)

| Primitiva | Retorna | Significado |
|-----------|---------|-------------|
| `leer_temperatura(banco)` | DECIMAL (°C) | Temperatura actual del sensor de celda del banco de baterías |

### Actuadores (acción)

| Primitiva | Efecto |
|-----------|--------|
| `activar_refrigeracion(banco)` | Enciende el sistema de refrigeración auxiliar |
| `conmutar_linea(sector, ESTADO)` | Conecta o aísla una línea o sector de la red |
| `emitir_alerta(mensaje)` | Notifica al operador del sistema |
| `esperar(segundos)` | Pausa antes de la siguiente evaluación |

---

## Estructuras de control demostradas

- **Secuencia:** cuatro actuadores disparados en orden determinista dentro del bloque crítico.
- **Selección:** `si_verdadero … entonces … sino … fin_si` anidado en dos niveles (alerta crítica y recuperación post-evento).
- **Iteración:** `mientras … ejecutar … fin_mientras` con re-evaluación cada 60 s, terminación controlada vía `activo = FALSO`.
- **Contador de ciclos:** variable `ciclos_en_peligro` que acumula la persistencia del peligro y habilita la escalada a emergencia total.
