import pandas as pd


def construir_prompt(df: pd.DataFrame, consulta: str) -> str:
    """
    Construye el prompt que se enviará a Phi-4 vía Ollama.

    El prompt le entrega al modelo:
      - Los nombres de las columnas del dataset.
      - El resumen estadístico producido por df.describe().
      - La consulta del usuario en lenguaje natural.
      - Instrucciones explícitas de formato de respuesta.

    Parameters
    ----------
    df      : DataFrame cargado por el usuario.
    consulta: Texto libre ingresado en el campo de consulta.

    Returns
    -------
    str : Prompt listo para enviarse al modelo.
    """

    columnas  = ", ".join(df.columns.tolist())
    n_filas   = len(df)
    resumen   = df.describe(include="all").to_string()

    prompt = f"""Eres un experto en análisis de datos con Python.
Se te proporciona un DataFrame llamado `df` que ya está cargado en memoria.

INFORMACIÓN DEL DATASET
=======================
Filas      : {n_filas}
Columnas   : {columnas}

Resumen estadístico:
{resumen}

CONSULTA DEL USUARIO
====================
{consulta}

INSTRUCCIONES ESTRICTAS
=======================
1. Responde ÚNICAMENTE con código Python ejecutable. No escribas texto explicativo,
   comentarios en prosa, ni bloques de markdown (no uses ```python ni ```).
2. Usa SOLO las siguientes librerías, que ya están disponibles en el entorno:
   - pandas  (alias: pd)
   - matplotlib.pyplot  (alias: plt)
   - seaborn  (alias: sns)
   - El DataFrame ya cargado se llama `df`.
3. No importes ninguna librería. No leas archivos. No uses `input()`.
4. Si la consulta requiere una visualización, genera exactamente UNA figura
   con plt y llama a plt.tight_layout() al final. No llames a plt.show().
5. Si la consulta no requiere visualización (por ejemplo, pide un cálculo o
   un resumen), guarda el resultado final en una variable llamada `resultado`
   como string. Ejemplo: resultado = str(df['col'].mean())
6. El código debe ser correcto y ejecutarse sin errores dado el dataset descrito.

CÓDIGO PYTHON:
"""

    return prompt