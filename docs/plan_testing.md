# Plan de Testing — PlayMaker Pro

> **Version 2.0** — Actualizado tras revision de pares y feedbacks del profesor.
> Tests totales: **147** | Cobertura total: **84.21%** | Estado CI/CD: ✅ Verde

---

## Historial de Cambios

| Version | Cambio |
|---|---|
| v1.0 | Plan inicial con 25 casos de test (T01-T25) |
| v2.0 | +41 tests para `cli_commands/` (antes excluidos de cobertura) |
| v2.0 | +14 tests para `cli.py` (antes en 0% de cobertura) |
| v2.0 | Fix real de W291 (trailing whitespace) en 5 archivos de test |
| v2.0 | Eliminado `--extend-ignore=W291` del CI |
| v2.0 | Eliminado `cli.py` y `cli_commands/*` del `omit` de cobertura |
| v2.0 | Aclaracion de NF4: el limite de 50 lineas aplica por funcion, no por modulo |


## Estrategia General

El testing se realiza en paralelo con el desarrollo. Cada funcion implementada tiene
su test antes de pasar a la siguiente funcionalidad. Se sigue el mismo patron de
aislamiento en todos los archivos de test: cada test usa un directorio temporal
(`tmp_path` de pytest) y redirige `data_manager.RUTA_JSON` a un archivo JSON temporal,
para que los tests no toquen jamas los datos reales del proyecto.

---

## Tipos de Tests

| Tipo | Que verifica | Archivos |
|---|---|---|
| Unitario | Comportamiento de una sola funcion en aislamiento | `test_data_importer.py`, `test_data_manager.py`, `test_analyzer.py`, `test_reporter.py`, `test_alerts.py`, `test_simulator.py`, `test_cobertura_adicional.py` |
| CLI | Parser de argparse y enrutamiento de comandos en `cli.py` | `test_cli.py` |
| CLI Commands | Logica de presentacion de cada submodulo de `cli_commands/` | `test_cli_commands.py` |
| Integracion | Que los modulos funcionan correctamente en conjunto | `test_integration.py` |
| Rendimiento | Que el sistema cumple NF1 (10K jugadas en menos de 3s) | `test_performance.py` |

---

## Tabla de Casos de Test — Modulos Core (T01-T25)

| ID | Modulo | Funcion | Tipo | Escenario | Resultado Esperado | Estado |
|---|---|---|---|---|---|---|
| T01 | data_importer | `cargar_csv()` | Unitario | CSV valido con 10 jugadas | Lista de 10 objetos Play | ✅ |
| T02 | data_importer | `cargar_csv()` | Limite | CSV con solo cabeceras | Lista vacia `[]` | ✅ |
| T03 | data_importer | `cargar_csv()` | Error | Archivo no encontrado | `FileNotFoundError` capturada | ✅ |
| T04 | data_importer | `validar_fila()` | Error | Fila con yardas no numericas | Fila omitida, no crash | ✅ |
| T05 | data_importer | `sanitizar_datos()` | Limite | CSV con columnas extra | Columnas extras ignoradas | ✅ |
| T06 | data_manager | `crear_playbook()` | Unitario | Parametros validos | Playbook creado y guardado en JSON | ✅ |
| T07 | data_manager | `crear_playbook()` | Error | Nombre vacio | `ValidationError` lanzada | ✅ |
| T08 | data_manager | `actualizar_jugada()` | Unitario | Play existente, nuevos atributos | Play actualizada en JSON | ✅ |
| T09 | data_manager | `eliminar_playbook()` | Limite | ID inexistente | `PlaybookNotFoundError` con mensaje claro | ✅ |
| T10 | data_manager | `obtener_jugada()` | Unitario | ID valido | Objeto Play correcto devuelto | ✅ |
| T11 | analyzer | `calcular_estadisticas()` | Unitario | 10 jugadas con yardas distintas | Media, min, max, top-5 correctos | ✅ |
| T12 | analyzer | `detectar_anomalias()` | Unitario | Dataset con outlier de yardas | Outlier detectado con razon Z-score | ✅ |
| T13 | analyzer | `detectar_anomalias()` | Limite | Lista con 1 sola jugada | Sin anomalias de Z-score | ✅ |
| T14 | analyzer | `predecir_efectividad()` | Unitario | 10 registros validos, ventana=5 | Float en rango [0.0, 1.0] | ✅ |
| T15 | analyzer | `predecir_efectividad()` | Error | Menos registros que ventana | `ValueError` capturada | ✅ |
| T16 | reporter | `exportar_csv()` | Unitario | Lista de plays valida | CSV creado en `data/exports/` | ✅ |
| T17 | reporter | `mostrar_grafico_ascii()` | Unitario | Dict con stats por tipo | String con barras `#` correcto | ✅ |
| T18 | alerts | `evaluar_jugada()` | Unitario | Play con formacion invalida | Alerta disparada en consola | ✅ |
| T19 | alerts | `verificar_playbook()` | Limite | Playbook con 51 jugadas | Alerta de capacidad excedida | ✅ |
| T20 | simulator | `generar_jugadas()` | Unitario | n=100 jugadas sinteticas | Lista de 100 objetos Play validos | ✅ |
| T21 | simulator | `generar_jugadas()` | Limite | n=0 | Lista vacia `[]` | ✅ |
| T22 | Integracion | Pipeline carga → analiza → exporta | Integracion | Pipeline completo con CSV real | CSV exportado con estadisticas correctas | ✅ |
| T23 | Integracion | Pipeline playbook → jugada → anomalia | Integracion | Playbook nuevo con jugada anomala | Anomalia detectada correctamente | ✅ |
| T24 | Integracion | Pipeline simula → carga → predice | Integracion | Datos sinteticos → prediccion valida | Prediccion en rango [0.0, 1.0] | ✅ |
| T25 | Rendimiento | `cargar_csv + calcular_estadisticas` | Rendimiento | CSV con 10.000 jugadas | Completado en menos de 3 segundos | ✅ |

