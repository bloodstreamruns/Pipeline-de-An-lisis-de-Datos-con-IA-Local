import os
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure

# Raíz del proyecto: dos niveles arriba desde lógica/
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_ROOT  = os.path.join(BASE_DIR, "resultados")


# ── Utilidades de sistema de archivos ─────────────────────────────────────────

def _asegurar_raiz():
    """Crea la carpeta raíz de resultados si no existe."""
    os.makedirs(SCRIPTS_ROOT, exist_ok=True)


def ruta_carpeta(nombre: str) -> str:
    return os.path.join(SCRIPTS_ROOT, nombre)


def ruta_script(carpeta: str, nombre: str) -> str:
    """Devuelve la ruta absoluta de un script dado su carpeta y nombre (sin .py)."""
    return os.path.join(SCRIPTS_ROOT, carpeta, f"{nombre}.py")


# ── Lectura del árbol ──────────────────────────────────────────────────────────

def obtener_arbol() -> dict[str, list[str]]:
    """
    Recorre SCRIPTS_ROOT y devuelve un diccionario:
        { nombre_carpeta: [nombre_script_sin_extension, ...] }
    Solo considera directorios de un nivel y archivos .py dentro de ellos.
    Los archivos .py sueltos en la raíz se ignoran.
    """
    _asegurar_raiz()
    arbol = {}
    for entrada in sorted(os.scandir(SCRIPTS_ROOT), key=lambda e: e.name.lower()):
        if entrada.is_dir():
            scripts = sorted(
                [
                    os.path.splitext(f.name)[0]
                    for f in os.scandir(entrada.path)
                    if f.is_file() and f.name.endswith(".py")
                ]
            )
            arbol[entrada.name] = scripts
    return arbol


# ── CRUD de carpetas ───────────────────────────────────────────────────────────

def crear_carpeta(nombre: str) -> tuple[bool, str]:
    """
    Crea una carpeta dentro de SCRIPTS_ROOT.
    Retorna (True, nombre) si tuvo éxito, (False, mensaje_error) si no.
    """
    _asegurar_raiz()
    nombre = nombre.strip()
    if not nombre:
        return False, "El nombre de la carpeta no puede estar vacío."
    ruta = ruta_carpeta(nombre)
    if os.path.exists(ruta):
        return False, f"Ya existe una carpeta llamada '{nombre}'."
    try:
        os.makedirs(ruta)
        return True, nombre
    except Exception as e:
        return False, str(e)


def renombrar_carpeta(nombre_actual: str, nombre_nuevo: str) -> tuple[bool, str]:
    """
    Renombra una carpeta existente.
    Retorna (True, nombre_nuevo) si tuvo éxito, (False, mensaje_error) si no.
    """
    nombre_nuevo = nombre_nuevo.strip()
    if not nombre_nuevo:
        return False, "El nuevo nombre no puede estar vacío."
    ruta_actual = ruta_carpeta(nombre_actual)
    ruta_nueva  = ruta_carpeta(nombre_nuevo)
    if not os.path.exists(ruta_actual):
        return False, f"La carpeta '{nombre_actual}' no existe."
    if os.path.exists(ruta_nueva):
        return False, f"Ya existe una carpeta llamada '{nombre_nuevo}'."
    try:
        os.rename(ruta_actual, ruta_nueva)
        return True, nombre_nuevo
    except Exception as e:
        return False, str(e)


def eliminar_carpeta(nombre: str) -> tuple[bool, str]:
    """
    Elimina una carpeta y todos sus scripts.
    Retorna (True, mensaje) si tuvo éxito, (False, mensaje_error) si no.
    """
    ruta = ruta_carpeta(nombre)
    if not os.path.exists(ruta):
        return False, f"La carpeta '{nombre}' no existe."
    try:
        shutil.rmtree(ruta)
        return True, f"Carpeta '{nombre}' eliminada."
    except Exception as e:
        return False, str(e)


# ── CRUD de scripts ────────────────────────────────────────────────────────────

