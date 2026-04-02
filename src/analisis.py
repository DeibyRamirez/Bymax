# analisis.py
import pandas as pd
from src.datos import cargar_dataset, SINTOMAS

def resumen_general(df):
    """Estadísticas clave del dataset completo."""
    return {
        'total_registros':    len(df),
        'enfermedades_unicas': df['Enfermedad'].nunique(),
        'con_fiebre':         int((df['Fiebre'] == 'Sí').sum()),
        'con_tos':            int((df['Tos'] == 'Sí').sum()),
    }

def frecuencia_sintomas(df):
    """
    Cuántas veces aparece cada síntoma en 'Sí'
    en todo el dataset. Para la gráfica de barras.
    """
    return {
        sintoma: int((df[sintoma] == 'Sí').sum())
        for sintoma in SINTOMAS
    }

def top_enfermedades(df):
    """Las 10 enfermedades más frecuentes en el dataset."""
    return df['Enfermedad'].value_counts().head(10).to_dict()

def perfil_por_enfermedad(df, enfermedad):
    """
    Dado un diagnóstico, devuelve el perfil típico:
    edad promedio, género más frecuente,
    presión arterial y colesterol más comunes.
    """
    sub = df[df['Enfermedad'] == enfermedad]
    if sub.empty:
        return {}
    return {
        'total_casos':       len(sub),
        'edad_promedio':     round(sub['Edad'].mean(), 1),
        'genero_frecuente':  sub['Género'].mode()[0],
        'presion_frecuente': sub['Presión arterial'].mode()[0],
        'colesterol_top':    sub['Colesterol'].mode()[0],
    }
