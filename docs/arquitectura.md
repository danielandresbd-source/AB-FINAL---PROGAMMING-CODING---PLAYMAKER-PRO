# Arquitectura del Sistema — PlayMaker Pro

**Proyecto:** AB Final — Programming & Coding 

---

## Vision General

El proyecto sigue una arquitectura modular en capas. Cada modulo tiene una responsabilidad unica y bien definida.

---

## Diagrama de Capas

```
 ----------------------------------------------------------
|                     CAPA DE PRESENTACION                 |
|                          cli.py                          |
|          (Interfaz de linea de comandos con argparse)    |
 ----------------------------------------------------------
          |              |              |
          v              v              v
 ----------------   ----------   -------------
|  data_manager  | | analyzer | |  reporter   |
|   (RF2: CRUD)  | | (RF3/4/7)| | (RF5/RF9)   |
 ----------------   ----------   -------------
          |              |              |
          v              v              v
 ----------------------------------------------------------
|                    CAPA DE DATOS Y MODELOS               |
|   models.py (Play, Playbook, Formation, PlayType)        |
|   exceptions.py (PlayMakerError, ValidationError, ...)   |
 ----------------------------------------------------------
          |
          v
 ----------------------------------------------------------
|                   CAPA DE ENTRADA / SALIDA               |
|   data_importer.py (RF1)  |  simulator.py (RF10)         |
|   alerts.py (RF6)                                        |
 ----------------------------------------------------------
          |
          v
 ----------------------------------------------------------
|                     ALMACENAMIENTO                       |
|   data/playbooks.json      |   data/exports/*.csv        |
|   data/sample_plays.csv    |                             |
 ----------------------------------------------------------
```



## Módulos

### `models.py` — Modelos de Dominio

En este múdlo se contiene las clases de datos del dominio de futbol americano.

**Clases:**
- `Formation` (Enum): Formaciones validas del sistema (SHOTGUN, I_FORMATION, etc.)
- `PlayType` (Enum): Tipos de jugada (run, pass, special_teams)
- `Play`: Representa una jugada individual
- `Playbook`: Representa un libro de jugadas que agrupa varios `Play`

**Patron del diseño utilizado:** Value Object + Factory Method (`desde_diccionario`)

---

### `exceptions.py` — Excepciones Personalizadas

Este módulo define la jerarquia de excepciones del sistema.

```
PlayMakerError (base)
├── ValidationError
├── PlaybookNotFoundError
├── PlayNotFoundError
├── PlaybookFullError
└── ArchivoCsvError
```

---

### `data_importer.py` — Importacion de CSV (RF1)

Este módulo será el responsable de leer un archivo CSV y convertirlo en objetos `Play`.

**Flujo de trabajo:**
1. Verificar que el archivo existe
2. Verificar que tiene las columnas requeridas
3. Procesar cada fila y validarla
4. Devolver la lista de jugadas validas

**Funciones publicas:**
- `cargar_csv(ruta)` → `list[Play]`
- `sanitizar_datos(jugadas)` → `list[Play]`

---

### `data_manager.py` — CRUD con JSON (RF2)

Este módulo será responsable de persistir y recuperar datos en `data/playbooks.json`.

**Funciones publicas:**
- `crear_playbook(nombre, tipo_ofensa)` → `Playbook`
- `listar_playbooks()` → `list[Playbook]`
- `obtener_playbook(id)` → `Playbook`
- `actualizar_playbook(id, ...)` → `Playbook`
- `eliminar_playbook(id)` → `None`
- `anadir_jugada(playbook_id, jugada)` → `Play`
- `actualizar_jugada(playbook_id, play_id, datos)` → `Play`
- `eliminar_jugada(playbook_id, play_id)` → `None`
- `obtener_jugada(playbook_id, play_id)` → `Play`

---

### `analyzer.py` — Analisis (RF3, RF4, RF7)

Este módulo será el responsable de calcular metricas, detectar anomalias y predecir tendencias.

**Funciones publicas:**
- `calcular_estadisticas(jugadas)` → `dict` (RF3)
- `detectar_anomalias(jugadas)` → `list[dict]` (RF4)
- `predecir_efectividad(jugadas, ventana)` → `dict` (RF7)
- `obtener_resumen_tendencias(jugadas)` → `dict`

Todas las funciones son puras (no tienen efectos secundarios), lo que facilita el testing.

---

### `reporter.py` — Reportes (RF5, RF9)

Este módulo sera el responsable de exportar datos a archivos y generar visualizaciones ASCII.

