import logging
import requests
from PyQt6.QtCore import QThread, pyqtSignal

OLLAMA_URL   = "http://localhost:11434/api/generate"
MODELO       = "phi4"
TIMEOUT_SEG  = 120   # Phi-4 puede tardar en responder en hardware de consumo


# ── Cliente HTTP síncrono ──────────────────────────────────────────────────────

def llamar_ollama(prompt: str) -> tuple[bool, str, str]:
    """
    Envía el prompt a Phi-4 vía la API REST local de Ollama.

    Returns
    -------
    (True,  nombre,         codigo)  si la llamada tuvo éxito.
    (False, mensaje_error,  "")      si hubo un error de conexión o respuesta inesperada.
    """
    payload = {
        "model":  MODELO,
        "prompt": prompt,
        "stream": False,
    }

    logging.info("Enviando prompt a Ollama. Largo prompt: %d", len(prompt))
    logging.debug("Prompt: %s", prompt[:400])

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SEG)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        return False, (
            "No se pudo conectar con Ollama.\n"
            "Asegúrese de que el servicio esté corriendo: ejecute 'ollama serve' en la terminal."
        ), ""
    except requests.exceptions.Timeout:
        return False, (
            f"La solicitud superó el tiempo límite de {TIMEOUT_SEG} segundos.\n"
            "El modelo puede estar sobrecargado. Intente de nuevo."
        ), ""
    except requests.exceptions.HTTPError as e:
        return False, f"Error HTTP {e.response.status_code}: {e}", ""
    except Exception as e:
        return False, f"Error inesperado: {e}", ""

    logging.info("Ollama respondió status %s", response.status_code)
    logging.debug("Respuesta cruda de Ollama (completa): %s", response.text)

    try:
        codigo = response.json().get("response", "").strip()
    except Exception:
        return False, "La respuesta de Ollama no pudo ser procesada como JSON.", ""

    if not codigo:
        return False, "Ollama devolvió una respuesta vacía.", ""

    logging.debug("Respuesta ANTES de parsear (%d chars):\n%s", len(codigo), codigo)

    # Parsear nombre y código de la respuesta estructurada
    nombre, codigo = _parsear_respuesta(codigo)

    # Limpiar bloques de markdown si el modelo los incluyó a pesar de las instrucciones
    codigo = _limpiar_markdown(codigo)

    logging.debug("Nombre: %s | Código (%d chars):\n%s", nombre, len(codigo), codigo)

    return True, nombre, codigo


def _parsear_respuesta(texto: str) -> tuple[str, str]:
    """
    Parsea la respuesta estructurada del modelo, que debe tener el formato:

        NOMBRE: nombre_en_snake_case
        CODIGO:
        <código Python>

    Retorna (nombre, codigo). Si el modelo no respetó el formato, devuelve
    un nombre genérico basado en timestamp y el texto completo como código.
    """
    import re
    from datetime import datetime

    nombre_fallback = f"consulta_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Buscar NOMBRE: ... (puede tener espacios, mayúsculas/minúsculas)
    match_nombre = re.search(r'(?i)^nombre\s*:\s*(.+)$', texto, re.MULTILINE)
    # Buscar CODIGO: y tomar todo lo que sigue
    match_codigo = re.search(r'(?i)^codigo\s*:\s*\n([\s\S]+)', texto, re.MULTILINE)

    if match_nombre and match_codigo:
        nombre = match_nombre.group(1).strip()
        # Sanitizar: solo letras, números y guiones bajos
        nombre = re.sub(r'[^a-zA-Z0-9_]', '_', nombre)
        nombre = re.sub(r'_+', '_', nombre).strip('_')
        nombre = nombre[:60] if nombre else nombre_fallback
        codigo = match_codigo.group(1).strip()
        return nombre, codigo

    # Fallback: el modelo no respetó el formato, usar texto completo como código
    logging.warning("La respuesta no tiene el formato NOMBRE/CODIGO esperado. Usando fallback.")
    return nombre_fallback, texto.strip()


def _limpiar_markdown(texto: str) -> str:
    """
    Elimina bloques de markdown (```python ... ``` o ``` ... ```) que el modelo
    puede incluir aunque el prompt lo prohíba explícitamente.

    Solo actúa si detecta al menos un bloque markdown real (apertura + cierre).
    Si no hay bloques, devuelve el texto sin modificar para evitar falsos positivos
    donde una línea con ``` dentro del código generado active el toggle y descarte
    el resto del script.
    """
    lineas = texto.splitlines()

    # Detectar si hay bloques markdown reales (al menos una apertura y un cierre)
    marcadores = [i for i, l in enumerate(lineas) if l.strip().startswith("```")]
    if len(marcadores) < 2:
        # Sin bloques completos: no tocar el texto
        return texto.strip()

    # Hay bloques: extraer solo el contenido dentro de ellos
    resultado = []
    dentro_bloque = False

    for linea in lineas:
        stripped = linea.strip()
        if stripped.startswith("```"):
            dentro_bloque = not dentro_bloque
            continue
        if dentro_bloque:
            resultado.append(linea)

    texto_limpio = "\n".join(resultado).strip()

    # Fallback: si la extracción resultó vacía (bloques vacíos), devolver original
    return texto_limpio if texto_limpio else texto.strip()


# ── Worker QThread ─────────────────────────────────────────────────────────────

class OllamaWorker(QThread):
    """
    Ejecuta la llamada a Ollama en un hilo secundario para no bloquear
    la interfaz durante la inferencia.

    Señales
    -------
    exito(str)  : emitida con el código generado si la llamada tuvo éxito.
    error(str)  : emitida con el mensaje de error si la llamada falló.
    """

    exito = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            ok, nombre_o_error, codigo = llamar_ollama(self.prompt)
            if ok:
                if not codigo.strip():
                    self.error.emit("Ollama devolvió una respuesta vacía.")
                else:
                    # Emitir "nombre||codigo" para que el receptor los separe
                    self.exito.emit(f"{nombre_o_error}||{codigo}")
            else:
                self.error.emit(nombre_o_error)
        except Exception as e:
            self.error.emit(f"Error inesperado en el worker: {type(e).__name__}: {e}")