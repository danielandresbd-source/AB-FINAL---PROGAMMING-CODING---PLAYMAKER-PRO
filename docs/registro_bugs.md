# Registro de Bugs — PlayMaker Pro

---

## Bug 001 — Deteccion de anomalias falla con un solo registro

**Fecha del bug:** Durante la implementacion de analyzer.py

**Descripcion del bug:**
Al llamar a `detectar_anomalias()` con una lista que contenia solo una jugada, el programa lanzaba un error de division por cero al intentar calcular la desviacion estandar.

**Pasos para reproducir:**
```python
from models import Play
from analyzer import detectar_anomalias

jugada = Play(nombre="Test", tipo="run", formacion="SHOTGUN", yardas=5.0)
detectar_anomalias([jugada])
# ZeroDivisionError: float division by zero
```

**Causa raiz:**
La formula de la varianza divida entre `len(lista_yardas)` que es 1, lo cual en si no es division por cero. Pero al calcular la desviacion estandar con `math.sqrt(varianza)`, la varianza era 0.0 (un solo valor no tiene dispersion). Luego al calcular el Z-score se dividia entre la desviacion estandar que era 0.0, causando `ZeroDivisionError`.

**Solucion aplicada:**
Se agregó una condicion para verificar que la desviacion estandar es mayor que cero antes de calcular el Z-score:

```python
# Antes (codigo con bug):
z_score = (jugada.yardas - media_yardas) / desviacion_estandar

# Despues (codigo corregido):
if desviacion_estandar > 0:
    z_score = (jugada.yardas - media_yardas) / desviacion_estandar
    if abs(z_score) > 2.5:
        razones_anomalia.append(...)
```



---

## Bug 002 — JSON corrupto bloqueaba toda la aplicacion

**Fecha de bug:** Durante las pruebas de casos limite

**Descripcion del bug:**
Si el archivo `data/playbooks.json` contenia texto invalido o estaba corrupto (por ejemplo, si el usuario lo editaba manualmente y cometia un error), la aplicacion se bloqueaba completamente al arrancar y mostraba un traceback largo que el usuario no entendia.

**Pasos para reproducir:**
```bash
# Corromper el archivo JSON manualmente
echo "esto no es json valido {{{" > data/playbooks.json

# Ejecutar cualquier comando
python cli.py playbooks listar
# json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes...
# (traceback largo de Python que confunde al usuario)
```

**Causa raiz:**
La funcion `_cargar_datos_json()` en `data_manager.py` no tenia manejo de excepciones para cuando `json.load()` falla. El error propagaba hasta el usuario sin una explicacion clara.

**Solucion aplicada:**
Se agrego un bloque `try/except` especifico para `json.JSONDecodeError` que, en lugar de mostrar el traceback, registra el error en el log e inicializa el sistema con datos vacios:

```python
# Antes (codigo con bug):
with open(RUTA_JSON) as archivo:
    datos = json.load(archivo)

# Despues (codigo corregido):
try:
    with open(RUTA_JSON, encoding="utf-8") as archivo:
        datos = json.load(archivo)
        return datos
except json.JSONDecodeError:
    logger.error(
        f"El archivo '{RUTA_JSON}' esta corrupto. "
        "Se iniciara con datos vacios."
    )
    return {"playbooks": []}
```



---

## Bug 003 — Importacion de CSV con codificacion incorrecta crasheaba sin aviso

**Fecha de bug:** Durante las pruebas de integracion

**Descripcion del bug:**
Al intentar importar un archivo CSV que habia sido guardado en codificacion Latin-1 (comun en Windows con caracteres como acento o ñ), la aplicacion lanzaba un `UnicodeDecodeError` que no se manejaba correctamente, mostrando un error tecnico al usuario.

**Pasos para reproducir:**
```bash
# Crear CSV con codificacion Latin-1 que tiene caracteres especiales
python -c "
with open('jugadas_latin.csv', 'w', encoding='latin-1') as f:
    f.write('nombre,tipo,formacion,yardas\n')
    f.write('Jugada de Proteccion,run,SHOTGUN,5.0\n')
"

python cli.py jugadas importar --archivo jugadas_latin.csv --playbook pb_test
# UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3
```

**Causa raiz:**
La funcion `cargar_csv()` en `data_importer.py` abria el archivo siempre con `encoding='utf-8'`. Si el archivo tenia otra codificacion y contenia caracteres no ASCII (como vocales acentuadas), Python lanzaba `UnicodeDecodeError` que no estaba capturado.

**Solucion aplicada:**
Se agrego un `except UnicodeDecodeError` que captura el error y muestra un mensaje explicativo al usuario con la solucion:

```python
# Antes (codigo con bug):
with open(ruta_archivo, encoding="utf-8") as archivo:
    ...

# Despues (codigo corregido):
try:
    with open(ruta_archivo, encoding="utf-8") as archivo:
        ...
except UnicodeDecodeError:
    raise ArchivoCsvError(
        f"El archivo '{ruta_archivo}' no esta en formato UTF-8. "
        "Guarda el archivo con codificacion UTF-8 e intentalo de nuevo."
    )
```


