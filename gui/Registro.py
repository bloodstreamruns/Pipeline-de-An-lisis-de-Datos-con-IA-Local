import sys
import os
import json
import hashlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "usuarios.json")

APP_STYLE = """
QWidget {
    background-color: #141414;
    color: #E8E8E6;
    font-family: Arial;
    font-size: 13px;
}
#login-card {
    background-color: #1E1E1E;
    border: 1px solid #2E2E2E;
    border-radius: 12px;
}
#app-title {
    font-size: 11px;
    color: #555550;
    letter-spacing: 2px;
}
#app-name {
    font-size: 22px;
    font-weight: bold;
    color: #E8E8E6;
}
#field-label {
    font-size: 11px;
    color: #888780;
}
QLineEdit {
    border: 1px solid #2E2E2E;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 13px;
    background-color: #2A2A2A;
    color: #E8E8E6;
}
QLineEdit:focus {
    border: 1px solid #555550;
}
#btn-login {
    background-color: #E8E8E6;
    color: #141414;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 10px 0;
}
#btn-login:hover {
    background-color: #CCCCCA;
}
"""


class LoginScreen(QWidget):
    # Señal emitida al autenticarse correctamente.
    # Transporta el username y el rol para que app.py
    # pueda decidir qué pantalla mostrar a continuación.
    login_exitoso = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataPipeline AI")
        self.setFixedSize(420, 520)
        self.setStyleSheet(APP_STYLE)
        self._init_ui()

    def _init_ui(self):
        # Layout raíz: centra la tarjeta vertical y horizontalmente
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 0, 40, 0)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("login-card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(0)

        # Encabezado
        title = QLabel("SISTEMA DE ANÁLISIS")
        title.setObjectName("app-title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)
        card_layout.addSpacing(6)

        name = QLabel("DataPipeline AI")
        name.setObjectName("app-name")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(name)
        card_layout.addSpacing(28)

        # Campo usuario
        lbl_user = QLabel("Usuario")
        lbl_user.setObjectName("field-label")
        card_layout.addWidget(lbl_user)
        card_layout.addSpacing(4)
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("nombre de usuario")
        card_layout.addWidget(self.input_user)
        card_layout.addSpacing(14)

        # Campo contraseña
        lbl_pass = QLabel("Contraseña")
        lbl_pass.setObjectName("field-label")
        card_layout.addWidget(lbl_pass)
        card_layout.addSpacing(4)
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("••••••••")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        # Enter en el campo de contraseña dispara el login
        self.input_pass.returnPressed.connect(self._procesar_login)
        card_layout.addWidget(self.input_pass)
        card_layout.addSpacing(24)

        # Botón ingresar
        btn = QPushButton("Ingresar")
        btn.setObjectName("btn-login")
        btn.setFixedHeight(42)
        btn.clicked.connect(self._procesar_login)
        card_layout.addWidget(btn)

        root.addWidget(card)

    # ── Lógica de autenticación ────────────────────────────────────────────────

    def _obtener_usuarios(self):
        if not os.path.exists(DB_PATH):
            return []
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("usuarios", [])
        except Exception:
            return []

    def _hash(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _procesar_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Campos vacíos", "Ingrese usuario y contraseña.")
            return

        usuarios = self._obtener_usuarios()

        # Busca el usuario ignorando mayúsculas/minúsculas
        usuario = next(
            (u for u in usuarios if u.get("username", "").lower() == username.lower()),
            None
        )

        if usuario is None:
            QMessageBox.critical(self, "Error", "El usuario no existe.")
            return

        # Acepta contraseña en texto plano (formato legado) o hasheada
        password_almacenada = usuario.get("password", "")
        es_valida = (
            password_almacenada == password or
            password_almacenada == self._hash(password)
        )

        if not es_valida:
            QMessageBox.critical(self, "Error", "Contraseña incorrecta.")
            self.input_pass.clear()
            self.input_pass.setFocus()
            return

        # Autenticación exitosa: emite señal con username y rol
        self.login_exitoso.emit(username, usuario.get("role", "usuario"))