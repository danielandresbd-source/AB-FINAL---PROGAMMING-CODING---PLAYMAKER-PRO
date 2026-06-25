# Pseudocodigo de Algoritmos Principales — PlayMaker Pro



---

## RF4 — Deteccion de Anomalias en Jugadas

### Descripcion del Algoritmo

El algoritmo de deteccion de anomalias evalua cada jugada del dataset buscando datos inusuales o incorrectos. Usa el metodo estadistico Z-score para detectar valores extremos en las yardas, y ademas verifica otras condiciones como nombres duplicados o valores imposibles.

### Pseudocodigo

```
FUNCION detectar_anomalias(jugadas: lista[Play]) -> lista[dict]:

  SI jugadas esta VACIA:
    RETORNAR lista_vacia

  anomalias = []

  // Calcular la media y desviacion estandar de las yardas
  lista_yardas = [jugada.yardas PARA CADA jugada EN jugadas]
  media = SUMA(lista_yardas) / LONGITUD(lista_yardas)
  varianza = SUMA((y - media)^2 PARA y EN lista_yardas) / LONGITUD(lista_yardas)
  desviacion = RAIZ_CUADRADA(varianza)

  // Recopilar todos los nombres para detectar duplicados
  todos_los_nombres = [jugada.nombre.MINUSCULAS() PARA CADA jugada EN jugadas]

  PARA CADA jugada EN jugadas:
    razones = []

    // Anomalia 1: yardas outlier por Z-score
    SI desviacion > 0:
      z_score = (jugada.yardas - media) / desviacion
      SI VALOR_ABSOLUTO(z_score) > 2.5:
        razones.ANADIR("Yardas fuera de rango estadistico (Z=" + z_score + ")")

    // Anomalia 2: nombre duplicado
    SI todos_los_nombres.CONTAR(jugada.nombre.MINUSCULAS()) > 1:
      razones.ANADIR("Nombre de jugada duplicado en el dataset")

    // Anomalia 3: tasa de exito imposible
    SI jugada.tasa_exito < 0.0 O jugada.tasa_exito > 1.0:
      razones.ANADIR("Tasa de exito fuera del rango valido [0.0, 1.0]")

    // Anomalia 4: down_distance desconocido
    SI jugada.down_distance NO ESTA EN lista_downs_validos:
      razones.ANADIR("Situacion de down-and-distance desconocida")

    // Anomalia 5: hash_position no reconocida
    SI jugada.hash_position NO ESTA EN ["left", "middle", "right"]:
      razones.ANADIR("Posicion en el campo no reconocida")

    // Si hay razones, agregar a la lista de anomalias
    SI razones NO ESTA VACIA:
      anomalias.ANADIR({"jugada": jugada, "razones": razones})

  RETORNAR anomalias
```

### Implementacion en Python para el desarollo del proyecto (archivo `analyzer.py`)

```python
def detectar_anomalias(jugadas):
    if not jugadas:
        return []

    lista_yardas = [j.yardas for j in jugadas]
    media_yardas = sum(lista_yardas) / len(lista_yardas)
    varianza = sum((y - media_yardas) ** 2 for y in lista_yardas) / len(lista_yardas)
    desviacion_estandar = math.sqrt(varianza) if varianza > 0 else 0

    todos_los_nombres = [j.nombre.lower() for j in jugadas]
    anomalias_encontradas = []

    for jugada in jugadas:
        razones_anomalia = []

        if desviacion_estandar > 0:
            z_score = (jugada.yardas - media_yardas) / desviacion_estandar
            if abs(z_score) > 2.5:
                razones_anomalia.append(
                    f"Yardas fuera del rango estadistico (Z-score = {round(z_score, 2)})"
                )

        # ... resto de verificaciones

        if razones_anomalia:
            anomalias_encontradas.append({
                "jugada": jugada,
                "razones": razones_anomalia,
            })

    return anomalias_encontradas
```

---

## RF7 — Prediccion de Efectividad con Media Movil Simple

### Descripcion del Algoritmo

La media movil simple (MMS) calcula el promedio de los ultimos N valores de una serie de datos (donde N es el tamano de la ventana). Se usa para predecir cual sera la efectividad de las proximas jugadas basandose en el historial de jugadas pasadas.

