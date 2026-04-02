# baymax_agent.py
from src.datos import cargar_dataset, SINTOMAS, PREGUNTAS

class BaymaxAgent:

    def __init__(self):
        self.df = cargar_dataset('data/Disease_symptom_and_patient_profile_dataset.csv')
        self.estado = 'ESCUCHANDO'
        self.sintomas_usuario = {}   # {'Fiebre': 'Sí', 'Tos': 'No', ...}
        self.candidatos = {}         # {'Influenza': 0.82, 'COVID-19': 0.41, ...}
        self.historial_chat = []     # lista de (rol, mensaje)

    # ── PERCEPCIÓN ──────────────────────────────────────────────
    def percibir(self, sintoma, valor):
        """Registra un síntoma que el usuario reportó."""
        self.sintomas_usuario[sintoma] = valor
        self.historial_chat.append(('usuario', f"{sintoma}: {valor}"))

    # ── RAZONAMIENTO ─────────────────────────────────────────────
    def razonar(self):
        """
        Filtra el dataset con los síntomas conocidos
        y calcula la probabilidad de cada enfermedad.
        """
        df_filtrado = self.df.copy()

        for sintoma, valor in self.sintomas_usuario.items():
            df_filtrado = df_filtrado[df_filtrado[sintoma] == valor]

        if df_filtrado.empty:
            # Si no hay coincidencias exactas, usa solo el síntoma principal
            primer_sintoma = list(self.sintomas_usuario.items())[0]
            df_filtrado = self.df[
                self.df[primer_sintoma[0]] == primer_sintoma[1]
            ]

        # Calcula porcentaje de cada enfermedad en los resultados filtrados
        conteo = df_filtrado['Enfermedad'].value_counts()
        total  = conteo.sum()
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
        sintomas_total = len(SINTOMAS)

        if confianza_top >= 70 or sintomas_dados >= sintomas_total:
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
        for sintoma in SINTOMAS:
            if sintoma not in self.sintomas_usuario:
                return sintoma
        return None

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
