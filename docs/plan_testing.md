# Plan de Testing — PlayMaker Pro



---

## Estrategia General

El testing se realiza en paralelo con el desarrollo. Cada funcion implementada tiene su test antes de pasar a la siguiente funcionalidad. El objetivo minimo es un 80% de cobertura con al menos 20 casos de test documentados.

**Este plan incluye 25 casos de test.**

---

## Tipos de Tests

| Tipo | Que verifica | Archivos |

| Unitario | Comportamiento de una sola funcion en aislamiento | `test_data_importer.py`, `test_data_manager.py`, `test_analyzer.py`, `test_reporter.py`, `test_alerts.py`, `test_simulator.py` |
| Integracion | Que los modulos funcionan correctamente en conjunto | `test_integration.py` |
| Rendimiento | Que el sistema cumple NF1 (10K jugadas en menos de 3s) | `test_performance.py` |

---

## Tabla Completa de Casos de Test

| ID | Modulo | Funcion | Tipo | Escenario | Resultado Esperado | Estado |

| T01 | data_importer | `cargar_csv()` | Unitario | CSV valido con 10 jugadas | Lista de 10 objetos Play | Implementado |
| T02 | data_importer | `cargar_csv()` | Limite | CSV con solo cabeceras | Lista vacia `[]` | Implementado |
| T03 | data_importer | `cargar_csv()` | Error | Archivo no encontrado | `FileNotFoundError` capturada | Implementado |
| T04 | data_importer | `validar_fila()` | Error | Fila con yardas no numericas | Fila omitida, no crash | Implementado |
| T05 | data_importer | `sanitizar_datos()` | Limite | CSV con columnas extra | Columnas extras ignoradas | Implementado |
| T06 | data_manager | `crear_playbook()` | Unitario | Parametros validos | Playbook creado y guardado en JSON | Implementado |
| T07 | data_manager | `crear_playbook()` | Error | Nombre vacio | `ValidationError` lanzada | Implementado |
| T08 | data_manager | `actualizar_jugada()` | Unitario | Play existente, nuevos atributos | Play actualizada en JSON | Implementado |
| T09 | data_manager | `eliminar_playbook()` | Limite | ID inexistente | `PlaybookNotFoundError` con mensaje claro | Implementado |
| T10 | data_manager | `obtener_jugada()` | Unitario | ID valido | Objeto Play correcto devuelto | Implementado |
| T11 | analyzer | `calcular_estadisticas()` | Unitario | 10 jugadas con yardas distintas | Media, min, max, top-5 correctos | Implementado |
| T12 | analyzer | `detectar_anomalias()` | Unitario | Dataset con outlier de yardas | Outlier detectado con razon Z-score | Implementado |
| T13 | analyzer | `detectar_anomalias()` | Limite | Lista con 1 sola jugada | Sin anomalias de Z-score | Implementado |
| T14 | analyzer | `predecir_efectividad()` | Unitario | 10 registros validos, ventana=5 | Float en rango [0.0, 1.0] | Implementado |
| T15 | analyzer | `predecir_efectividad()` | Error | Menos registros que ventana | `ValueError` capturada | Implementado |
| T16 | reporter | `exportar_csv()` | Unitario | Lista de plays valida | CSV creado en `data/exports/` | Implementado |
| T17 | reporter | `mostrar_grafico_ascii()` | Unitario | Dict con stats por tipo | String con barras `#` correcto | Implementado |
| T18 | alerts | `evaluar_jugada()` | Unitario | Play con formacion invalida | Alerta disparada en consola | Implementado |
| T19 | alerts | `verificar_playbook()` | Limite | Playbook con 51 jugadas | Alerta de capacidad excedida | Implementado |
| T20 | simulator | `generar_jugadas()` | Unitario | n=100 jugadas sinteticas | Lista de 100 objetos Play validos | Implementado |
| T21 | simulator | `generar_jugadas()` | Limite | n=0 | Lista vacia `[]` | Implementado |
| T22 | Integracion | `cargar_csv → calcular_estadisticas → exportar` | Integracion | Pipeline completo con CSV real | CSV exportado con estadisticas correctas | Implementado |
| T23 | Integracion | `crear_playbook → anadir_jugada → detectar_anomalias` | Integracion | Playbook nuevo con jugada anomala | Anomalia detectada correctamente | Implementado |
| T24 | Integracion | `generar_jugadas → guardar_csv → cargar_csv → predecir` | Integracion | Datos sinteticos → prediccion valida | Prediccion en rango [0.0, 1.0] | Implementado |
| T25 | Rendimiento | `cargar_csv + calcular_estadisticas` | Rendimiento | CSV con 10.000 jugadas | Completado en menos de 3 segundos | Implementado |

---

## Como Ejecutar los Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con cobertura
pytest tests/ --cov=. --cov-report=term-missing

# Ejecutar solo tests unitarios de un modulo
pytest tests/test_analyzer.py -v

# Ejecutar tests de integracion
pytest tests/test_integration.py -v

# Ejecutar tests de rendimiento
pytest tests/test_performance.py -v

# Ejecutar y generar reporte HTML de cobertura
pytest tests/ --cov=. --cov-report=html
```

---

## Herramientas Utilizadas

| Herramienta | Uso | Comando |
|---|---|---|
| `pytest` | Ejecutar la suite de tests | `pytest tests/ -v` |
| `pytest-cov` | Medir cobertura de codigo | `pytest tests/ --cov=. --cov-report=term-missing` |
| `pytest-benchmark` | Tests de rendimiento | Se usa en `test_performance.py` |
| `flake8` | Verificar PEP 8 | `flake8 . --max-line-length=99` |
| `pylint` | Analisis estatico | `pylint *.py --disable=C0114` |

---

## Requisitos de Calidad

| Requisito | Meta | Como se verifica |
|---|---|---|
| Cobertura minima | 80% por modulo | `pytest --cov=. --cov-fail-under=80` |
| Numero de tests | Minimo 20  | Contar en la tabla |
| Todos los tests pasan | 0 tests fallidos | `pytest tests/ -v` |
| Rendimiento NF1 | 10K jugadas en menos de 3s | T25 en `test_performance.py` |
| PEP 8 | Sin errores de estilo | `flake8 .` |