**Ejemplo visual con ventana=3:**

```
Tasas historicas:  [0.60, 0.55, 0.70, 0.65, 0.80, 0.72]

Media movil:
  Posicion 3: promedio(0.60, 0.55, 0.70) = 0.617
  Posicion 4: promedio(0.55, 0.70, 0.65) = 0.633
  Posicion 5: promedio(0.70, 0.65, 0.80) = 0.717
  Posicion 6: promedio(0.65, 0.80, 0.72) = 0.723  <- prediccion

Prediccion para la siguiente jugada: 72.3% de exito
```

### Pseudocodigo

```
FUNCION predecir_efectividad(jugadas: lista[Play], ventana: int = 5) -> dict:

  SI LONGITUD(jugadas) < ventana:
    LANZAR ValueError("Se necesitan al menos " + ventana + " registros")

  // Ordenar jugadas cronologicamente y extraer tasas de exito
  jugadas_ordenadas = ORDENAR(jugadas, CLAVE = jugada.creada_en)
  tasas = [jugada.tasa_exito PARA CADA jugada EN jugadas_ordenadas]

  // Calcular la media movil para cada posicion valida
  medias_moviles = []
  PARA i DESDE ventana HASTA LONGITUD(tasas) + 1:
    ventana_actual = tasas[i - ventana : i]
    media = SUMA(ventana_actual) / ventana
    medias_moviles.ANADIR(REDONDEAR(media, 4))

  // La prediccion es la ultima media movil calculada
  prediccion = medias_moviles[ULTIMO]

  // Determinar la tendencia comparando las dos ultimas medias
  SI LONGITUD(medias_moviles) >= 2:
    diferencia = medias_moviles[-1] - medias_moviles[-2]
    SI diferencia > 0.01:
      tendencia = "subiendo"
    SINO SI diferencia < -0.01:
      tendencia = "bajando"
    SINO:
      tendencia = "estable"

  RETORNAR {
    "prediccion": prediccion,
    "tendencia": tendencia,
    "ventana_usada": ventana,
    "total_registros": LONGITUD(jugadas),
    "medias_moviles": medias_moviles,
    "ultimo_valor_real": tasas[-1]
  }
```

### Implementacion en Python para el desarollo del proyecto (archivo `analyzer.py`)

```python
def predecir_efectividad(jugadas, ventana=5):
    if len(jugadas) < ventana:
        raise ValueError(
            f"Se necesitan al menos {ventana} registros. Solo hay {len(jugadas)}."
        )

    jugadas_ordenadas = sorted(jugadas, key=lambda j: j.creada_en)
    tasas_de_exito = [j.tasa_exito for j in jugadas_ordenadas]

    medias_moviles = []
    for i in range(ventana, len(tasas_de_exito) + 1):
        ventana_actual = tasas_de_exito[i - ventana:i]
        media = sum(ventana_actual) / ventana
        medias_moviles.append(round(media, 4))

    prediccion = medias_moviles[-1]

    # Calcular tendencia
    if len(medias_moviles) >= 2:
        diferencia = medias_moviles[-1] - medias_moviles[-2]
        if diferencia > 0.01:
            tendencia = "subiendo"
        elif diferencia < -0.01:
            tendencia = "bajando"
        else:
            tendencia = "estable"

    return {
        "prediccion": prediccion,
        "tendencia": tendencia,
        ...
    }
```

---

## Diagrama de Flujo del CLI

```
Inicio: python cli.py <comando> <subcomando> [opciones]
                    |
                    v
           ------------------
          |  argparse parsea |
          |  los argumentos  |
           ------------------
                    |
            -------------------
          |                    |
    No hay modulo         Si hay modulo
          |                    |
    Mostrar ayuda        No hay accion
          |                    |
      (fin)             Mostrar ayuda del modulo
                              |
                         Si hay accion
                              |
                   Buscar en tabla de comandos
                              |
               ----------------------------
              |              |              |
         playbooks        jugadas        analisis
              |              |              |
    listar/crear/       listar/anadir/  estadisticas/
    eliminar/exportar   eliminar/       anomalias/
                        importar        prediccion/alertas
```
