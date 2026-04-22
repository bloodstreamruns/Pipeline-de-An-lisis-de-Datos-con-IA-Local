import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QMessageBox
from core.auth_service import AuthService, AuthServiceError


class AdminLogic:
    def __init__(self, interface):
        self.interface = interface
        self.auth = AuthService()

    def registrar_usuario(self):
        u   = self.interface.right_panel.u_input.text().strip()
        p   = self.interface.right_panel.p_input.text().strip()
        rol = "admin" if self.interface.right_panel.b_admin.objectName() == "role-btn-selected" else "usuario"

        if not u or not p:
            QMessageBox.warning(self.interface, "Error", "Debes rellenar todos los campos.")
            return

        try:
            usuarios = self.auth.obtener_usuarios()
        except AuthServiceError as e:
            QMessageBox.critical(self.interface, "Error del sistema", str(e))
            return

        if any(user["username"].lower() == u.lower() for user in usuarios):
            QMessageBox.critical(self.interface, "Error", f"El usuario '{u}' ya existe.")
            return

        try:
            self.auth.crear_usuario(u, p, rol)
        except AuthServiceError as e:
            QMessageBox.critical(self.interface, "Error del sistema", str(e))
            return

        QMessageBox.information(self.interface, "Éxito", f"Usuario '{u}' creado correctamente.")
        self.interface.right_panel.u_input.clear()
        self.interface.right_panel.p_input.clear()
        self.interface.right_panel._set_role("usuario")
        self.interface.left_panel.refrescar_lista()

    def eliminar_usuario(self, username):
        confirmar = QMessageBox.question(
            self.interface, "Confirmar",
            f"¿Seguro que quieres eliminar a {username}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmar == QMessageBox.StandardButton.Yes:
            try:
                self.auth.eliminar_usuario(username)
            except AuthServiceError as e:
                QMessageBox.critical(self.interface, "Error del sistema", str(e))
                return
            self.interface.left_panel.refrescar_lista()

    def cambiar_contrasena(self):
        u  = self.interface.right_panel.cp_user_input.text().strip()
        p1 = self.interface.right_panel.cp_new_input.text().strip()
        p2 = self.interface.right_panel.cp_confirm_input.text().strip()

        if not u or not p1 or not p2:
            QMessageBox.warning(self.interface, "Error", "Debes rellenar todos los campos.")
            return

        if p1 != p2:
            QMessageBox.critical(self.interface, "Error", "Las contraseñas no coinciden.")
            return

        try:
            usuarios = self.auth.obtener_usuarios()
        except AuthServiceError as e:
            QMessageBox.critical(self.interface, "Error del sistema", str(e))
            return

        if not any(user["username"].lower() == u.lower() for user in usuarios):
            QMessageBox.critical(self.interface, "Error", f"El usuario '{u}' no existe.")
            return

        try:
            self.auth.cambiar_contrasena(u, p1)
        except AuthServiceError as e:
            QMessageBox.critical(self.interface, "Error del sistema", str(e))
            return

        QMessageBox.information(self.interface, "Éxito", f"Contraseña de '{u}' actualizada correctamente.")
        self.interface.right_panel.cp_user_input.clear()
        self.interface.right_panel.cp_new_input.clear()
        self.interface.right_panel.cp_confirm_input.clear()
