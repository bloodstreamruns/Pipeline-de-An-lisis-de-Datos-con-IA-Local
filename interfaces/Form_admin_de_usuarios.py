import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QSize
import administrador_autenticacion
from logica_administrador import AdminLogic

APP_STYLE = """
QWidget { background-color: #141414; color: #E8E8E6; font-family: Arial; font-size: 13px; }
#topbar { background-color: #1E1E1E; border-bottom: 1px solid #2E2E2E; }
#topbar-logo { font-size: 14px; font-weight: bold; color: #E8E8E6; }
#nav-item { color: #555550; font-size: 13px; background: transparent; border: none; padding: 0 6px; }
#nav-item-active { color: #E8E8E6; font-size: 13px; font-weight: bold; background: transparent; border: none; border-bottom: 2px solid #E8E8E6; padding: 0 6px; }
#session-badge { font-size: 11px; color: #555550; background-color: #1E1E1E; border: 1px solid #2E2E2E; border-radius: 4px; padding: 2px 8px; }
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
#divider { background-color: #2E2E2E; }
#info-note { font-size: 11px; color: #444441; }
"""

# Pantalla de administración de usuarios para la aplicación DataPipeline AI. Permite crear y eliminar usuarios, asignar roles y visualizar la lista de usuarios registrados.
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

        # Botones de navegación
        self.btn1 = QPushButton("Consulta"); self.btn1.setObjectName("nav-item")
        self.btn2 = QPushButton("Scripts"); self.btn2.setObjectName("nav-item")
        self.btn3 = QPushButton("Administración"); self.btn3.setObjectName("nav-item-active")

        
        layout.addWidget(self.btn1); layout.addWidget(self.btn2); layout.addWidget(self.btn3)
        layout.addStretch()
        layout.addWidget(QLabel("sesión: admin", objectName="session-badge"))

# Cada fila de usuario en la lista de la izquierda. Muestra el avatar, nombre, rol y un botón de eliminación si no es admin.
class UserRow(QFrame):
    def __init__(self, data, logic):
        super().__init__()
        self.setObjectName("user-row"); self.setFixedHeight(52)
        layout = QHBoxLayout(self); layout.setContentsMargins(10, 0, 10, 0)
        
        # Avatar con iniciales y estilo según rol
        is_admin = data['role'] == "admin"
        avatar = QLabel(data.get('initials', '??'), objectName="avatar-admin" if is_admin else "avatar")
        avatar.setFixedSize(28, 28); avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(avatar)


        # Información de usuario (nombre y descripción del rol)
        info = QVBoxLayout()
        info.addWidget(QLabel(data['username']))
        info.addWidget(QLabel("Administrador del sistema" if is_admin else "Usuario estándar", styleSheet="font-size: 11px; color: #B4B2A9;"))
        layout.addLayout(info); layout.addStretch()

        # Recuadro de Rol (ajustado para ser pequeño)
        pill = QLabel(data['role'], objectName="pill-admin" if is_admin else "pill-user")
        pill.setFixedHeight(18) # Forzamos una altura baja para que sea fino
        layout.addWidget(pill)

        # Botón de eliminación solo para usuarios que no son admin
        if not is_admin:
            btn = QPushButton("✕", objectName="btn-delete"); btn.setFixedSize(24, 24)
            btn.clicked.connect(lambda: logic.eliminar_usuario(data['username']))
            layout.addWidget(btn)

# Panel izquierdo que muestra la lista de usuarios registrados. Permite refrescar la lista después de cambios.
class LeftPanel(QFrame):
    def __init__(self, logic):
        super().__init__()
        self.setObjectName("panel-left"); self.logic = logic
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("USUARIOS REGISTRADOS", objectName="section-label"))
        
        # Área scrollable para la lista de usuarios
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.container = QWidget(); self.rows_layout = QVBoxLayout(self.container)
        self.rows_layout.setSpacing(6); self.rows_layout.addStretch()
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)
        self.refrescar_lista()

    # Función para refrescar la lista de usuarios en el panel izquierdo. Limpia la lista actual y la vuelve a poblar con los datos actualizados desde el archivo JSON.
    def refrescar_lista(self):
        while self.rows_layout.count() > 1:
            item = self.rows_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for u in administrador_autenticacion.obtener_lista_usuarios():
            self.rows_layout.insertWidget(self.rows_layout.count()-1, UserRow(u, self.logic))

