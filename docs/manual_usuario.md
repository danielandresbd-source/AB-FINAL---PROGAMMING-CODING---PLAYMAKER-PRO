# Manual de Usuario — PlayMaker Pro

**Proyecto:** AB Final — Programming & Coding | MSMK
**Cliente:** Madrid Bulldogs — Equipo de Futbol Americano
**Version:** 1.0

---

## Indice

1. Instalacion paso a paso
2. Inicio rapido
3. Modulo 1: Playbooks
4. Modulo 2: Jugadas
5. Modulo 3: Analisis
6. Modulo 4: Reportes
7. Modulo 5: Simulador
8. Flujo de trabajo recomendado
9. Como interpretar los resultados
10. Preguntas frecuentes (FAQ)

---

## 1. Instalacion Paso a Paso

Esta seccion explica como instalar PlayMaker Pro desde cero en cualquier ordenador.

### Paso 1 — Instalar Python

Descarga Python 3.10 o superior desde [python.org/downloads](https://www.python.org/downloads/).

Durante la instalacion en Windows, marca la casilla **"Add Python to PATH"** antes de hacer clic en Install.

Verifica que la instalacion funciona abriendo una terminal y ejecutando:

```bash
python --version
# Debe mostrar: Python 3.10.x o superior
```

### Paso 2 — Instalar Git

Descarga Git desde [git-scm.com](https://git-scm.com/). Instala con las opciones por defecto.

Verifica la instalacion:

```bash
git --version
# Debe mostrar: git version 2.x.x
```

### Paso 3 — Clonar el repositorio

```bash
git clone https://github.com/danielandresbd-source/AB-FINAL---PROGAMMING-CODING---PLAYMAKER-PRO.git
cd AB-FINAL---PROGAMMING-CODING---PLAYMAKER-PRO
```

### Paso 4 — Crear el entorno virtual

El entorno virtual aísla las dependencias del proyecto para no interferir con otras instalaciones de Python.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Sabrás que el entorno virtual está activo cuando veas `(venv)` al inicio del prompt:

```
(venv) PS C:\...>
```

### Paso 5 — Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 6 — Verificar la instalacion

```bash
pytest tests/ -v
# Deben pasar todos los tests sin errores
```

### Paso 7 — Ejecutar la aplicacion

```bash
python cli.py --help
```

Si ves el menu de ayuda, la instalacion fue exitosa.

---

## 2. Inicio Rapido

```bash
# Ver todos los comandos disponibles
python cli.py --help

# Crear un playbook
python cli.py playbooks crear --nombre "Mi Primer Playbook"

# Importar las jugadas de muestra
python cli.py jugadas importar \
  --archivo data/sample_plays.csv \
  --playbook <ID del playbook>

# Ver estadisticas con grafico
python cli.py analisis estadisticas --playbook <ID del playbook>
```

---

## 3. Modulo 1: Playbooks

Los playbooks son el contenedor principal del sistema. Cada playbook puede tener hasta 50 jugadas.

### Listar todos los playbooks

```bash
python cli.py playbooks listar
```

Salida esperada:
```
=======================================================
  PLAYBOOKS GUARDADOS
=======================================================
  ID: pb_abc12345
  Nombre: Red Zone Offense
  Tipo de ofensa: spread
  Jugadas: 12
  Creado: 2025-05-08

  ID: pb_xyz98765
  Nombre: Two Minute Drill
  Tipo de ofensa: air_raid
  Jugadas: 8
  Creado: 2025-05-09
=======================================================
```

### Crear un playbook

```bash
python cli.py playbooks crear --nombre "Red Zone Offense"
python cli.py playbooks crear --nombre "Two Minute Drill" --tipo air_raid
```

Tipos de ofensa disponibles: `spread`, `power`, `west_coast`, `air_raid`, `option`

### Eliminar un playbook

```bash
python cli.py playbooks eliminar --id pb_abc12345
```

### Exportar jugadas a CSV

```bash
python cli.py playbooks exportar --id pb_abc12345
python cli.py playbooks exportar --id pb_abc12345 --archivo mi_reporte.csv
```

El archivo se guarda en `data/exports/`.

---

## 4. Modulo 2: Jugadas

### Listar jugadas de un playbook

```bash
python cli.py jugadas listar --playbook-id pb_abc12345
```

Salida esperada:
```
=======================================================
  JUGADAS DE: Red Zone Offense
=======================================================
  ID: play_xyz98765
  Nombre: HB Dive Left
  Tipo: run  |  Formacion: I_FORMATION
  Yardas: 4.5  |  Exito: 68%
  Situacion: 2nd&short

  ID: play_abc11111
  Nombre: Slant Route Right
  Tipo: pass  |  Formacion: SHOTGUN
  Yardas: 8.0  |  Exito: 72%
  Situacion: 3rd&medium
=======================================================
```

### Anadir una jugada

```bash
python cli.py jugadas anadir \
  --playbook pb_abc12345 \
  --nombre "HB Dive Left" \
  --tipo run \
  --formacion I_FORMATION \
  --yardas 4.5 \
  --tasa-exito 0.68 \
  --down 2nd&short \
  --hash middle \
  --descripcion "Entrega al RB que corre por el hueco A izquierdo"
```

**Tipos disponibles:** `run`, `pass`, `special_teams`

**Formaciones disponibles:**

| Ofensivas   | Defensivas |
|---|---|
| SHOTGUN     | FOUR_THREE |
| I_FORMATION | THREE_FOUR |
| SINGLEBACK  | NICKEL     |
| GUN_TRIPS   | DIME       |
| EMPTY_SET   |            |
| PISTOL      |            |
| WILDCAT     |            |

**Situaciones de down-and-distance validas:**
`1st&10`, `1st&goal`, `2nd&long`, `2nd&medium`, `2nd&short`, `2nd&goal`,
`3rd&long`, `3rd&medium`, `3rd&short`, `3rd&goal`, `4th&short`, `4th&goal`, `4th&long`

### Importar jugadas desde CSV

```bash
python cli.py jugadas importar \
  --archivo data/sample_plays.csv \
  --playbook pb_abc12345
```

**Formato requerido del CSV:**

```csv
nombre,tipo,formacion,yardas,tasa_exito,down_distance,hash_position,descripcion,etiquetas
HB Dive Left,run,I_FORMATION,4.5,0.68,2nd&short,middle,Descripcion aqui,etiqueta1;etiqueta2
```

Columnas obligatorias: `nombre`, `tipo`, `formacion`, `yardas`
Columnas opcionales: `tasa_exito`, `down_distance`, `hash_position`, `descripcion`, `etiquetas`

### Eliminar una jugada

```bash
python cli.py jugadas eliminar --playbook pb_abc12345 --id play_xyz98765
```

---

## 5. Modulo 3: Analisis

### Estadisticas descriptivas (RF3)

```bash
python cli.py analisis estadisticas --playbook pb_abc12345
```

Muestra:
- Total de jugadas
- Formacion mas usada
- Yardas promedio, minimas y maximas
- Grafico de barras ASCII por tipo de jugada
- Grafico de barras ASCII por formacion
- Top 5 jugadas por tasa de exito

### Deteccion de anomalias (RF4)

```bash
python cli.py analisis anomalias --playbook pb_abc12345
```

Detecta jugadas con:
- Yardas extremas (Z-score mayor a 2.5)
- Nombres duplicados
- Tasa de exito imposible (fuera de 0.0 a 1.0)
- Down-and-distance desconocido
- Hash position no reconocida

### Prediccion de efectividad (RF7)

```bash
# Con ventana por defecto de 5 jugadas
python cli.py analisis prediccion --playbook pb_abc12345

# Con ventana personalizada
python cli.py analisis prediccion --playbook pb_abc12345 --ventana 10
```

Requiere al menos tantas jugadas como el tamano de la ventana.

Salida esperada:
```
=======================================================
  PREDICCION DE EFECTIVIDAD: Red Zone Offense
=======================================================
  Prediccion: 65% de exito
  Tendencia actual: subiendo
  Ventana de calculo: 5 jugadas
  Total de registros analizados: 12
=======================================================
```

### Alertas automaticas (RF6)

```bash
python cli.py analisis alertas --playbook pb_abc12345
```

Verifica si el playbook tiene:
- Formaciones no reconocidas
- Tipos de jugada invalidos
- Yardas extremas
- Tasas de exito imposibles
- Nombres de jugada duplicados
- Playbook cerca del limite o lleno

---

## 6. Modulo 4: Reportes

### Exportar estadisticas a CSV

```bash
python cli.py reportes csv --playbook pb_abc12345
```

Genera un CSV con estadisticas completas en `data/exports/`.

---

## 7. Modulo 5: Simulador

```bash
# Generar 30 jugadas mixtas
python cli.py simulador generar --jugadas 30

# Generar solo jugadas de corrida
python cli.py simulador generar --jugadas 20 --tipo run

# Generar solo jugadas de pase
python cli.py simulador generar --jugadas 20 --tipo pass

# Generar jugadas de equipos especiales
python cli.py simulador generar --jugadas 10 --tipo special_teams
```

Los datos se guardan automaticamente en `data/exports/` como CSV.

---

## 8. Flujo de Trabajo Recomendado

```
1. Crear el playbook
   python cli.py playbooks crear --nombre "Red Zone Offense"

2. Importar jugadas base desde CSV
   python cli.py jugadas importar --archivo data/sample_plays.csv --playbook <ID>

3. Anadir jugadas propias manualmente
   python cli.py jugadas anadir --playbook <ID> --nombre "Mi Jugada" ...

4. Revisar alertas para detectar problemas
   python cli.py analisis alertas --playbook <ID>

5. Ver estadisticas con grafico
   python cli.py analisis estadisticas --playbook <ID>

6. Detectar jugadas con datos raros
   python cli.py analisis anomalias --playbook <ID>

7. Predecir la efectividad
   python cli.py analisis prediccion --playbook <ID>

8. Exportar para compartir
   python cli.py reportes csv --playbook <ID>
```

---

## 9. Como Interpretar los Resultados

Esta seccion explica el significado de cada resultado que muestra la aplicacion.

### 9.1 Estadisticas descriptivas

```
Total de jugadas: 12
Formacion mas usada: SHOTGUN
Yardas promedio: 6.4
Yardas minimas: 1.2
Yardas maximas: 18.5
```

- **Total de jugadas:** cuantas jugadas tiene el playbook en este momento.
- **Formacion mas usada:** la formacion que aparece con mas frecuencia. Si una sola formacion domina (mas del 70%), el rival puede anticipar tu juego con facilidad.
- **Yardas promedio:** media de yardas ganadas por jugada. En futbol americano profesional, un promedio de 5-6 yardas por jugada se considera bueno.
- **Yardas minimas y maximas:** el rango de variacion. Una diferencia muy grande entre el minimo y el maximo indica que el rendimiento es muy inconsistente.

### 9.2 Grafico de barras ASCII

```
  DISTRIBUCION POR TIPO DE JUGADA
=======================================================
  run            ############################## 18
  pass           #################### 12
  special_teams  #### 3
=======================================================
```

- Cada `#` representa una unidad relativa al tipo mas frecuente.
- El numero al final es el conteo real de jugadas de ese tipo.
- **Como leerlo:** si `run` tiene una barra mucho mas larga que `pass`, tu playbook es mayoritariamente de corrida. Un playbook equilibrado suele tener una proporcion de 40-60% pase y 30-50% corrida.

```
  DISTRIBUCION POR FORMACION
=======================================================
  SHOTGUN         ######################### 15
  I_FORMATION     ############## 8
  SINGLEBACK      ######### 5
=======================================================
```

- Las formaciones aparecen ordenadas de mayor a menor uso.
- Si una sola formacion supera el 60% del total, considera diversificar para dificultar la lectura del rival.

### 9.3 Top 5 jugadas por tasa de exito

```
  TOP 5 JUGADAS POR TASA DE EXITO
=======================================================
  1. Slant Route Right
     Tipo: pass  |  Yardas: 8.0
     Exito: ########################### 72%
```

- La **tasa de exito** es un valor entre 0% y 100% que indica con que frecuencia esta jugada logra el objetivo (ganar el primer down o anotar).
- Una jugada con mas del 70% de exito es una jugada de alta confianza.
- Una jugada con menos del 40% de exito deberia revisarse o eliminarse del playbook.

### 9.4 Deteccion de anomalias

```
Se encontraron 2 jugadas con datos inusuales:

Jugada: HB Mega Dive (ID: play_xyz)
  - Yardas fuera del rango estadistico (Z-score = 3.2)
  - Nombre de jugada duplicado en el dataset
```

- **Z-score mayor a 2.5:** las yardas de esta jugada son estadisticamente inusuales comparadas con el resto del playbook. Puede ser un dato correcto (una jugada excepcionalmente buena o mala) o un error de entrada de datos.
- **Nombre duplicado:** dos jugadas tienen el mismo nombre, lo que puede causar confusion durante el partido. Renombra una de ellas.
- **Tasa de exito fuera de rango:** el valor introducido es menor a 0.0 o mayor a 1.0, lo cual es matematicamente imposible. Corrige el dato.
- **Down-and-distance desconocido:** la situacion de juego no coincide con ninguna de las validas. Revisa el valor introducido.

**Como actuar:** corrige los datos de las jugadas marcadas usando `jugadas eliminar` y `jugadas anadir` con los valores correctos.

### 9.5 Prediccion de efectividad

```
Prediccion: 65% de exito
Tendencia actual: subiendo
Ventana de calculo: 5 jugadas
```

- **Prediccion:** porcentaje de exito esperado para las proximas jugadas, calculado como la media movil de las ultimas N jugadas (donde N es la ventana).
- **Tendencia subiendo:** las jugadas mas recientes tienen mejor tasa de exito que las anteriores. El equipo esta mejorando.
- **Tendencia bajando:** las jugadas recientes tienen peor rendimiento. Puede indicar que el rival ha ajustado su defensa.
- **Tendencia estable:** el rendimiento se mantiene constante.
- **Ventana de calculo:** cuantas jugadas se usan para calcular la prediccion. Una ventana de 5 es sensible a cambios recientes; una ventana de 10 es mas conservadora.

### 9.6 Alertas automaticas

```
[ALERTA] Jugada 'HB Mega Dive': Yardas extremas: 145.0
[AVISO] El playbook 'Red Zone Offense' tiene 46 jugadas. Esta cerca del limite de 50.
```

- **[ALERTA]:** problema que debe corregirse. Los datos son invalidos o el playbook esta lleno.
- **[AVISO]:** advertencia informativa. El sistema funciona pero conviene tomar accion pronto.

**Como actuar ante una alerta:**
- *Formacion no reconocida:* corrige el nombre de la formacion usando uno de los valores validos.
- *Yardas extremas:* verifica si el dato es correcto. Si es un error, elimina la jugada y vuelve a anadirla con las yardas correctas.
- *Playbook lleno o cerca del limite:* elimina jugadas poco usadas antes de anadir nuevas.
- *Nombres duplicados:* renombra una de las jugadas con nombres identicos.

---

## 10. Preguntas Frecuentes (FAQ)

### Error 1: "No se encontro el playbook con el ID indicado"

```
[ERROR] No se encontro ningun playbook con el ID 'pb_abc123'.
```

**Causa:** el ID del playbook que escribiste no existe en el sistema.

**Solucion:** lista todos los playbooks para ver los IDs disponibles y copia el correcto:

```bash
python cli.py playbooks listar
```

---

### Error 2: "El archivo CSV no esta en formato UTF-8"

```
[ERROR] El archivo 'jugadas.csv' no esta en formato UTF-8.
Guarda el archivo con codificacion UTF-8 e intentalo de nuevo.
```

**Causa:** el archivo CSV fue creado en Windows con codificacion Latin-1 y contiene caracteres especiales (acentos, ñ, etc.).

**Solucion:** abre el CSV en Excel o en un editor de texto, guárdalo de nuevo seleccionando "UTF-8" como codificacion, e importalo otra vez.

---

### Error 3: "El playbook ya tiene 50 jugadas. No se pueden agregar mas"

```
[ERROR] El playbook 'Red Zone Offense' ya tiene 50 jugadas. No se pueden agregar mas.
```

**Causa:** el playbook alcanzo el limite maximo de 50 jugadas.

**Solucion:** elimina alguna jugada que no uses antes de anadir nuevas:

```bash
# Listar jugadas para ver los IDs
python cli.py jugadas listar --playbook-id pb_abc12345

# Eliminar la jugada que no necesitas
python cli.py jugadas eliminar --playbook pb_abc12345 --id play_xyz98765
```

---

### Error 4: "Se necesitan al menos N registros para calcular la prediccion"

```
[ERROR] Se necesitan al menos 5 registros para calcular la prediccion. Solo hay 3 jugadas.
```

**Causa:** el playbook tiene menos jugadas que el tamano de la ventana de prediccion (por defecto 5).

**Solucion:** usa una ventana mas pequena o anade mas jugadas al playbook:

```bash
# Reducir la ventana de calculo
python cli.py analisis prediccion --playbook pb_abc12345 --ventana 3
```

---

### Error 5: "El tipo 'X' no es valido"

```
[ERROR] Fila 3: el tipo 'especial' no es valido. Opciones permitidas: ['run', 'pass', 'special_teams']
```

**Causa:** el CSV contiene un valor de tipo de jugada que no coincide exactamente con los valores permitidos.

**Solucion:** edita el CSV y asegurate de usar exactamente `run`, `pass` o `special_teams` (en minuscula, sin espacios).

---

### Error 6: "pytest no se reconoce como comando"

```
pytest : El termino 'pytest' no se reconoce...
```

**Causa:** el entorno virtual no esta activado o las dependencias no estan instaladas.

**Solucion:**

```bash
# Activar el entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ahora si ejecutar pytest
pytest tests/ -v
```