---

## Tabla de Casos de Test — CLI Commands (v2.0)

Estos 41 tests cubren los 6 modulos de `cli_commands/` que antes estaban excluidos
de la cobertura sin ningun test asociado. Se anadieron en la rama `test/cli-commands-coverage`.

### common.py (4 tests)

| Test | Escenario | Resultado Esperado |
|---|---|---|
| `test_imprimir_separador_muestra_linea_de_55_caracteres` | Llamar a `imprimir_separador()` | Salida contiene 55 caracteres `=` |
| `test_imprimir_titulo_muestra_nombre_de_la_app` | Llamar a `imprimir_titulo()` | Salida contiene "PLAYMAKER PRO" y "Madrid Bulldogs" |
| `test_imprimir_error_incluye_etiqueta_error` | Llamar a `imprimir_error("mensaje")` | Salida contiene `[ERROR]` y el mensaje |
| `test_imprimir_exito_incluye_etiqueta_ok` | Llamar a `imprimir_exito("mensaje")` | Salida contiene `[OK]` y el mensaje |

### playbooks.py (8 tests)

| Test | Escenario | Resultado Esperado |
|---|---|---|
| `test_listar_sin_playbooks_muestra_mensaje_vacio` | Sin playbooks guardados | Mensaje "No hay playbooks guardados todavia" |
| `test_listar_con_playbooks_muestra_sus_datos` | 1 playbook existente | Muestra nombre y tipo de ofensa |
| `test_crear_con_nombre_valido_lo_guarda` | Nombre valido, tipo "power" | `[OK]` y playbook guardado en JSON |
| `test_crear_sin_tipo_usa_spread_por_defecto` | Sin `--tipo` | `tipo_ofensa == "spread"` |
| `test_crear_con_nombre_vacio_muestra_error` | Nombre vacio `""` | `[ERROR]` y 0 playbooks guardados |
| `test_eliminar_id_existente_lo_borra` | ID valido existente | `[OK]` y lista vacia |
| `test_eliminar_id_inexistente_muestra_error` | ID que no existe | `[ERROR]` |
| `test_exportar_playbook_sin_jugadas_muestra_error` | Playbook vacio | `[ERROR]` con "no tiene jugadas" |
| `test_exportar_playbook_con_jugadas_genera_archivo` | Playbook con 1 jugada | `[OK]` con confirmacion de exportacion |
| `test_exportar_playbook_inexistente_muestra_error` | ID fantasma | `[ERROR]` |

### jugadas.py (9 tests)

| Test | Escenario | Resultado Esperado |
|---|---|---|
| `test_listar_playbook_inexistente_muestra_error` | ID invalido | `[ERROR]` |
| `test_listar_playbook_sin_jugadas_muestra_aviso` | Playbook sin jugadas | "no tiene jugadas todavia" |
| `test_listar_playbook_con_jugadas_las_muestra` | Playbook con 1 jugada | Nombre de la jugada en la salida |
| `test_anadir_jugada_valida_la_guarda` | Todos los args validos | `[OK]` y jugada en JSON |
| `test_anadir_jugada_a_playbook_inexistente_muestra_error` | ID de playbook falso | `[ERROR]` |
| `test_anadir_jugada_con_tipo_invalido_muestra_error` | `tipo="kickflip"` | `[ERROR]` |
| `test_eliminar_jugada_existente_la_borra` | ID valido existente | `[OK]` y 0 jugadas |
| `test_eliminar_jugada_inexistente_muestra_error` | ID de jugada falso | `[ERROR]` |
| `test_importar_csv_valido_anade_jugadas` | CSV con 2 jugadas | `[OK]` y 2 jugadas en JSON |
| `test_importar_archivo_inexistente_muestra_error` | Ruta invalida | `[ERROR]` |
| `test_importar_a_playbook_inexistente_muestra_error` | Playbook falso | `[ERROR]` |