**Funciones publicas:**
- `exportar_csv(jugadas, nombre_archivo)` → `str` (ruta del archivo) (RF5)
- `exportar_estadisticas_csv(estadisticas)` → `str` (RF5)
- `mostrar_grafico_ascii(estadisticas)` → `str` (RF9)
- `mostrar_top_jugadas(estadisticas)` → `None`

---

### `alerts.py` — Motor de Alertas (RF6)

Este módulo será el responsable de evaluar jugadas y playbooks en busca de conflictos.

**Clase principal:** `MotorAlertas`

**Metodos publicos:**
- `evaluar_jugada(jugada)` → `list[str]`
- `verificar_playbook(playbook)` → `list[str]`
- `obtener_alertas()` → `list[str]`
- `limpiar_registro()` → `None`

**Reglas internas:**
- `_regla_formacion_invalida`
- `_regla_tipo_invalido`
- `_regla_yardas_extremas`
- `_regla_tasa_exito_invalida`
- `_regla_down_distance_invalido`

---

### `simulator.py` — Simulador (RF10)

Este módulo será el responsable de generar datos sinteticos para testing y demostraciones.

**Funciones publicas:**
- `generar_jugadas(cantidad, tipo_ofensa)` → `list[Play]`
- `generar_playbooks(num_playbooks, jugadas_por_playbook)` → `list[Playbook]`
- `guardar_dataset_json(playbooks, ruta)` → `str`
- `guardar_dataset_csv(jugadas, ruta)` → `str`

---

### `cli.py` — Interfaz de Linea de Comandos (RF8)

Este módulo será el responsable de recibir los comandos del usuario y enrutarlos al modulo correcto.

**Estructura:**
- Un parser principal con 5 subparsers (playbooks, jugadas, analisis, reportes, simulador)
- Una tabla de comandos `dict[(modulo, accion)] → funcion`
- Funciones `cmd_*` que coordinan los modulos y muestran resultados

---

## Patron de Persistencia

El sistema usa un archivo JSON como base de datos simple.

**Ruta:** `data/playbooks.json`

**Estructura:**
```json
{
  "playbooks": [
    {
      "id": "pb_abc12345",
      "nombre": "Red Zone Offense",
      "tipo_ofensa": "spread",
      "creado_en": "2025-05-08T16:00:00",
      "actualizado_en": "2025-05-08T16:00:00",
      "jugadas": [
        {
          "id": "play_xyz98765",
          "nombre": "HB Dive Left",
          "tipo": "run",
          "formacion": "I_FORMATION",
          "yardas": 4.5,
          "tasa_exito": 0.68,
          "down_distance": "2nd&short",
          "hash_position": "middle",
          "etiquetas": ["short_yardage", "power_run"],
          "creada_en": "2025-05-08T16:00:00"
        }
      ]
    }
  ]
}
```

---

## Flujo de Datos en el Sistema

```
Usuario escribe comando en terminal
        |
        v
    cli.py (argparse)
        |
        v
Funcion cmd_* correspondiente
        |
      ----------------------------------------
      |                    |                  |
      v                    v                  v
data_manager.py       analyzer.py        reporter.py
(CRUD / JSON)     (estadisticas/IA)    (CSV / ASCII)
      |
      v
  models.py
(Play, Playbook)
      |
      v
data/playbooks.json
```

---

## Convencion de Commits

```
feat:      Nueva funcionalidad
fix:       Correccion de bug
test:      Añadir o modificar tests
docs:      Cambios en documentacion
refactor:  Mejora de codigo sin cambiar funcionalidad
chore:     Tareas de mantenimiento
perf:      Mejora de rendimiento
```



---

## Estrategia de Branches

| Branch | Proposito |
|---|---|
| `main` | Codigo estable, listo para produccion |
| `develop` | Integracion de features en desarrollo |
| `feature/rf1-importacion-csv` | Desarrollo de RF1 |
| `feature/rf2-crud-playbooks` | Desarrollo de RF2 |
| `feature/rf3-rf4-rf7-analyzer` | Desarrollo de RF3, RF4, RF7 |
| `feature/rf5-rf9-reporter` | Desarrollo de RF5, RF9 |
| `feature/rf6-alertas` | Desarrollo de RF6 |
| `feature/rf8-cli` | Desarrollo de RF8 |
| `feature/rf10-simulador` | Desarrollo de RF10 |
| `fix/<descripcion>` | Correcciones de bugs |
| `docs/<descripcion>` | Actualizaciones de documentacion |
