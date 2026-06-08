# Diagrama UML de Clases — PlayMaker Pro

**Proyecto:** AB Final — Programming & Coding | MSMK University College 2025–2026

---

## Diagrama de Clases

```
 -----------------------------          ----------------------------------
|           Play              |        |           Playbook               |
 -----------------------------   1      ----------------------------------
| - id: str                   |<-------| - id: str                        |
| - nombre: str               |        | - nombre: str                    |
| - tipo: PlayType (enum)     |        | - tipo_ofensa: str               |
| - formacion: Formation(enum)|        | - jugadas: list[Play]            |
| - descripcion: str          |        | - creado_en: str (ISO datetime)  |
| - yardas: float             |        | - actualizado_en: str            |
| - tasa_exito: float         |         ----------------------------------
| - down_distance: str        |        | + anadir_jugada(jugada): None    |
| - hash_position: str        |        | + eliminar_jugada(id): None      |
| - etiquetas: list[str]      |        | + obtener_jugada(id): Play       |
| - creada_en: str            |        | + a_diccionario(): dict          |
 -----------------------------         | + desde_diccionario(d): Playbook |
| + validar(): bool           |         ----------------------------------
| + es_anomala(): bool        |
| + a_diccionario(): dict     |
| + desde_diccionario(): Play |
 -----------------------------
              |
              | usa
              v
 -----------------------------
|      Formation (Enum)       |
 -----------------------------
| SHOTGUN                     |
| I_FORMATION                 |
| SINGLEBACK                  |
| GUN_TRIPS                   |
| EMPTY_SET                   |
| PISTOL                      |
| WILDCAT                     |
| FOUR_THREE                  |
| THREE_FOUR                  |
| NICKEL                      |
| DIME                        |
 -----------------------------

 -----------------------------
|       PlayType (Enum)       |
 -----------------------------
| CORRIDA = "run"             |
| PASE = "pass"               |
| ESPECIALES = "special_teams"|
 -----------------------------


 ----------------------------------        ----------------------------------
|         TrendAnalyzer            |      |          AlertEngine             |
|       (en analyzer.py)           |      |        (en alerts.py)            |
 ----------------------------------        ----------------------------------
| Funciones:                       |      | - _registro_alertas: list[str]   |
| + calcular_estadisticas()        |      | - _reglas_jugada: list[Callable] |
| + detectar_anomalias()           |       ----------------------------------
| + predecir_efectividad()         |      | + evaluar_jugada(jugada)         |
| + obtener_resumen_tendencias()   |      | + verificar_playbook(playbook)   |
 ----------------------------------       | + obtener_alertas()              |
                                          | + limpiar_registro()             |
                                           ----------------------------------


 ----------------------------------        ----------------------------------
|       DataImporter               |      |         Reporter                 |
|     (en data_importer.py)        |      |       (en reporter.py)           |
 ----------------------------------        ----------------------------------
| Funciones:                       |      | Funciones:                       |
| + cargar_csv(ruta)               |      | + exportar_csv(jugadas)          |
| + sanitizar_datos(jugadas)       |      | + exportar_estadisticas_csv()    |
 ----------------------------------       | + mostrar_grafico_ascii()        |
                                          | + mostrar_top_jugadas()          |
                                           ----------------------------------


 ----------------------------------
|          Simulator               |
|        (en simulator.py)         |
 ---------------------------------- 
| Funciones:                       |
| + generar_jugadas(cantidad)      |
| + generar_playbooks(num, cant)   |
| + guardar_dataset_json()         |
| + guardar_dataset_csv()          |
 ----------------------------------
```

---

## Relaciones Entre Clases

| Relacion | Descripcion |
|---|---|
| `Playbook` contiene `Play` (1) | Un playbook tiene una o mas jugadas |
| `Play` usa `Formation` (enum) | Cada jugada referencia una formacion valida |
| `Play` usa `PlayType` (enum) | Cada jugada tiene un tipo definido por el enum |
| `MotorAlertas` evalua `Play` y `Playbook` | El motor de alertas recibe objetos del dominio |
| `DataManager` persiste `Playbook` | El gestor de datos serializa y deserializa playbooks |

---

## Jerarquia de Excepciones

```
Exception (Python base)
└── PlayMakerError
    ├── ValidationError
    │     (datos invalidos del usuario)
    ├── PlaybookNotFoundError
    │     (playbook no encontrado por ID)
    ├── PlayNotFoundError
    │     (jugada no encontrada en playbook)
    ├── PlaybookFullError
    │     (limite de 50 jugadas alcanzado)
    └── ArchivoCsvError
          (problema con el archivo CSV de importacion)
```

---

## Ciclo de Vida de un Objeto Play

```
1. Creacion
   Play(nombre, tipo, formacion, yardas, ...)
          |
          v
2. Validacion
   jugada.validar()  <-- lanza ValidationError si hay problemas
          |
          v
3. Persistencia
   data_manager.anadir_jugada(playbook_id, jugada)
          |
          v
4. Analisis
   analyzer.calcular_estadisticas([jugada, ...])
   analyzer.detectar_anomalias([jugada, ...])
          |
          v
5. Exportacion
   reporter.exportar_csv([jugada, ...])
```

---

## Patron de Serializacion

Cada clase del dominio implementa dos metodos:

```python
# Convertir objeto a diccionario (para guardar en JSON)
jugada.a_diccionario() -> dict

# Crear objeto desde diccionario (para leer del JSON)
Play.desde_diccionario(datos_dict) -> Play
```

Este patron permite serializar y deserializar objetos sin depender de librerias externas.
