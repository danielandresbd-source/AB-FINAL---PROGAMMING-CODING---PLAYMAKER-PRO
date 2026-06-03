# Manual de Usuario — PlayMaker Pro

**Proyecto:** AB Final — Programming & Coding | MSMK University College 2025–2026

---

## Introduccion

PlayMaker Pro es una herramienta de linea de comandos que permite a coordinadores y entrenadores de futbol americano crear y analizar playbooks digitalmente. Este manual explica como usar cada funcion de la aplicacion.

---

## Inicio Rapido

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

## Modulo 1: Playbooks

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

## Modulo 2: Jugadas

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

### Añadir una jugada

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

| Ofensivas | Defensivas |
|---|---|
| SHOTGUN | FOUR_THREE |
| I_FORMATION | THREE_FOUR |
| SINGLEBACK | NICKEL |
| GUN_TRIPS | DIME |
| EMPTY_SET | |
| PISTOL | |
| WILDCAT | |

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

## Modulo 3: Analisis

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

## Modulo 4: Reportes

### Exportar estadisticas a CSV

```bash
python cli.py reportes csv --playbook pb_abc12345
```

Genera un CSV con estadisticas completas en `data/exports/`.

---

## Modulo 5: Simulador

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

## Flujo de Trabajo Recomendado

```
1. Crear el playbook
   python cli.py playbooks crear --nombre "Red Zone Offense"

2. Importar jugadas base desde CSV
   python cli.py jugadas importar --archivo data/sample_plays.csv --playbook <ID>

3. Añadir jugadas propias manualmente
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
