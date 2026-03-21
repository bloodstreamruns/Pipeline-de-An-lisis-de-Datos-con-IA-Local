#Esta es la interfaz para la administración de usuarios. Crea, modifica y elimina los usuarios. 
#Sólo un usuario administrador puede entrar a ella. Se debe poder ingresar a ella por medio del menú de la barra superior.

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QFrame, QButtonGroup,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

# ── Estilos ────────────────────────────────────────────────────────────────────

APP_STYLE = """
QWidget {
    background-color: #141414;
    color: #E8E8E6;
    font-family: Arial;
    font-size: 13px;
}

/* Barra superior */
#topbar {
    background-color: #1E1E1E;
    border-bottom: 1px solid #2E2E2E;
}

#topbar-logo {
    font-size: 14px;
    font-weight: bold;
    color: #E8E8E6;
}

#nav-item {
    color: #555550;
    font-size: 13px;
    background: transparent;
    border: none;
    padding: 0 6px;
}

#nav-item-active {
    color: #E8E8E6;
    font-size: 13px;
    font-weight: bold;
    background: transparent;
    border: none;
    border-bottom: 2px solid #E8E8E6;
    padding: 0 6px;
}

#session-badge {
    font-size: 11px;
    color: #555550;
    background-color: #1E1E1E;
    border: 1px solid #2E2E2E;
    border-radius: 4px;
    padding: 2px 8px;
}

/* Panel izquierdo */
#panel-left {
    background-color: #141414;
    border-right: 1px solid #2E2E2E;
}

/* Panel derecho */
#panel-right {
    background-color: #1E1E1E;
}

/* Etiquetas de sección */
#section-label {
    font-size: 11px;
    color: #555550;
    font-weight: bold;
    letter-spacing: 1px;
}

/* Fila de usuario */
#user-row {
    background-color: #1E1E1E;
    border: 1px solid #2E2E2E;
    border-radius: 8px;
}

/* Avatar */
#avatar {
    background-color: #2A2A2A;
    border: 1px solid #3A3A3A;
    border-radius: 14px;
    color: #555550;
    font-size: 11px;
    font-weight: bold;
}

#avatar-admin {
    background-color: #2E2E2E;
    border: 1px solid #444441;
    border-radius: 14px;
    color: #888780;
    font-size: 11px;
    font-weight: bold;
}

/* Pill de rol */
#pill-admin {
    background-color: #2E2E2E;
    color: #888780;
    border: 1px solid #444441;
    border-radius: 8px;
    font-size: 10px;
    padding: 2px 8px;
}

#pill-user {
    background-color: #1E1E1E;
    color: #555550;
    border: 1px solid #2E2E2E;
    border-radius: 8px;
    font-size: 10px;
    padding: 2px 8px;
}

/* Botón eliminar */
#btn-delete {
    background-color: transparent;
    border: 1px solid #712B13;
    border-radius: 4px;
    color: #D85A30;
    font-size: 12px;
    font-weight: bold;
    padding: 2px 6px;
}

#btn-delete:hover {
    background-color: #2A1510;
}

/* Campos del formulario */
QLineEdit {
    border: 1px solid #2E2E2E;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    background-color: #2A2A2A;
    color: #E8E8E6;
}

QLineEdit:focus {
    border: 1px solid #555550;
}

/* Selector de rol */
#role-btn {
    background-color: #2A2A2A;
    border: 1px solid #2E2E2E;
    border-radius: 6px;
    color: #555550;
    font-size: 12px;
    padding: 5px 0;
}

#role-btn:hover {
    background-color: #333333;
}

#role-btn-selected {
    background-color: #E8E8E6;
    border: 1px solid #E8E8E6;
    border-radius: 6px;
    color: #141414;
    font-size: 12px;
    padding: 5px 0;
}

/* Botón registrar */
#btn-register {
    background-color: #E8E8E6;
    color: #141414;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 8px 0;
}

#btn-register:hover {
    background-color: #CCCCCA;
}

/* Separador */
#divider {
    background-color: #2E2E2E;
}

/* Nota informativa */
#info-note {
    font-size: 11px;
    color: #444441;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    width: 6px;
    background: transparent;
}

QScrollBar::handle:vertical {
    background: #3A3A3A;
    border-radius: 3px;
}
"""

# ── Componentes ────────────────────────────────────────────────────────────────

class UserRow(QFrame):
    """Fila individual de usuario en el listado."""

    def __init__(self, initials: str, username: str, role: str, is_admin: bool = False):
        super().__init__()
        self.setObjectName("user-row")
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        # Avatar
        avatar = QLabel(initials)
        avatar.setObjectName("avatar-admin" if is_admin else "avatar")
        avatar.setFixedSize(QSize(28, 28))
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(avatar)

        # Nombre y rol
        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)
        info_layout.setContentsMargins(0, 0, 0, 0)

        name_label = QLabel(username)
        name_label.setObjectName("user-name")
        role_label = QLabel("Administrador del sistema" if is_admin else "Usuario estándar")
        role_label.setObjectName("user-role")
        role_label.setStyleSheet("font-size: 11px; color: #B4B2A9;")

        info_layout.addWidget(name_label)
        info_layout.addWidget(role_label)
        layout.addLayout(info_layout)
        layout.addStretch()

        # Pill de rol
        pill = QLabel(role)
        pill.setObjectName("pill-admin" if is_admin else "pill-user")
        pill.setFixedHeight(20)
        layout.addWidget(pill)

        # Botón eliminar (solo usuarios no admin)
        if not is_admin:
            delete_btn = QPushButton("✕")
            delete_btn.setObjectName("btn-delete")
            delete_btn.setFixedSize(QSize(24, 24))
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(delete_btn)


