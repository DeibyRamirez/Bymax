# main.py
from src.bymax_agente import BaymaxAgent
from src.datos import PREGUNTAS

def limpiar_pantalla():
    print("\n" + "─" * 50 + "\n")

def main():
    print("=" * 50)
    print("  BAYMAX — Asistente médico personal")
    print("=" * 50)

    agente = BaymaxAgent()

    # Saludo inicial
    saludo = agente.responder(
        "Hola, soy Baymax. Voy a hacerte algunas preguntas "
        "sobre tus síntomas para orientarte. ¿Empezamos?"
    )
    print(f"\nBaymax: {saludo}")
    input("Tú (presiona Enter para continuar): ")

    # Loop principal
    while True:
        limpiar_pantalla()

        # Razona con lo que sabe hasta ahora
        agente.razonar()
        decision = agente.decidir()

        if decision == 'DIAGNOSTICAR':
            # Muestra diagnóstico y candidatos
            print(f"Baymax: {agente.diagnostico_texto()}\n")
            print("── Diagnósticos posibles ──")
            for enfermedad, pct in agente.candidatos.items():
                barra = '█' * int(pct / 5)
                print(f"  {enfermedad:<30} {barra} {pct}%")
            break

        elif decision == 'PREGUNTAR':
            sintoma = agente.siguiente_pregunta()
            if sintoma is None:
                # Ya preguntó todo
                print(f"Baymax: {agente.diagnostico_texto()}")
                break

            pregunta = PREGUNTAS[sintoma]
            print(f"Baymax: {pregunta} (s/n)")

            # Recibe y valida respuesta
            while True:
                resp = input("Tú: ").strip().lower()
                if resp in ['s', 'si', 'sí', '1', 'y', 'yes']:
                    agente.percibir(sintoma, 'Sí')
                    break
                elif resp in ['n', 'no', '0']:
                    agente.percibir(sintoma, 'No')
                    break
                else:
                    print("  Por favor responde s (sí) o n (no)")

    print("\n" + "=" * 50)
    print("  Consulta tu médico para un diagnóstico oficial.")
    print("=" * 50)

if __name__ == '__main__':
    main()