# Panel derecho con el formulario para registrar un nuevo usuario. Permite ingresar nombre, contraseña y seleccionar el rol antes de registrar.
class RightPanel(QFrame):
    def __init__(self, logic):
        super().__init__()
        self.setObjectName("panel-right"); self.setFixedWidth(260)
        layout = QVBoxLayout(self); layout.setContentsMargins(16, 16, 16, 16); layout.setSpacing(0)

        layout.addWidget(QLabel("REGISTRAR USUARIO", objectName="section-label"))
        layout.addSpacing(10)

        layout.addWidget(QLabel("Nombre de usuario", styleSheet="font-size: 11px; color: #888780; margin-bottom: 4px;"))
        self.u_input = QLineEdit(); self.u_input.setPlaceholderText("nombre_usuario")
        layout.addWidget(self.u_input); layout.addSpacing(10)

        layout.addWidget(QLabel("Contraseña", styleSheet="font-size: 11px; color: #888780; margin-bottom: 4px;"))
        self.p_input = QLineEdit(); self.p_input.setPlaceholderText("••••••••"); self.p_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.p_input); layout.addSpacing(10)

# Selección de rol con dos botones. El botón seleccionado indica el rol que se asignará al nuevo usuario. Por defecto, "Usuario" está seleccionado.
        layout.addWidget(QLabel("Rol", styleSheet="font-size: 11px; color: #888780; margin-bottom: 4px;"))
        row = QHBoxLayout(); row.setSpacing(6)
        self.b_user = QPushButton("Usuario", objectName="role-btn-selected")
        self.b_admin = QPushButton("Admin", objectName="role-btn")
        self.b_user.clicked.connect(lambda: self._set_role("usuario"))
        self.b_admin.clicked.connect(lambda: self._set_role("admin"))
        row.addWidget(self.b_user); row.addWidget(self.b_admin)
        layout.addLayout(row); layout.addSpacing(14)

        btn_reg = QPushButton("Registrar", objectName="btn-register"); btn_reg.setFixedHeight(36)
        btn_reg.clicked.connect(logic.registrar_usuario)
        layout.addWidget(btn_reg); layout.addSpacing(14)

        div = QFrame(objectName="divider"); div.setFrameShape(QFrame.Shape.HLine); div.setFixedHeight(1)
        layout.addWidget(div); layout.addSpacing(10)
        note = QLabel("La cuenta del administrador principal no puede eliminarse desde esta pantalla.", objectName="info-note")
        note.setWordWrap(True); layout.addWidget(note); layout.addStretch()

# Función para actualizar el estado de los botones de rol. Cambia el estilo del botón seleccionado para indicar qué rol se asignará al nuevo usuario.
    def _set_role(self, r):
        self.b_user.setObjectName("role-btn-selected" if r == "usuario" else "role-btn")
        self.b_admin.setObjectName("role-btn-selected" if r == "admin" else "role-btn")
        self.b_user.setStyle(self.b_user.style()); self.b_admin.setStyle(self.b_admin.style())

# Pantalla principal de administración de usuarios. Combina el TopBar, el panel izquierdo con la lista de usuarios y el panel derecho con el formulario de registro.
class AdminScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataPipeline AI — Administración")
        self.setStyleSheet(APP_STYLE); self.setMinimumSize(820, 500)
        
        self.logic = AdminLogic(self)
        root = QVBoxLayout(self); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(TopBar())

     # El contenido principal se divide en dos paneles: el izquierdo para la lista de usuarios y el derecho para el formulario de registro. Ambos paneles reciben la lógica para manejar las acciones de creación y eliminación de usuarios.
        content = QHBoxLayout()
        self.left_panel = LeftPanel(self.logic)
        self.right_panel = RightPanel(self.logic)
        content.addWidget(self.left_panel); content.addWidget(self.right_panel)
        root.addLayout(content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminScreen(); window.show()
    sys.exit(app.exec())