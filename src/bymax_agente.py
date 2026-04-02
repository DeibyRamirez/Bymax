# baymax_agent.py
from src.datos import DATOS_PERFIL, MAPEO_GENERO, PREGUNTAS, PREGUNTAS_PERFIL, SINTOMAS

class BaymaxAgent:

    def __init__(self, df):
        self.df = df
        self.estado = 'ESCUCHANDO'
        self.sintomas_usuario = {}   # {'Fiebre': 'Sí', 'Tos': 'No', ...}
        self.perfil_usuario = {'Edad': None, 'Género': None}
        self.candidatos = {}         # {'Influenza': 0.82, 'COVID-19': 0.41, ...}
        self.historial_chat = []     # lista de (rol, mensaje)
        self.preguntas_realizadas = []

    # ── PERCEPCIÓN ──────────────────────────────────────────────
    def percibir(self, sintoma, valor):
        """Registra un síntoma que el usuario reportó."""
        self.sintomas_usuario[sintoma] = valor
        if sintoma not in self.preguntas_realizadas:
            self.preguntas_realizadas.append(sintoma)
        self.historial_chat.append(('usuario', f"{sintoma}: {valor}"))

    def percibir_perfil(self, campo, valor):
        """Registra datos de perfil del usuario."""
        valor_original = valor
        if campo == 'Edad':
            valor = int(valor)
        elif campo == 'Género':
            valor = MAPEO_GENERO.get(valor.strip().lower())

        self.perfil_usuario[campo] = valor
        if campo not in self.preguntas_realizadas:
            self.preguntas_realizadas.append(campo)
        self.historial_chat.append(('usuario', f"{campo}: {valor_original}"))

    # ── RAZONAMIENTO ─────────────────────────────────────────────
    def razonar(self):
        """
        Filtra el dataset con los síntomas conocidos
        y calcula la probabilidad de cada enfermedad.
        """
        df_filtrado = self.df.copy()

        for sintoma, valor in self.sintomas_usuario.items():
            df_filtrado = df_filtrado[df_filtrado[sintoma] == valor]

        if self.perfil_usuario['Edad'] is not None:
            edad = self.perfil_usuario['Edad']
            df_filtrado = df_filtrado[df_filtrado['Edad'].between(max(0, edad - 10), edad + 10)]

        if self.perfil_usuario['Género'] is not None:
            df_filtrado = df_filtrado[df_filtrado['Género'] == self.perfil_usuario['Género']]

        if df_filtrado.empty and self.sintomas_usuario:
            df_relajado = self.df.copy()
            sintomas_si = [s for s, v in self.sintomas_usuario.items() if v == 'Sí']
            for sintoma in sintomas_si:
                df_relajado = df_relajado[df_relajado[sintoma] == 'Sí']
            df_filtrado = df_relajado if not df_relajado.empty else self.df.copy()

        conteo = df_filtrado['Enfermedad'].value_counts()
        total = conteo.sum()
        self.candidatos = {
            enfermedad: round((n / total) * 100, 1)
            for enfermedad, n in conteo.head(5).items()
        }

    # ── DECISIÓN ─────────────────────────────────────────────────
    def decidir(self):
        """
        Decide qué hacer según la confianza actual.
        Devuelve 'DIAGNOSTICAR' o 'PREGUNTAR'.
        """
        if not self.candidatos:
            return 'PREGUNTAR'

        confianza_top = list(self.candidatos.values())[0]
        sintomas_dados = len(self.sintomas_usuario)
        perfil_completo = all(self.perfil_usuario[c] is not None for c in DATOS_PERFIL)

        if confianza_top >= 65 and perfil_completo:
            self.estado = 'DIAGNOSTICANDO'
            return 'DIAGNOSTICAR'

        if sintomas_dados >= len(SINTOMAS) and perfil_completo:
            self.estado = 'DIAGNOSTICANDO'
            return 'DIAGNOSTICAR'
        else:
            self.estado = 'INTERROGANDO'
            return 'PREGUNTAR'

    # ── SIGUIENTE PREGUNTA ────────────────────────────────────────
    def siguiente_pregunta(self):
        """
        Devuelve el próximo síntoma que Baymax
        aún no le ha preguntado al usuario.
        """
        for campo in DATOS_PERFIL:
            if self.perfil_usuario[campo] is None:
                return campo

        pendientes = [s for s in SINTOMAS if s not in self.sintomas_usuario]
        if not pendientes:
            return None

        mejor_sintoma = None
        mejor_puntaje = -1

        for sintoma in pendientes:
            puntaje = self._puntaje_discriminacion(sintoma)
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_sintoma = sintoma

        return mejor_sintoma

    def _puntaje_discriminacion(self, sintoma):
        if not self.candidatos:
            return int((self.df[sintoma] == 'Sí').sum())

        top = list(self.candidatos.keys())
        sub = self.df[self.df['Enfermedad'].isin(top)]
        if sub.empty:
            return 0

        yes_rate = (sub[sintoma] == 'Sí').mean()
        return abs(0.5 - yes_rate)

    def validar_entrada_perfil(self, campo, valor):
        if campo == 'Edad':
            try:
                edad = int(valor)
                return 0 <= edad <= 120
            except ValueError:
                return False

        if campo == 'Género':
            return valor.strip().lower() in MAPEO_GENERO

        return False

    def estado_en_vivo(self):
        return {
            'perfil': self.perfil_usuario,
            'sintomas': self.sintomas_usuario,
            'candidatos': self.candidatos,
        }

    def texto_pregunta(self, campo):
        if campo in PREGUNTAS:
            return PREGUNTAS[campo]
        return PREGUNTAS_PERFIL[campo]

    def opciones_respuesta(self, campo):
        if campo in PREGUNTAS:
            return ['Sí', 'No']
        if campo == 'Género':
            return ['Masculino', 'Femenino']
        return []

    # ── ACCIÓN: RESPUESTA ─────────────────────────────────────────
    def responder(self, mensaje):
        """Registra una respuesta de Baymax en el historial."""
        self.historial_chat.append(('baymax', mensaje))
        return mensaje

    # ── DIAGNÓSTICO FINAL ─────────────────────────────────────────
    def diagnostico_texto(self):
        """Genera el mensaje de diagnóstico final."""
        if not self.candidatos:
            return "No encontré coincidencias suficientes. Te recomiendo consultar un médico."

        top_enfermedad = list(self.candidatos.keys())[0]
        top_confianza  = list(self.candidatos.values())[0]

        msg = f"Basándome en tus síntomas, el diagnóstico más probable es "
        msg += f"**{top_enfermedad}** con una confianza del {top_confianza}%.\n"
        msg += "Recuerda que esto es orientativo — consulta un médico para confirmarlo."
        return msg
