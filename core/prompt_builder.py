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

    columnas = ", ".join(df.columns.tolist())
    n_filas  = len(df)

    # Limitar el resumen estadístico para no saturar el contexto del modelo.
    # describe(include="all") en datasets anchos puede generar cientos de líneas
    # y consumir la mayor parte del contexto disponible de Phi-4 (~16K tokens).
    resumen_df = df.describe(include="all")
    max_cols_resumen = 15
    if len(resumen_df.columns) > max_cols_resumen:
        resumen = (
            resumen_df.iloc[:, :max_cols_resumen].to_string()
            + f"\n... (y {len(resumen_df.columns) - max_cols_resumen} columnas más, omitidas para abreviar)"
        )
    else:
        resumen = resumen_df.to_string()

    # Determinar si la consulta probablemente requiere visualización para
    # darle al modelo una instrucción de salida única y sin ambigüedad,
    # evitando que mezcle la rama de `resultado` con la de `plt`.
    palabras_viz = {
        "gráfico", "grafico", "grafica", "gráfica", "chart", "plot",
        "visualiz", "histograma", "barras", "línea", "linea",
        "dispersión", "dispersion", "pie", "mapa", "heatmap", "diagrama",
    }
    requiere_viz = any(p in consulta.lower() for p in palabras_viz)

    if requiere_viz:
        instruccion_salida = (
            "La consulta requiere una visualización. "
            "Genera exactamente UNA figura usando matplotlib o seaborn. "
            "Ejemplo con matplotlib: fig, ax = plt.subplots(); ax.bar(x, y); plt.tight_layout(). "
            "Ejemplo con seaborn: sns.barplot(data=df, x='col_x', y='col_y'); plt.tight_layout(). "
            "Termina SIEMPRE con plt.tight_layout(). No llames a plt.show(). "
            "No asignes nada a una variable llamada `resultado`."
        )
    else:
        instruccion_salida = (
            "La consulta NO requiere visualización. "
            "Guarda el resultado final en una variable llamada `resultado` como string. "
            "Ejemplo: resultado = str(df['col'].mean()). "
            "No generes ninguna figura ni llames a plt ni a sns."
        )

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
1. Tu respuesta debe tener EXACTAMENTE este formato, sin excepciones:

   NOMBRE: nombre_descriptivo_en_snake_case
   CODIGO:
   <código Python aquí>

   El NOMBRE debe ser snake_case, máximo 5 palabras, descriptivo del análisis.
   El CODIGO debe ser código Python ejecutable puro, sin texto explicativo,
   sin comentarios en prosa, sin bloques de markdown (no uses ```python ni ```).
2. Las siguientes librerías ya están importadas en el entorno y disponibles directamente:
   pandas as pd, matplotlib.pyplot as plt, seaborn as sns.
   El DataFrame ya cargado se llama `df`. Úsalas sin importarlas de nuevo.
   No leas archivos. No uses input().
3. {instruccion_salida}
4. Para agregaciones múltiples sobre una columna, usa ÚNICAMENTE la sintaxis de lista:
   df.groupby('col_grupo')['col_valor'].agg(['mean', 'min', 'max'])
   NUNCA uses named aggregation con tuplas dentro de agg (e.g. agg(nombre=('col', 'func'))).
5. El código debe ser correcto y ejecutarse sin errores dado el dataset descrito.

RESPUESTA:
"""

    return prompt