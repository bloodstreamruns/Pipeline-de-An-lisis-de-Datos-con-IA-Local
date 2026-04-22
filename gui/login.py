import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.auth_service import AuthService, AuthServiceError

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
    login_exitoso = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.auth = AuthService()
        self.setWindowTitle("DataPipeline AI")
        self.setFixedSize(420, 520)
        self.setStyleSheet(APP_STYLE)
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 0, 40, 0)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("login-card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(0)

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

        lbl_user = QLabel("Usuario")
        lbl_user.setObjectName("field-label")
        card_layout.addWidget(lbl_user)
        card_layout.addSpacing(4)
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("nombre de usuario")
        card_layout.addWidget(self.input_user)
        card_layout.addSpacing(14)

        lbl_pass = QLabel("Contraseña")
        lbl_pass.setObjectName("field-label")
        card_layout.addWidget(lbl_pass)
        card_layout.addSpacing(4)
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("••••••••")
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.returnPressed.connect(self._procesar_login)
        card_layout.addWidget(self.input_pass)
        card_layout.addSpacing(24)

        btn = QPushButton("Ingresar")
        btn.setObjectName("btn-login")
        btn.setFixedHeight(42)
        btn.clicked.connect(self._procesar_login)
        card_layout.addWidget(btn)

        root.addWidget(card)

    def _procesar_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Campos vacíos", "Ingrese usuario y contraseña.")
            return

        try:
            usuario = self.auth.autenticar(username, password)
        except AuthServiceError as e:
            QMessageBox.critical(self, "Error del sistema", str(e))
            self.input_user.clear()
            self.input_pass.clear()
            self.input_user.setFocus()
            return

        if usuario is None:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas.")
            self.input_pass.clear()
            self.input_pass.setFocus()
            return

        self.login_exitoso.emit(usuario)