# PlayMaker Pro

**Football Playbook Creator and Analyzer**

Proyecto Final — Programming & Coding | MSMK University College 2025–2026

---

## Descripcion del Proyecto

PlayMaker Pro es una aplicacion de escritorio de linea de comandos (CLI) desarrollada en Python 3.10+. Permite a entrenadores, coordinadores y analistas de futbol americano crear, gestionar, visualizar y analizar playbooks y jugadas de forma profesional.

El proyecto esta inspirado en herramientas como [Cloob Football](https://cloobfootball.com/) y [Tackle Football Playmaker](https://www.tacklefootballplaymaker.com/).

### Contexto del Proyecto

- **Cliente:** Madrid Bulldogs — Equipo de Futbol Americano
- **Consultora:** TechPlay Solutions
- **Lenguaje:** Python 3.10+
- **IDE:** Visual Studio Code
- **Repositorio:** GitHub

---

## Estructura del Proyecto

```
playmaker_pro/
├── cli.py                  # Punto de entrada principal (RF8)
├── models.py               # Clases de dominio: Play, Playbook, Formation
├── exceptions.py           # Excepciones personalizadas del sistema
├── data_importer.py        # Importacion de jugadas desde CSV (RF1)
├── data_manager.py         # CRUD de Playbooks y Jugadas en JSON (RF2)
├── analyzer.py             # Estadisticas, anomalias y prediccion (RF3, RF4, RF7)
├── reporter.py             # Exportacion CSV y graficos ASCII (RF5, RF9)
├── alerts.py               # Motor de alertas automaticas (RF6)
├── simulator.py            # Generador de datos sinteticos (RF10)
├── tests/                  # Suite completa de tests (25 casos)
├── data/                   # Datos de entrada y exportaciones
│   ├── sample_plays.csv    # Dataset de muestra con 20 jugadas
│   └── exports/            # Reportes generados por la aplicacion
├── docs/                   # Documentacion tecnica completa
├── .github/workflows/      # Pipelines de CI/CD con GitHub Actions
├── requirements.txt        # Dependencias del proyecto
└── .gitignore
```

---

## Instalacion

### Requisitos previos

- Python 3.10 o superior
- Git 2.30 o superior
- pip 22.0 o superior

### Pasos de instalacion

**1. Clonar el repositorio**

```bash
git clone https://github.com/danielandresbd-source/AB-FINAL---PROGAMMING-CODING---PLAYMAKER-PRO.git
cd AB-FINAL---PROGAMMING-CODING---PLAYMAKER-PRO
```

**2. Crear el entorno virtual**

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**4. Verificar la instalacion ejecutando los tests**

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

**5. Iniciar la aplicacion**

```bash
python cli.py --help
```

---

## Guia de Uso del CLI

### Ver la ayuda general

```bash
python cli.py --help
```

### Modulo: Playbooks

```bash
# Listar todos los playbooks guardados
python cli.py playbooks listar

# Crear un nuevo playbook
python cli.py playbooks crear --nombre "Red Zone Offense" --tipo spread

# Eliminar un playbook por su ID
python cli.py playbooks eliminar --id pb_abc12345

# Exportar las jugadas de un playbook a CSV
python cli.py playbooks exportar --id pb_abc12345
```

### Modulo: Jugadas

```bash
# Listar jugadas de un playbook
python cli.py jugadas listar --playbook-id pb_abc12345

# Anadir una jugada a un playbook
python cli.py jugadas anadir \
  --playbook pb_abc12345 \
  --nombre "HB Dive Left" \
  --tipo run \
  --formacion I_FORMATION \
  --yardas 4.5 \
  --tasa-exito 0.68 \
  --down 2nd&short

# Importar jugadas desde un CSV
python cli.py jugadas importar \
  --archivo data/sample_plays.csv \
  --playbook pb_abc12345

# Eliminar una jugada
python cli.py jugadas eliminar --playbook pb_abc12345 --id play_xyz98765
```

### Modulo: Analisis

```bash
# Ver estadisticas descriptivas
python cli.py analisis estadisticas --playbook pb_abc12345

# Detectar jugadas anomalas
python cli.py analisis anomalias --playbook pb_abc12345

# Predecir efectividad (requiere 5+ jugadas)
python cli.py analisis prediccion --playbook pb_abc12345 --ventana 5

# Verificar alertas y conflictos
python cli.py analisis alertas --playbook pb_abc12345
```

### Modulo: Reportes

```bash
# Exportar estadisticas a CSV
python cli.py reportes csv --playbook pb_abc12345
```

### Modulo: Simulador

```bash
# Generar 30 jugadas sinteticas mixtas
python cli.py simulador generar --jugadas 30

# Generar solo jugadas de pase
python cli.py simulador generar --jugadas 20 --tipo pass
```

---

## Ejemplo de Sesion Completa

```bash
# 1. Crear un playbook
python cli.py playbooks crear --nombre "Red Zone Offense"

# 2. Importar jugadas de muestra
python cli.py jugadas importar \
  --archivo data/sample_plays.csv \
  --playbook <ID del playbook creado>

# 3. Ver estadisticas con grafico ASCII
python cli.py analisis estadisticas --playbook <ID>

# 4. Buscar jugadas anomalas
python cli.py analisis anomalias --playbook <ID>

# 5. Predecir efectividad
python cli.py analisis prediccion --playbook <ID>

# 6. Exportar estadisticas
python cli.py reportes csv --playbook <ID>
```

---

## Formaciones Disponibles

| Tipo | Formacion |
|---|---|
| Ofensiva | SHOTGUN, I_FORMATION, SINGLEBACK, GUN_TRIPS, EMPTY_SET, PISTOL, WILDCAT |
| Defensiva | FOUR_THREE, THREE_FOUR, NICKEL, DIME |

## Tipos de Jugada

| Codigo | Descripcion |
|---|---|
| `run` | Jugada de corrida |
| `pass` | Jugada de pase |
| `special_teams` | Jugada de equipos especiales |

---

## Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar con reporte de cobertura
pytest tests/ --cov=. --cov-report=term-missing

# Ejecutar solo tests de un modulo
pytest tests/test_analyzer.py -v

# Ejecutar tests de rendimiento
pytest tests/test_performance.py -v
```

La suite incluye **25 casos de test** documentados que cubren:
- Tests unitarios por modulo
- Tests de integracion entre modulos
- Tests de casos limite
- Tests de error controlado
- Tests de rendimiento (10.000 jugadas en menos de 3 segundos)

---

## Problemas Frecuentes

| Error | Causa | Solucion |
|---|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Entorno virtual no activado | Activar venv y ejecutar `pip install -r requirements.txt` |
| `FileNotFoundError: data/playbooks.json` | Primera ejecucion sin datos | Ejecutar `python cli.py playbooks crear --nombre "Mi Playbook"` |
| `ValidationError: invalid formation` | Formacion no reconocida en el CSV | Usar solo las formaciones definidas en el sistema |
| `pytest: no tests ran` | pytest no encuentra los tests | Verificar que los archivos empiezan con `test_` |
| `UnicodeDecodeError al cargar CSV` | CSV no esta en UTF-8 | Guardar el CSV con codificacion UTF-8 |

---

## Tecnologias Utilizadas

| Tecnologia | Version | Uso |
|---|---|---|
| Python | 3.10+ | Lenguaje principal |
| pytest | 7.4.0 | Framework de testing |
| pytest-cov | 4.1.0 | Cobertura de tests |
| pandas | 2.2.2 | Manipulacion de datos |
| numpy | 1.26.4 | Calculos estadisticos |
| flake8 | 7.0.0 | Verificacion PEP 8 |
| GitHub Actions | - | CI/CD automatizado |

---

## Documentacion Adicional

Toda la documentacion tecnica detallada se encuentra en la carpeta `/docs/`:

- `docs/arquitectura.md` — Arquitectura modular del sistema
- `docs/uml.md` — Diagrama UML de clases
- `docs/pseudocodigo.md` — Pseudocodigo de los algoritmos principales
- `docs/plan_testing.md` — Plan completo de testing con los 25 casos
- `docs/manual_usuario.md` — Manual de usuario detallado
- `docs/registro_bugs.md` — Registro de bugs documentados

---

**Proyecto:** AB Final — Programming & Coding
**Universidad:** MSMK University College
**Curso:** 2025–2026
**Docente:** Dario Sanchez Tierno
