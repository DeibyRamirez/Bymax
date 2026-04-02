# app.py  — Programador 1
from flask import Flask, render_template, request, jsonify, session
from bymax_agente import BaymaxAgent
from visualizacion import grafica_diagnosticos, grafica_sintomas, grafica_enfermedades
from datos import cargar_dataset, PREGUNTAS, SINTOMAS
import uuid

app = Flask(__name__)
app.secret_key = 'baymax-secret-2024'

# Almacena agentes por sesión de usuario
agentes = {}

@app.route('/')
def index():
    """Página principal — carga el HTML."""
    return render_template('index.html')

@app.route('/iniciar', methods=['POST'])
def iniciar():
    """Crea un agente nuevo para esta sesión."""
    session_id = str(uuid.uuid4())
    agentes[session_id] = BaymaxAgent()
    primera_pregunta = PREGUNTAS[SINTOMAS[0]]
    return jsonify({
        'session_id': session_id,
        'mensaje': '¡Hola! Soy Baymax. Voy a hacerte algunas preguntas.',
        'pregunta': primera_pregunta,
        'sintoma':  SINTOMAS[0]
    })

@app.route('/responder', methods=['POST'])
def responder():
    """Recibe la respuesta del usuario y devuelve la siguiente acción."""
    datos       = request.json
    session_id  = datos['session_id']
    sintoma     = datos['sintoma']
    valor       = datos['valor']           # 'Sí' o 'No'

    agente = agentes.get(session_id)
    if not agente:
        return jsonify({'error': 'Sesión no encontrada'}), 400

    # 1. El agente percibe el síntoma
    agente.percibir(sintoma, valor)

    # 2. Razona con todos los síntomas acumulados
    agente.razonar()

    # 3. Decide qué hacer
    decision = agente.decidir()

    if decision == 'DIAGNOSTICAR':
        df = cargar_dataset()
        return jsonify({
            'accion':       'diagnostico',
            'mensaje':      agente.diagnostico_texto(),
            'candidatos':   agente.candidatos,
            'grafica_diag': grafica_diagnosticos(agente.candidatos),
            'grafica_sint': grafica_sintomas(df),
            'grafica_enf':  grafica_enfermedades(df)
        })
    else:
        proximo = agente.siguiente_pregunta()
        return jsonify({
            'accion':    'pregunta',
            'mensaje':   f'Entendido. Siguiente pregunta:',
            'pregunta':  PREGUNTAS[proximo],
            'sintoma':   proximo
        })

if __name__ == '__main__':
    app.run(debug=True)