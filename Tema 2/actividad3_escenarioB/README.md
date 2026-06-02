# Escenario Operativo B — Balance de Carga y Optimización Energética Autónoma

**Actividad III · Lenguaje L · ECO-GRID**
Pareja: **Ronniel e Yvanna**

---

## Descripción del escenario

El script evalúa de forma continua y autónoma el estado energético de la planta
ECO-GRID y toma decisiones en dos situaciones extremas:

| Situación | Condición | Acción |
|-----------|-----------|--------|
| Excedente vendible | Batería > 90 % **y** generación solar > demanda | Acciona relé de venta e inyecta el excedente a la red pública |
| Emergencia nocturna | Batería < 20 % **y** hora entre 18:00 y 06:00 | Aísla sectores no esenciales; mantiene médico y servidores conectados |
| Estado intermedio | Ninguna de las anteriores | Emite aviso de operación estable y re-evalúa en 60 s |

---

## Archivo del script

| Archivo | Descripción |
|---------|-------------|
| `escenario_b.lgrid` | Script completo en Lenguaje L |

La extensión `.lgrid` identifica scripts del Lenguaje L para ECO-GRID.

---

## Estructura del programa

```
init_grid
│
└── mientras activo == VERDADERO ejecutar   ← lazo de monitoreo continuo
    │
    ├── [lectura de sensores]
    │     estado_carga, flujo_generacion, demanda_actual, hora_actual
    │
    ├── si_verdadero carga > 90 Y generacion > demanda   ← CASO 1
    │     conmutar_linea(rele_venta, CONECTADO)
    │     inyectar_red(excedente)
    │
    └── sino
          si_verdadero carga < 20 Y hora nocturna         ← CASO 2
                conmutar_linea(sector_no_esencial, AISLADO)
                conmutar_linea(sector_medico, CONECTADO)
                conmutar_linea(sector_servidores, CONECTADO)
          sino
                emitir_alerta("Operacion estable...")
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
| `estado_carga(banco)` | ENTERO (%) | Nivel de carga de la batería |
| `flujo_generacion()` | DECIMAL (kW) | Potencia generada por los paneles solares |
| `demanda_actual()` | DECIMAL (kW) | Consumo actual de la planta |
| `hora_actual()` | ENTERO (0–23) | Hora del sistema |

### Actuadores (acción)

| Primitiva | Efecto |
|-----------|--------|
| `conmutar_linea(sector, ESTADO)` | Conecta o aísla un sector de la red |
| `inyectar_red(kW)` | Vende/inyecta excedente a la red pública |
| `emitir_alerta(mensaje)` | Notifica al operador del sistema |
| `esperar(segundos)` | Pausa antes de la siguiente evaluación |

---

## Estructuras de control demostradas

- **Secuencia:** asignaciones y llamadas a actuadores en orden lógico.
- **Selección:** `si_verdadero … entonces … sino … fin_si` (anidado en dos niveles).
- **Iteración:** `mientras … ejecutar … fin_mientras` con re-evaluación cada 60 s.
- **Operadores lógicos:** `Y` (AND) y `O` (OR) combinando condiciones relacionales.