def guardar_script(carpeta: str, nombre: str, codigo: str) -> tuple[bool, str]:
    """
    Guarda un script .py en la carpeta indicada.
    Si el archivo ya existe, lo sobreescribe.
    Retorna (True, ruta) si tuvo éxito, (False, mensaje_error) si no.
    """
    _asegurar_raiz()
    nombre = nombre.strip()
    if not nombre:
        return False, "El nombre del script no puede estar vacío."
    ruta_c = ruta_carpeta(carpeta)
    if not os.path.exists(ruta_c):
        os.makedirs(ruta_c)
    ruta = ruta_script(carpeta, nombre)
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(codigo)
        return True, ruta
    except Exception as e:
        return False, str(e)


def leer_script(carpeta: str, nombre: str) -> tuple[bool, str]:
    """
    Lee el contenido de un script .py.
    Retorna (True, codigo) si tuvo éxito, (False, mensaje_error) si no.
    """
    ruta = ruta_script(carpeta, nombre)
    if not os.path.exists(ruta):
        return False, f"El script '{nombre}' no existe en '{carpeta}'."
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return True, f.read()
    except Exception as e:
        return False, str(e)


def eliminar_script(carpeta: str, nombre: str) -> tuple[bool, str]:
    """
    Elimina un script .py.
    Retorna (True, mensaje) si tuvo éxito, (False, mensaje_error) si no.
    """
    ruta = ruta_script(carpeta, nombre)
    if not os.path.exists(ruta):
        return False, f"El script '{nombre}' no existe."
    try:
        os.remove(ruta)
        return True, f"Script '{nombre}' eliminado."
    except Exception as e:
        return False, str(e)


def mover_script(carpeta_origen: str, nombre: str, carpeta_destino: str) -> tuple[bool, str]:
    """
    Mueve un script de una carpeta a otra.
    Retorna (True, mensaje) si tuvo éxito, (False, mensaje_error) si no.
    """
    origen  = ruta_script(carpeta_origen, nombre)
    destino = ruta_script(carpeta_destino, nombre)
    if not os.path.exists(origen):
        return False, f"El script '{nombre}' no existe en '{carpeta_origen}'."
    ruta_dest_dir = ruta_carpeta(carpeta_destino)
    if not os.path.exists(ruta_dest_dir):
        return False, f"La carpeta destino '{carpeta_destino}' no existe."
    if os.path.exists(destino):
        return False, f"Ya existe un script llamado '{nombre}' en '{carpeta_destino}'."
    try:
        shutil.move(origen, destino)
        return True, f"Script movido a '{carpeta_destino}'."
    except Exception as e:
        return False, str(e)


# ── Ejecución de scripts ───────────────────────────────────────────────────────

def ejecutar_script(carpeta: str, nombre: str, df: pd.DataFrame) -> tuple[bool, Figure | str]:
    """
    Lee y ejecuta el script con exec(), inyectando el DataFrame como 'df'
    junto con las librerías estándar de análisis.

    Retorna:
        (True,  figura_matplotlib)  si el script generó un gráfico.
        (True,  texto_str)          si el script no generó gráfico pero sí salida de texto.
        (False, mensaje_error)      si ocurrió una excepción durante la ejecución.

    El script generado por el LLM debe usar 'df' como nombre del DataFrame
    y producir una figura Matplotlib activa (plt.gcf()) para que se capture.
    """
    ok, codigo = leer_script(carpeta, nombre)
    if not ok:
        return False, codigo

    # Entorno de ejecución: se inyectan las librerías y el DataFrame
    entorno = {
        "df":  df,
        "pd":  pd,
        "plt": plt,
        "sns": sns,
    }

    # Cerramos cualquier figura previa para que gcf() capture solo la nueva
    plt.close("all")

    try:
        exec(codigo, entorno)  # noqa: S102
    except Exception as e:
        return False, f"Error al ejecutar el script:\n{type(e).__name__}: {e}"

    # Si el script produjo una figura, la capturamos
    fig = plt.gcf()
    if fig.get_axes():
        return True, fig

    # Si no hay figura, devolvemos cualquier variable 'resultado' que el script
    # haya definido, o un mensaje genérico
    resultado = entorno.get("resultado", "El script se ejecutó sin producir un gráfico.")
    return True, str(resultado)