### analisis.py (9 tests)

| Test | Escenario | Resultado Esperado |
|---|---|---|
| `test_estadisticas_playbook_inexistente_muestra_error` | ID fantasma | `[ERROR]` |
| `test_estadisticas_playbook_sin_jugadas_muestra_error` | Playbook vacio | `[ERROR]` con "no tiene jugadas" |
| `test_estadisticas_con_jugadas_muestra_resumen` | 3 jugadas validas | "ESTADISTICAS" y "Total de jugadas: 3" |
| `test_anomalias_sin_jugadas_muestra_error` | Playbook vacio | `[ERROR]` |
| `test_anomalias_sin_anomalias_muestra_mensaje_correcto` | 3 jugadas normales | "No se encontraron anomalias" |
| `test_anomalias_con_nombre_duplicado_las_detecta` | 2 jugadas con mismo nombre | "Se encontraron" anomalias |
| `test_prediccion_con_pocos_registros_muestra_error` | Solo 1 jugada | `[ERROR]` |
| `test_prediccion_con_registros_suficientes_muestra_resultado` | 6 jugadas | "PREDICCION" y "Tendencia actual" |
| `test_alertas_playbook_sin_problemas_muestra_mensaje_ok` | Jugada valida | "VERIFICACION DE ALERTAS" |
| `test_alertas_playbook_inexistente_muestra_error` | ID fantasma | `[ERROR]` |

### reportes.py (3 tests)

| Test | Escenario | Resultado Esperado |
|---|---|---|
| `test_csv_sin_jugadas_muestra_error` | Playbook vacio | `[ERROR]` |
| `test_csv_con_jugadas_genera_archivo` | Playbook con 1 jugada | `[OK]` con ruta del archivo |
| `test_csv_playbook_inexistente_muestra_error` | ID fantasma | `[ERROR]` |

### simulador.py (3 tests)

| Test | Escenario | Resultado Esperado |
|---|---|---|
| `test_generar_con_cantidad_por_defecto_crea_20_jugadas` | Sin `--jugadas` | "Jugadas generadas: 20" |
| `test_generar_con_cantidad_especifica_la_respeta` | `--jugadas 7` | "Jugadas generadas: 7" |
| `test_generar_con_tipo_especifico_no_lanza_error` | `--tipo run` | Sin `[ERROR]` en salida |

---

## Tabla de Casos de Test — CLI Entry Point (v2.0)

Estos 14 tests cubren `cli.py` que estaba en 0% de cobertura.
Se anadieron en la rama `test/cli-entrypoint`.

### construir_parser() (8 tests)

| Test | Escenario | Resultado Esperado |
|---|---|---|
| `test_parser_playbooks_listar` | `playbooks listar` | `modulo="playbooks"`, `accion="listar"` |
| `test_parser_playbooks_crear_con_argumentos` | `playbooks crear --nombre X --tipo Y` | Atributos correctos en `args` |
| `test_parser_jugadas_listar_usa_dest_playbook_id` | `jugadas listar --playbook-id Z` | `args.playbook_id == "Z"` |
| `test_parser_jugadas_anadir_argumentos_completos` | Todos los args de `jugadas anadir` | Todos los atributos correctos incluyendo `tasa_exito` |
| `test_parser_jugadas_anadir_tipo_invalido_falla` | `--tipo kickflip` | `SystemExit` por choices de argparse |
| `test_parser_analisis_prediccion_ventana_por_defecto` | Sin `--ventana` | `args.ventana == "5"` |
| `test_parser_simulador_generar_valores_por_defecto` | Sin argumentos | `args.jugadas == "20"`, `args.tipo is None` |
| `test_parser_sin_argumentos_no_falla` | Sin modulo ni accion | `args.modulo is None` |

### main() (6 tests)

