import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
import lógica.administrador_autenticacion
from lógica.logica_administrador import AdminLogic

APP_STYLE = """
QWidget { background-color: #141414; color: #E8E8E6; font-family: Arial; font-size: 13px; }
#panel-left { background-color: #141414; border-right: 1px solid #2E2E2E; }
#panel-right { background-color: #1E1E1E; }
#section-label { font-size: 11px; color: #555550; font-weight: bold; letter-spacing: 1px; }
#user-row { background-color: #1E1E1E; border: 1px solid #2E2E2E; border-radius: 8px; }
#avatar { background-color: #2A2A2A; border: 1px solid #3A3A3A; border-radius: 14px; color: #555550; font-size: 11px; font-weight: bold; }
#avatar-admin { background-color: #2E2E2E; border: 1px solid #444441; border-radius: 14px; color: #888780; font-size: 11px; font-weight: bold; }
#pill-admin { background-color: #2E2E2E; color: #888780; border: 1px solid #444441; border-radius: 8px; font-size: 10px; padding: 2px 8px; margin-right: 4px; }
#pill-user { background-color: #1E1E1E; color: #555550; border: 1px solid #2E2E2E; border-radius: 8px; font-size: 10px; padding: 2px 8px; margin-right: 4px; }
#btn-delete { background-color: transparent; border: 1px solid #712B13; border-radius: 4px; color: #D85A30; font-size: 12px; font-weight: bold; padding: 2px 6px; }
#btn-delete:hover { background-color: #2A1510; }
QLineEdit { border: 1px solid #2E2E2E; border-radius: 6px; padding: 6px 10px; font-size: 13px; background-color: #2A2A2A; color: #E8E8E6; }
QLineEdit:focus { border: 1px solid #555550; }
#role-btn { background-color: #2A2A2A; border: 1px solid #2E2E2E; border-radius: 6px; color: #555550; font-size: 12px; padding: 5px 0; }
#role-btn-selected { background-color: #E8E8E6; border: 1px solid #E8E8E6; border-radius: 6px; color: #141414; font-size: 12px; padding: 5px 0; }
#btn-register { background-color: #E8E8E6; color: #141414; border: none; border-radius: 6px; font-size: 13px; font-weight: bold; padding: 8px 0; }
#btn-register:hover { background-color: #CCCCCA; }
#btn-change-pass { background-color: transparent; color: #E8E8E6; border: 1px solid #3A3A3A; border-radius: 6px; font-size: 13px; font-weight: bold; padding: 8px 0; }
#btn-change-pass:hover { background-color: #2A2A2A; }
#divider { background-color: #2E2E2E; }
#info-note { font-size: 11px; color: #444441; }
"""

# TopBar se conserva solo para el modo standalone (__main__).
# Cuando AdminScreen se instancia con embedded=True, no se crea ni agrega.
APP_STYLE_STANDALONE = APP_STYLE + """
#topbar { background-color: #1E1E1E; border-bottom: 1px solid #2E2E2E; }
#topbar-logo { font-size: 14px; font-weight: bold; color: #E8E8E6; }
#nav-item { color: #555550; font-size: 13px; background: transparent; border: none; padding: 0 6px; }
#nav-item-active { color: #E8E8E6; font-size: 13px; font-weight: bold; background: transparent; border: none; border-bottom: 2px solid #E8E8E6; padding: 0 6px; }
#session-badge { font-size: 11px; color: #555550; background-color: #1E1E1E; border: 1px solid #2E2E2E; border-radius: 4px; padding: 2px 8px; }
"""


class TopBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("topbar")
        self.setFixedHeight(45)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(20)
        logo = QLabel("DataPipeline AI")
        logo.setObjectName("topbar-logo")
        layout.addWidget(logo)
        self.btn1 = QPushButton("Consulta");       self.btn1.setObjectName("nav-item")
        self.btn2 = QPushButton("Scripts");        self.btn2.setObjectName("nav-item")
        self.btn3 = QPushButton("Administración"); self.btn3.setObjectName("nav-item-active")
        layout.addWidget(self.btn1); layout.addWidget(self.btn2); layout.addWidget(self.btn3)
        layout.addStretch()
        badge = QLabel("sesión: admin")
        badge.setObjectName("session-badge")
        layout.addWidget(badge)


