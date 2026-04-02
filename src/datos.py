# datos.py
import pandas as pd

# Mapeo de columnas inglés → español
COLUMNAS_ES = {
    'Disease':              'Enfermedad',
    'Fever':                'Fiebre',
    'Cough':                'Tos',
    'Fatigue':              'Fatiga',
    'Difficulty Breathing': 'Dificultad al respirar',
    'Age':                  'Edad',
    'Gender':               'Género',
    'Blood Pressure':       'Presión arterial',
    'Cholesterol Level':    'Colesterol',
    'Outcome Variable':     'Resultado'
}

# Mapeo de valores Yes/No → Sí/No
VALORES_ES = {'Yes': 'Sí', 'No': 'No'}

# Columnas que son síntomas (Yes/No)
SINTOMAS = ['Fiebre', 'Tos', 'Fatiga', 'Dificultad al respirar']

# Preguntas que Baymax le hace al usuario por cada síntoma
PREGUNTAS = {
    'Fiebre':                  '¿Tienes fiebre?',
    'Tos':                     '¿Tienes tos?',
    'Fatiga':                  '¿Sientes fatiga o cansancio inusual?',
    'Dificultad al respirar':  '¿Tienes dificultad para respirar?'
}


def cargar_dataset(ruta='data/dataset.csv'):
    """
    Carga el CSV, renombra columnas al español,
    traduce Yes/No a Sí/No y devuelve el DataFrame limpio.
    """
    df = pd.read_csv(ruta)

    # 1. Renombrar columnas
    df = df.rename(columns=COLUMNAS_ES)

    # 2. Traducir valores de síntomas
    for col in SINTOMAS:
        if col in df.columns:
            df[col] = df[col].map(VALORES_ES)

    # 3. Eliminar filas con valores nulos
    df = df.dropna()

    # 4. Resetear el índice después de limpiar
    df = df.reset_index(drop=True)

    return df


def verificar_dataset(df):
    """
    Imprime un resumen de verificación del dataset limpio.
    Útil para confirmar que todo cargó bien.
    """
    print(f"Dataset cargado: {df.shape[0]} registros, {df.shape[1]} columnas")
    print(f"Enfermedades únicas: {df['Enfermedad'].nunique()}")
    print(f"Columnas: {df.columns.tolist()}")


# Si ejecutas este archivo directamente, hace la verificación
if __name__ == '__main__':
    df = cargar_dataset('data/Disease_symptom_and_patient_profile_dataset.csv')
    verificar_dataset(df)

