from PyQt6.QtWidgets import QMessageBox 
import administrador_autenticacion # Módulo encargado de manejar la lectura y escritura de usuarios en el archivo JSON. Proporciona funciones para obtener la lista de usuarios, guardar un nuevo usuario y eliminar un usuario existente.


class AdminLogic:
    def __init__(self, interface):
        self.interface = interface

# Función para registrar un nuevo usuario. Realiza validaciones de campos vacíos y duplicados antes de guardar el nuevo usuario en el archivo JSON. Después de registrar, limpia los campos del formulario y refresca la lista de usuarios en la interfaz.
    def registrar_usuario(self):
        # Extraemos los datos desde la interfaz
        u = self.interface.right_panel.u_input.text().strip()
        p = self.interface.right_panel.p_input.text().strip()
        # Determinamos el rol según qué botón está seleccionado en la interfaz
        rol = "admin" if self.interface.right_panel.b_admin.objectName() == "role-btn-selected" else "usuario"

        # Validaciones de funcionamiento
        if not u or not p:
            QMessageBox.warning(self.interface, "Error", "Debes rellenar todos los campos.")
            return

        usuarios = administrador_autenticacion.obtener_lista_usuarios()
        if any(user['username'].lower() == u.lower() for user in usuarios):
            QMessageBox.critical(self.interface, "Error", f"El usuario '{u}' ya existe.")
            return

        # Acción de guardado
        administrador_autenticacion.guardar_nuevo_usuario(u, p, rol)
        QMessageBox.information(self.interface, "Éxito", f"Usuario '{u}' creado correctamente.")
        
        # Limpiamos la interfaz y refrescamos la lista
        self.interface.right_panel.u_input.clear()
        self.interface.right_panel.p_input.clear()
        self.interface.right_panel._set_role("usuario")
        self.interface.left_panel.refrescar_lista()

     # Función para eliminar un usuario. Muestra un cuadro de confirmación antes de eliminar el usuario 
    def eliminar_usuario(self, username):
        confirmar = QMessageBox.question(
            self.interface, "Confirmar", 
            f"¿Seguro que quieres eliminar a {username}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmar == QMessageBox.StandardButton.Yes:
            administrador_autenticacion.eliminar_usuario(username)
            self.interface.left_panel.refrescar_lista()