class UserRow(QFrame):
    def __init__(self, data, logic, on_select=None):
        super().__init__()
        self.setObjectName("user-row"); self.setFixedHeight(52)
        self._username = data["username"]
        self._on_select = on_select
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QHBoxLayout(self); layout.setContentsMargins(10, 0, 10, 0)
        is_admin = data["role"] == "admin"
        avatar = QLabel(data.get("initials", "??"))
        avatar.setObjectName("avatar-admin" if is_admin else "avatar")
        avatar.setFixedSize(28, 28); avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(avatar)
        info = QVBoxLayout()
        info.addWidget(QLabel(data["username"]))
        lbl_rol = QLabel("Administrador del sistema" if is_admin else "Usuario estándar")
        lbl_rol.setStyleSheet("font-size: 11px; color: #B4B2A9;")
        info.addWidget(lbl_rol)
        layout.addLayout(info); layout.addStretch()
        pill = QLabel(data["role"])
        pill.setObjectName("pill-admin" if is_admin else "pill-user")
        pill.setFixedHeight(18)
        layout.addWidget(pill)
        if not is_admin:
            btn = QPushButton("✕")
            btn.setObjectName("btn-delete")
            btn.setFixedSize(24, 24)
            btn.clicked.connect(lambda: logic.eliminar_usuario(data["username"]))
            layout.addWidget(btn)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._on_select:
            self._on_select(self._username)
        super().mousePressEvent(event)


class LeftPanel(QFrame):
    def __init__(self, logic):
        super().__init__()
        self.setObjectName("panel-left"); self.logic = logic
        self._on_select = None
        layout = QVBoxLayout(self)
        lbl_section = QLabel("USUARIOS REGISTRADOS")
        lbl_section.setObjectName("section-label")
        layout.addWidget(lbl_section)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.container = QWidget(); self.rows_layout = QVBoxLayout(self.container)
        self.rows_layout.setSpacing(6); self.rows_layout.addStretch()
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        self.refrescar_lista()

    def set_callback_seleccion(self, callback):
        self._on_select = callback

    def refrescar_lista(self):
        while self.rows_layout.count() > 1:
            item = self.rows_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for u in lógica.administrador_autenticacion.obtener_lista_usuarios():
            self.rows_layout.insertWidget(
                self.rows_layout.count() - 1,
                UserRow(u, self.logic, on_select=self._on_select)
            )


def _divider():
    d = QFrame()
    d.setObjectName("divider")
    d.setFrameShape(QFrame.Shape.HLine)
    d.setFixedHeight(1)
    return d

def _field_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet("font-size: 11px; color: #888780; margin-bottom: 4px;")
    return lbl


