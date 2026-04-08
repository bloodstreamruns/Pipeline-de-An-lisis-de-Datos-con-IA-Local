import requests
from PyQt6.QtCore import QThread, pyqtSignal

OLLAMA_URL   = "http://localhost:11434/api/generate"
MODELO       = "phi4"
TIMEOUT_SEG  = 120   # Phi-4 puede tardar en responder en hardware de consumo


# ── Cliente HTTP síncrono ──────────────────────────────────────────────────────

def llamar_ollama(prompt: str) -> tuple[bool, str]:
    """
    Envía el prompt a Phi-4 vía la API REST local de Ollama.

    Returns
    -------
    (True,  codigo_generado)  si la llamada tuvo éxito.
    (False, mensaje_error)    si hubo un error de conexión o respuesta inesperada.
    """
    payload = {
        "model":  MODELO,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SEG)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        return False, (
            "No se pudo conectar con Ollama.\n"
            "Asegúrese de que el servicio esté corriendo: ejecute 'ollama serve' en la terminal."
        )
    except requests.exceptions.Timeout:
        return False, (
            f"La solicitud superó el tiempo límite de {TIMEOUT_SEG} segundos.\n"
            "El modelo puede estar sobrecargado. Intente de nuevo."
        )
    except requests.exceptions.HTTPError as e:
        return False, f"Error HTTP {e.response.status_code}: {e}"
    except Exception as e:
        return False, f"Error inesperado: {e}"

    try:
        codigo = response.json().get("response", "").strip()
    except Exception:
        return False, "La respuesta de Ollama no pudo ser procesada como JSON."

    if not codigo:
        return False, "Ollama devolvió una respuesta vacía."

    # Limpiar bloques de markdown si el modelo los incluyó a pesar de las instrucciones
    codigo = _limpiar_markdown(codigo)

    return True, codigo


def _limpiar_markdown(texto: str) -> str:
    """
    Elimina bloques de markdown (```python ... ``` o ``` ... ```) que el modelo
    puede incluir aunque el prompt lo prohíba explícitamente.
    """
    lineas = texto.splitlines()
    resultado = []
    dentro_bloque = False

    for linea in lineas:
        stripped = linea.strip()
        if stripped.startswith("```"):
            dentro_bloque = not dentro_bloque
            continue
        if not dentro_bloque:
            resultado.append(linea)

    # Si el modelo no usó bloques, devolver el texto original sin modificar
    texto_limpio = "\n".join(resultado).strip()
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
        ok, resultado = llamar_ollama(self.prompt)
        if ok:
            self.exito.emit(resultado)
        else:
            self.error.emit(resultado)
                      