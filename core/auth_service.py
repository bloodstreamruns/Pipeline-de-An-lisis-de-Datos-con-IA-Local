import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.security import SecurityUtils

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "usuarios.json")


class AuthServiceError(Exception):
    # Excepción personalizada para errores de la capa de datos.
    # Al ser un tipo propio, login.py puede capturarla con `except AuthServiceError`
    # y distinguirla de cualquier otro error inesperado de la aplicación,
    # permitiendo mostrar mensajes específicos al usuario sin exponer
    # detalles internos del sistema.
    pass


class autenticar():
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _cargar_usuarios(self) -> list:
        if not os.path.exists(self.db_path):
            return []
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f).get("usuarios", [])
        except FileNotFoundError:
            # es una condición de carrera: el archivo desapareció entre el exists() y el open()
            return []
        except PermissionError:
            raise AuthServiceError(
                f"Sin permisos de lectura sobre {self.db_path}"
            )
        except UnicodeDecodeError:
            raise AuthServiceError(
                f"El archivo {self.db_path} contiene caracteres no válidos en UTF-8"
            )
        except json.JSONDecodeError:
            raise AuthServiceError(
                f"El archivo {self.db_path} contiene JSON inválido: {e.msg} (línea {e.lineno})"
            )
        except OSError as e:
            raise AuthServiceError(
                f"Error de sistema al acceder a {self.db_path}: {e.strerror}"
            )
    
    def _guardar_usuarios(self, usuarios: list) -> None:
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump({"usuarios": usuarios}, f, indent=4, ensure_ascii=False)