class TopBar(QFrame):
    """Barra de navegación superior."""

    def __init__(self):
        super().__init__()
        self.setObjectName("topbar")
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(20)

        logo = QLabel("DataPipeline AI")
        logo.setObjectName("topbar-logo")
        layout.addWidget(logo)

        for name, active in [("Consulta", False), ("Scripts", False), ("Administración", True)]:
            btn = QLabel(name)
            btn.setObjectName("nav-item-active" if active else "nav-item")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)

        layout.addStretch()

        session_badge = QLabel("sesión: admin")
        session_badge.setObjectName("session-badge")
        layout.addWidget(session_badge)


class LeftPanel(QFrame):
    """Panel izquierdo: listado de usuarios."""

    USERS = [
        ("AD", "admin",    "admin",   True),
        ("JM", "jmartinez","usuario", False),
        ("RP", "rperez",   "usuario", False),
        ("CL", "clopez",   "usuario", False),
    ]

    def __init__(self):
        super().__init__()
        self.setObjectName("panel-left")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(10)

        section_label = QLabel("USUARIOS REGISTRADOS")
        section_label.setObjectName("section-label")
        outer.addWidget(section_label)

        # Área desplazable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        rows_layout = QVBoxLayout(container)
        rows_layout.setContentsMargins(0, 0, 0, 0)
        rows_layout.setSpacing(6)

        for initials, username, role, is_admin in self.USERS:
            rows_layout.addWidget(UserRow(initials, username, role, is_admin))

        rows_layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)


class RightPanel(QFrame):
    """Panel derecho: formulario de registro."""

    def __init__(self):
        super().__init__()
        self.setObjectName("panel-right")
        self.setFixedWidth(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        # Título
        section_label = QLabel("REGISTRAR USUARIO")
        section_label.setObjectName("section-label")
        layout.addWidget(section_label)
        layout.addSpacing(10)

        # Campo: nombre
        lbl_user = QLabel("Nombre de usuario")
        lbl_user.setStyleSheet("font-size: 11px; color: #888780; margin-bottom: 4px;")
        layout.addWidget(lbl_user)
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("nombre_usuario")
        layout.addWidget(self.input_username)
        layout.addSpacing(10)

        # Campo: contraseña
        lbl_pass = QLabel("Contraseña")
        lbl_pass.setStyleSheet("font-size: 11px; color: #888780; margin-bottom: 4px;")
        layout.addWidget(lbl_pass)
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("••••••••")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input_password)
        layout.addSpacing(10)

        # Selector de rol
        lbl_role = QLabel("Rol")
        lbl_role.setStyleSheet("font-size: 11px; color: #888780; margin-bottom: 4px;")
        layout.addWidget(lbl_role)

        role_row = QHBoxLayout()
        role_row.setSpacing(6)
        role_row.setContentsMargins(0, 0, 0, 0)

        self.btn_role_user = QPushButton("Usuario")
        self.btn_role_user.setObjectName("role-btn-selected")
        self.btn_role_user.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_role_user.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.btn_role_admin = QPushButton("Admin")
        self.btn_role_admin.setObjectName("role-btn")
        self.btn_role_admin.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_role_admin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.btn_role_user.clicked.connect(lambda: self._select_role("usuario"))
        self.btn_role_admin.clicked.connect(lambda: self._select_role("admin"))

        role_row.addWidget(self.btn_role_user)
        role_row.addWidget(self.btn_role_admin)
        layout.addLayout(role_row)
        layout.addSpacing(14)

        # Botón registrar
        btn_register = QPushButton("Registrar")
        btn_register.setObjectName("btn-register")
        btn_register.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_register.setFixedHeight(36)
        layout.addWidget(btn_register)

        # Separador
        layout.addSpacing(14)
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        layout.addSpacing(10)

        # Nota
        note = QLabel("La cuenta del administrador principal no puede eliminarse desde esta pantalla.")
        note.setObjectName("info-note")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addStretch()

    def _select_role(self, role: str):
        if role == "usuario":
            self.btn_role_user.setObjectName("role-btn-selected")
            self.btn_role_admin.setObjectName("role-btn")
        else:
            self.btn_role_admin.setObjectName("role-btn-selected")
            self.btn_role_user.setObjectName("role-btn")
        # Re-aplicar estilo para que Qt recargue el objectName
        self.btn_role_user.setStyle(self.btn_role_user.style())
        self.btn_role_admin.setStyle(self.btn_role_admin.style())


# ── Pantalla principal ─────────────────────────────────────────────────────────

class AdminScreen(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataPipeline AI — Administración")
        self.setMinimumSize(820, 500)
        self.setStyleSheet(APP_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Barra superior
        root.addWidget(TopBar())

        # Contenido: dos paneles
        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)

        content.addWidget(LeftPanel())
        content.addWidget(RightPanel())

        root.addLayout(content)


# ── Entrada ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminScreen()
    window.show()
    sys.exit(app.exec())