class RightPanel(QFrame):
    def __init__(self, logic):
        super().__init__()
        self.setObjectName("panel-right"); self.setFixedWidth(260)
        layout = QVBoxLayout(self); layout.setContentsMargins(16, 16, 16, 16); layout.setSpacing(0)

        lbl_reg = QLabel("REGISTRAR USUARIO")
        lbl_reg.setObjectName("section-label")
        layout.addWidget(lbl_reg)
        layout.addSpacing(10)

        layout.addWidget(_field_label("Nombre de usuario"))
        self.u_input = QLineEdit(); self.u_input.setPlaceholderText("nombre_usuario")
        layout.addWidget(self.u_input); layout.addSpacing(10)

        layout.addWidget(_field_label("Contraseña"))
        self.p_input = QLineEdit(); self.p_input.setPlaceholderText("••••••••")
        self.p_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.p_input); layout.addSpacing(10)

        layout.addWidget(_field_label("Rol"))
        row = QHBoxLayout(); row.setSpacing(6)
        self.b_user  = QPushButton("Usuario")
        self.b_user.setObjectName("role-btn-selected")
        self.b_admin = QPushButton("Admin")
        self.b_admin.setObjectName("role-btn")
        self.b_user.clicked.connect(lambda: self._set_role("usuario"))
        self.b_admin.clicked.connect(lambda: self._set_role("admin"))
        row.addWidget(self.b_user); row.addWidget(self.b_admin)
        layout.addLayout(row); layout.addSpacing(14)

        btn_reg = QPushButton("Registrar")
        btn_reg.setObjectName("btn-register")
        btn_reg.setFixedHeight(36)
        btn_reg.clicked.connect(logic.registrar_usuario)
        layout.addWidget(btn_reg)

        layout.addSpacing(14)
        layout.addWidget(_divider())
        layout.addSpacing(14)

        lbl_cp = QLabel("CAMBIAR CONTRASEÑA")
        lbl_cp.setObjectName("section-label")
        layout.addWidget(lbl_cp)
        layout.addSpacing(10)

        layout.addWidget(_field_label("Usuario"))
        self.cp_user_input = QLineEdit(); self.cp_user_input.setPlaceholderText("nombre_usuario")
        layout.addWidget(self.cp_user_input); layout.addSpacing(10)

        layout.addWidget(_field_label("Nueva contraseña"))
        self.cp_new_input = QLineEdit(); self.cp_new_input.setPlaceholderText("••••••••")
        self.cp_new_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.cp_new_input); layout.addSpacing(10)

        layout.addWidget(_field_label("Confirmar contraseña"))
        self.cp_confirm_input = QLineEdit(); self.cp_confirm_input.setPlaceholderText("••••••••")
        self.cp_confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.cp_confirm_input); layout.addSpacing(14)

        btn_cp = QPushButton("Cambiar contraseña")
        btn_cp.setObjectName("btn-change-pass")
        btn_cp.setFixedHeight(36)
        btn_cp.clicked.connect(logic.cambiar_contrasena)
        layout.addWidget(btn_cp)

        layout.addSpacing(14)
        layout.addWidget(_divider())
        layout.addSpacing(10)
        note = QLabel("La cuenta del administrador principal no puede eliminarse desde esta pantalla.")
        note.setObjectName("info-note")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()

    def seleccionar_usuario(self, username):
        self.cp_user_input.setText(username)
        self.cp_new_input.setFocus()

    def _set_role(self, r):
        self.b_user.setObjectName("role-btn-selected" if r == "usuario" else "role-btn")
        self.b_admin.setObjectName("role-btn-selected" if r == "admin" else "role-btn")
        self.b_user.setStyle(self.b_user.style()); self.b_admin.setStyle(self.b_admin.style())


class AdminScreen(QWidget):
    def __init__(self, embedded: bool = False):
        super().__init__()
        self.setWindowTitle("DataPipeline AI — Administración")
        self.setMinimumSize(820, 500)
        self.logic = AdminLogic(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # TopBar solo en modo standalone; embebida, la navegación la maneja Consulta
        if not embedded:
            self.setStyleSheet(APP_STYLE_STANDALONE)
            self.topbar = TopBar()
            root.addWidget(self.topbar)
        else:
            self.setStyleSheet(APP_STYLE)
            self.topbar = None  # no existe en modo embebido

        content = QHBoxLayout()
        self.left_panel  = LeftPanel(self.logic)
        self.right_panel = RightPanel(self.logic)
        self.left_panel.set_callback_seleccion(self.right_panel.seleccionar_usuario)
        content.addWidget(self.left_panel)
        content.addWidget(self.right_panel)
        root.addLayout(content)

    def set_nav_callbacks(self, consulta_fn, scripts_fn, admin_fn):
        # Solo tiene efecto en modo standalone (topbar existe)
        if self.topbar:
            self.topbar.btn1.clicked.connect(consulta_fn)
            self.topbar.btn2.clicked.connect(scripts_fn)
            self.topbar.btn3.clicked.connect(admin_fn)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminScreen()   # standalone: muestra topbar
    window.show()
    exit_code = app.exec()
    sys.exit(exit_code)