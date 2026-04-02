# app.py  — Programador 1
from flask import Flask, jsonify, render_template, request
from src.bymax_agente import BaymaxAgent
from src.visualizacion import grafica_diagnosticos, grafica_sintomas, grafica_enfermedades
from src.datos import DATOS_PERFIL, SINTOMAS, cargar_dataset
import uuid
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

df_global = cargar_dataset('data/Disease_symptom_and_patient_profile_dataset.csv')

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
    agente = BaymaxAgent(df_global)
    agentes[session_id] = agente
    campo = agente.siguiente_pregunta()
    return jsonify({
        'session_id': session_id,
        'mensaje': '¡Hola! Soy Baymax. Vamos a revisar tu perfil y síntomas.',
        'pregunta': agente.texto_pregunta(campo),
        'campo': campo,
        'tipo': 'texto' if campo == 'Edad' else 'opciones',
        'opciones': agente.opciones_respuesta(campo),
        'estado': agente.estado_en_vivo(),
    })

@app.route('/responder', methods=['POST'])
def responder():
    """Recibe la respuesta del usuario y devuelve la siguiente acción."""
    datos = request.json
    session_id = datos['session_id']
    campo = datos['campo']
    valor = datos['valor']

    agente = agentes.get(session_id)
    if not agente:
        return jsonify({'error': 'Sesión no encontrada'}), 400

    if campo in SINTOMAS:
        if valor not in ('Sí', 'No'):
            return jsonify({'error': 'Respuesta inválida para síntoma'}), 400
        agente.percibir(campo, valor)
    elif campo in DATOS_PERFIL:
        if not agente.validar_entrada_perfil(campo, valor):
            return jsonify({
                'accion': 'pregunta',
                'mensaje': 'No pude entender esa respuesta. Intentemos de nuevo.',
                'pregunta': agente.texto_pregunta(campo),
                'campo': campo,
                'tipo': 'texto' if campo == 'Edad' else 'opciones',
                'opciones': agente.opciones_respuesta(campo),
                'estado': agente.estado_en_vivo(),
            })
        agente.percibir_perfil(campo, valor)
    else:
        return jsonify({'error': 'Campo desconocido'}), 400

    agente.razonar()
    decision = agente.decidir()

    if decision == 'DIAGNOSTICAR':
        return jsonify({
            'accion':       'diagnostico',
            'mensaje':      agente.diagnostico_texto(),
            'candidatos':   agente.candidatos,
            'grafica_diag': grafica_diagnosticos(agente.candidatos),
            'grafica_sint': grafica_sintomas(df_global),
            'grafica_enf':  grafica_enfermedades(df_global),
            'estado':       agente.estado_en_vivo(),
        })
    else:
        campo_siguiente = agente.siguiente_pregunta()
        return jsonify({
            'accion':    'pregunta',
            'mensaje':   'Entendido. Continuemos.',
            'pregunta':  agente.texto_pregunta(campo_siguiente),
            'campo':     campo_siguiente,
            'tipo':      'texto' if campo_siguiente == 'Edad' else 'opciones',
            'opciones':  agente.opciones_respuesta(campo_siguiente),
            'estado':    agente.estado_en_vivo(),
        })


@app.route('/estado', methods=['POST'])
def estado():
    datos = request.json
    session_id = datos['session_id']
    agente = agentes.get(session_id)
    if not agente:
        return jsonify({'error': 'Sesión no encontrada'}), 400

    return jsonify({'estado': agente.estado_en_vivo()})

if __name__ == '__main__':
    app.run(debug=True)
