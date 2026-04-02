# visualizacion.py
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')   # necesario para Flask (sin ventana gráfica)
import io, base64
from analisis import frecuencia_sintomas, top_enfermedades

VERDE_BAYMAX = '#1D9E75'
COLORES      = ['#1D9E75','#5DCAA5','#9FE1CB','#C0DD97','#D3D1C7']


def _fig_a_base64(fig):
    """
    Convierte una figura matplotlib a string base64.
    Así Flask puede enviarla al navegador sin guardar archivos.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight',
                facecolor='white', dpi=120)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_b64


def grafica_diagnosticos(candidatos: dict):
    """
    Gráfica 1: barras horizontales con probabilidad
    de cada enfermedad candidata.
    """
    enfermedades = list(candidatos.keys())
    valores      = list(candidatos.values())

    fig, ax = plt.subplots(figsize=(7, 3.5))
    bars = ax.barh(enfermedades[::-1], valores[::-1],
                   color=COLORES[:len(enfermedades)], height=0.5)
    ax.set_xlabel('Probabilidad (%)', fontsize=11)
    ax.set_title('Diagnósticos posibles', fontsize=13, fontweight='bold')
    ax.bar_label(bars, fmt='%.1f%%', padding=4, fontsize=10)
    ax.set_xlim(0, 110)
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout()
    return _fig_a_base64(fig)


def grafica_sintomas(df):
    """
    Gráfica 2: frecuencia de cada síntoma en el dataset.
    Útil para mostrar qué síntomas son más comunes.
    """
    datos = frecuencia_sintomas(df)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(datos.keys(), datos.values(),
           color=VERDE_BAYMAX, width=0.5, alpha=0.85)
    ax.set_ylabel('Número de registros', fontsize=11)
    ax.set_title('Frecuencia de síntomas en el dataset', fontsize=13,
                 fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    for i, (k, v) in enumerate(datos.items()):
        ax.text(i, v + 2, str(v), ha='center', fontsize=10)
    fig.tight_layout()
    return _fig_a_base64(fig)


def grafica_enfermedades(df):
    """
    Gráfica 3: top 10 enfermedades del dataset.
    Da contexto sobre qué tan representada está cada enfermedad.
    """
    datos = top_enfermedades(df)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.barh(list(datos.keys())[::-1],
            list(datos.values())[::-1],
            color=VERDE_BAYMAX, height=0.6, alpha=0.85)
    ax.set_xlabel('Número de casos', fontsize=11)
    ax.set_title('Enfermedades más frecuentes', fontsize=13,
                 fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    fig.tight_layout()
    return _fig_a_base64(fig)