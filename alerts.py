# ============================================================
# alerts.py
# RF6: Motor de alertas automaticas de conflictos
# Proyecto: AB Final - Programming & Coding
# ============================================================

"""
Este modulo implementa el motor de alertas del sistema.

Su trabajo es revisar jugadas y playbooks en busca de datos sospechosos
o problemas de capacidad, y avisar al usuario antes de que esos datos
causen errores mas adelante en otros modulos.

Analogia: es como el corrector ortografico de un procesador de texto,
pero en vez de buscar faltas de ortografia busca datos de futbol
americano que no tienen sentido (formaciones inventadas, yardas
imposibles, playbooks demasiado llenos, etc.)
"""

import logging

from models import Formation, PlayType

logger = logging.getLogger(__name__)

# Limite maximo de jugadas por playbook
LIMITE_JUGADAS_PLAYBOOK = 50

# Formaciones validas en el sistema
FORMACIONES_VALIDAS = [f.value for f in Formation]

# Tipos de jugada validos
TIPOS_VALIDOS = [t.value for t in PlayType]


class MotorAlertas:
    """
    Motor que evalua jugadas y playbooks en busca de conflictos y errores.

    Cada vez que se procesa una jugada o un playbook, este motor
    verifica si hay problemas y genera alertas que se muestran
    en consola y se guardan en el registro interno.
    """

    def __init__(self):
        """Inicializa el motor de alertas con el registro vacio."""

        # Lista donde se guardan todas las alertas generadas durante
        # la sesion actual (se acumulan, no se sobreescriben)
        self._registro_alertas = []

        # Reglas de validacion disponibles.
        # Cada regla es una funcion que recibe una jugada y devuelve
        # un mensaje de alerta (string) si encuentra un problema,
        # o None si la jugada esta bien. Tenerlas en una lista permite
        # recorrerlas todas con un simple bucle en evaluar_jugada(),
        # en lugar de escribir un if por cada regla cada vez que se
        # evalua una jugada.
        self._reglas_jugada = [
            self._regla_formacion_invalida,
            self._regla_tipo_invalido,
            self._regla_yardas_extremas,
            self._regla_tasa_exito_invalida,
            self._regla_down_distance_invalido,
        ]

    def evaluar_jugada(self, jugada):
        """
        Evalua una jugada aplicando todas las reglas de validacion.

        Muestra en consola cualquier alerta que se encuentre.

        Args:
            jugada: Objeto Play a evaluar.

        Returns:
            Lista de strings con las alertas encontradas.
            Lista vacia si la jugada no tiene problemas.
        """

        alertas_jugada = []

        # Recorremos todas las reglas definidas en __init__ y ejecutamos
        # cada una sobre la jugada. Si una regla devuelve un mensaje
        # (en vez de None), significa que encontro un problema.
        for regla in self._reglas_jugada:
            alerta = regla(jugada)
            if alerta:
                alertas_jugada.append(alerta)

                # Guardar la alerta en el registro con el nombre de la
                # jugada incluido, para saber a que jugada pertenece
                # cuando se revise el registro mas tarde
                mensaje_completo = f"[ALERTA] Jugada '{jugada.nombre}': {alerta}"
                self._registro_alertas.append(mensaje_completo)

                # Mostrar la alerta en consola para que el usuario la
                # vea inmediatamente, ademas de quedar guardada en logs
                print(mensaje_completo)
                logger.warning(mensaje_completo)

        return alertas_jugada

    def verificar_playbook(self, playbook):
        """
        Verifica si un playbook completo tiene problemas.

        Comprueba si esta lleno, si tiene jugadas duplicadas,
        y evalua cada jugada individualmente.

        Args:
            playbook: Objeto Playbook a verificar.

        Returns:
            Lista de strings con todas las alertas encontradas.
        """

        alertas_playbook = []

        # Verificar si el playbook esta lleno o cerca del limite.
        # Usamos dos niveles: ALERTA cuando ya esta lleno (no se puede
        # agregar nada mas) y AVISO cuando esta al 90% o mas (para que
        # el usuario se prepare antes de quedarse sin espacio)
        total_jugadas = len(playbook.jugadas)

        if total_jugadas >= LIMITE_JUGADAS_PLAYBOOK:
            alerta = (
                f"El playbook '{playbook.nombre}' ha alcanzado el limite "
                f"de {LIMITE_JUGADAS_PLAYBOOK} jugadas. No se pueden agregar mas."
            )
            alertas_playbook.append(alerta)
            self._registro_alertas.append(f"[ALERTA] {alerta}")
            print(f"[ALERTA] {alerta}")

        elif total_jugadas >= LIMITE_JUGADAS_PLAYBOOK * 0.9:
            alerta = (
                f"El playbook '{playbook.nombre}' tiene {total_jugadas} jugadas. "
                f"Esta cerca del limite de {LIMITE_JUGADAS_PLAYBOOK}."
            )
            alertas_playbook.append(alerta)
            self._registro_alertas.append(f"[AVISO] {alerta}")
            print(f"[AVISO] {alerta}")

        # Verificar si hay nombres de jugadas duplicados en el playbook.
        # Convertimos todo a minusculas antes de comparar para que
        # "HB Dive" y "hb dive" se consideren el mismo nombre duplicado.
        # Usamos dos sets: uno para llevar registro de los nombres ya
        # vistos, y otro para acumular los que resultaron duplicados.
        nombres_jugadas = [j.nombre.lower() for j in playbook.jugadas]
        nombres_vistos = set()
        nombres_duplicados = set()

        for nombre in nombres_jugadas:
            if nombre in nombres_vistos:
                nombres_duplicados.add(nombre)
            nombres_vistos.add(nombre)

        if nombres_duplicados:
            alerta = (
                f"El playbook '{playbook.nombre}' tiene jugadas con nombres "
                f"duplicados: {', '.join(nombres_duplicados)}"
            )
            alertas_playbook.append(alerta)
            self._registro_alertas.append(f"[ALERTA] {alerta}")
            print(f"[ALERTA] {alerta}")

        # Ademas de las verificaciones del playbook en si, evaluamos
        # cada jugada individualmente con las reglas de evaluar_jugada()
        # y juntamos todas las alertas en una sola lista de resultado
        for jugada in playbook.jugadas:
            alertas_jugada = self.evaluar_jugada(jugada)
            alertas_playbook.extend(alertas_jugada)

        if not alertas_playbook:
            print(f"El playbook '{playbook.nombre}' no tiene alertas. Todo correcto.")

        return alertas_playbook

    def obtener_alertas(self):
        """
        Devuelve todas las alertas guardadas en el registro.

        Returns:
            Lista de strings con todas las alertas generadas.
        """

        # Devolvemos una copia de la lista (list(...)) en vez de la
        # lista original, para que quien reciba el resultado no pueda
        # modificar el registro interno del motor por accidente
        return list(self._registro_alertas)

    def limpiar_registro(self):
        """Limpia el registro de alertas."""

        self._registro_alertas = []
        logger.info("Registro de alertas limpiado.")

    # --- Reglas de validacion individuales ---
    # Cada una de estas funciones revisa UN solo aspecto de la jugada.
    # Separarlas en funciones pequenas (en vez de un metodo gigante con
    # muchos ifs) hace que sea facil anadir, quitar o testear una regla
    # sin afectar a las demas.

    def _regla_formacion_invalida(self, jugada):
        """
        Verifica si la formacion de la jugada no es valida.

        Returns:
            Mensaje de alerta o None si esta bien.
        """

        if jugada.formacion not in FORMACIONES_VALIDAS:
            return (
                f"Formacion no reconocida: '{jugada.formacion}'. "
                f"Formaciones validas: {', '.join(FORMACIONES_VALIDAS)}"
            )
        return None

    def _regla_tipo_invalido(self, jugada):
        """
        Verifica si el tipo de jugada no es valido.

        Returns:
            Mensaje de alerta o None si esta bien.
        """

        if jugada.tipo not in TIPOS_VALIDOS:
            return (
                f"Tipo de jugada no reconocido: '{jugada.tipo}'. "
                f"Tipos validos: {', '.join(TIPOS_VALIDOS)}"
            )
        return None

    def _regla_yardas_extremas(self, jugada):
        """
        Verifica si las yardas de la jugada son valores extremos.

        Returns:
            Mensaje de alerta o None si esta bien.
        """

        # El campo de futbol americano mide 100 yardas, asi que ganar
        # mas de 99 yardas en una sola jugada es practicamente imposible
        if jugada.yardas > 99:
            return (
                f"Las yardas de la jugada son muy altas: {jugada.yardas}. "
                "Una jugada de mas de 99 yardas es inusual."
            )

        # Perder mas de 20 yardas en una sola jugada (por ejemplo, un
        # sack muy grande) tambien es estadisticamente raro
        if jugada.yardas < -20:
            return (
                f"Las yardas de la jugada son muy negativas: {jugada.yardas}. "
                "Una perdida de mas de 20 yardas es inusual."
            )

        return None

    def _regla_tasa_exito_invalida(self, jugada):
        """
        Verifica si la tasa de exito esta fuera del rango valido.

        Returns:
            Mensaje de alerta o None si esta bien.
        """

        # La tasa de exito es un porcentaje expresado como decimal,
        # por lo que matematicamente solo puede estar entre 0.0 y 1.0
        if jugada.tasa_exito < 0.0 or jugada.tasa_exito > 1.0:
            return (
                f"Tasa de exito invalida: {jugada.tasa_exito}. "
                "Debe estar entre 0.0 y 1.0."
            )
        return None

    def _regla_down_distance_invalido(self, jugada):
        """
        Verifica si la situacion de down-and-distance no es reconocida.

        Returns:
            Mensaje de alerta o None si esta bien.
        """

        # Lista de todas las situaciones de juego que el sistema
        # reconoce como validas (down = intento, distance = yardas
        # que faltan para conseguir un primer down)
        downs_validos = [
            "1st&10", "1st&goal",
            "2nd&long", "2nd&medium", "2nd&short", "2nd&goal",
            "3rd&long", "3rd&medium", "3rd&short", "3rd&goal",
            "4th&short", "4th&goal", "4th&long",
        ]

        if jugada.down_distance not in downs_validos:
            return (
                f"Situacion de down-and-distance no reconocida: "
                f"'{jugada.down_distance}'."
            )
        return None