| Test | Escenario | Resultado Esperado |
|---|---|---|
| `test_main_sin_argumentos_muestra_ayuda_y_ejemplos` | `sys.argv = ["cli.py"]` | "PLAYMAKER PRO" y "Ejemplos rapidos" |
| `test_main_modulo_sin_accion_redirige_a_ayuda_del_modulo` | `sys.argv = ["cli.py", "playbooks"]` | `SystemExit(0)` con ayuda del modulo |
| `test_main_playbooks_crear_persiste_el_playbook` | `playbooks crear --nombre X` | `[OK]` y playbook en JSON |
| `test_main_playbooks_listar_sin_datos_muestra_aviso` | `playbooks listar` sin datos | "No hay playbooks guardados todavia" |
| `test_main_simulador_generar_ejecuta_correctamente` | `simulador generar --jugadas 5` | "Jugadas generadas: 5" |
| `test_main_comando_no_mapeado_en_tabla_muestra_error` | Entrada eliminada de `TABLA_COMANDOS` | "Comando no reconocido" |

---

## Cobertura por Modulo (v2.0)

| Modulo | Lineas | Sin cubrir | Cobertura |
|---|---|---|---|
| `analyzer.py` | 85 | 1 | 99% |
| `data_manager.py` | 140 | 0 | 100% |
| `exceptions.py` | 12 | 0 | 100% |
| `reporter.py` | 117 | 4 | 97% |
| `simulator.py` | 99 | 4 | 96% |
| `cli_commands/common.py` | 13 | 0 | 100% |
| `alerts.py` | 80 | 7 | 91% |
| `models.py` | 107 | 10 | 91% |
| `cli_commands/analisis.py` | 87 | 12 | 86% |
| `cli_commands/playbooks.py` | 52 | 9 | 83% |
| `data_importer.py` | 82 | 9 | 89% |
| `cli_commands/reportes.py` | 18 | 2 | 89% |
| `cli_commands/simulador.py` | 16 | 2 | 88% |
| `cli_commands/jugadas.py` | 66 | 13 | 80% |
| `cli.py` | 96 | 18 | 81% |
| `cli_commands/__init__.py` | 0 | 0 | 100% |
| **TOTAL** | **1070** | **169** | **84.21%** |

---

## Fix W291 — Trailing Whitespace (v2.0)

Durante la revision de pares se detecto que 5 archivos de test tenian
espacios en blanco sobrantes al final de una linea de comentario (error W291
de flake8). El `ci.yml` original tenia `--extend-ignore=W291` para ignorar
este error, lo cual ocultaba el problema en vez de resolverlo.

**Archivos corregidos:**
- `tests/test_alerts.py`
- `tests/test_analyzer.py`
- `tests/test_data_importer.py`
- `tests/test_integration.py`
- `tests/test_performance.py`

**Cambio en `ci.yml`:** eliminado `W291` de `--extend-ignore`. El CI ahora
detecta y rechaza este error de verdad, no lo ignora silenciosamente.

---

## Como Ejecutar los Tests

```bash
# Ejecutar todos los tests (147 en total)
pytest tests/ -v

# Ejecutar con cobertura completa
pytest tests/ --cov=. --cov-report=term-missing

# Ejecutar solo los tests de CLI
pytest tests/test_cli.py tests/test_cli_commands.py -v

# Ejecutar solo tests unitarios de un modulo
pytest tests/test_analyzer.py -v

# Ejecutar tests de integracion
pytest tests/test_integration.py -v

# Ejecutar tests de rendimiento
pytest tests/test_performance.py -v

# Verificar estilo PEP 8 (sin errores deberia imprimir nada)
flake8 . --max-line-length=99 --extend-ignore=E402
```

---

## Herramientas Utilizadas

| Herramienta | Uso | Comando |
|---|---|---|
| `pytest` | Ejecutar la suite de tests | `pytest tests/ -v` |
| `pytest-cov` | Medir cobertura de codigo | `pytest tests/ --cov=. --cov-report=term-missing` |
| `pytest-benchmark` | Tests de rendimiento | Se usa en `test_performance.py` |
| `flake8` | Verificar PEP 8 | `flake8 . --max-line-length=99 --extend-ignore=E402` |

---

## Requisitos de Calidad

| Requisito | Meta | Valor actual | Estado |
|---|---|---|---|
| Cobertura minima | 80% | 84.21% | ✅ |
| Numero de tests | Minimo 20 | 147 | ✅ |
| Todos los tests pasan | 0 fallidos | 0 fallidos | ✅ |
| Rendimiento NF1 | 10K jugadas en menos de 3s | ~1s | ✅ |
| PEP 8 | 0 errores W291 | 0 errores | ✅ |
| CI/CD | Badge verde | Verde | ✅ |