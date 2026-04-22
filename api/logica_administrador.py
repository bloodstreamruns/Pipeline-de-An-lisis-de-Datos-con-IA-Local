from PyQt6.QtWidgets import QMessageBox 
from api import administrador_autenticacion # Módulo encargado de manejar la lectura y escritura de usuarios en el archivo JSON. Proporciona funciones para obtener la lista de usuarios, guardar un nuevo usuario y eliminar un usuario existente.


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
    
        # Cambia la contraseña de un usuario existente.
    # Validaciones:
    #   1. Ningún campo puede estar vacío.
    #   2. La nueva contraseña y la confirmación deben coincidir.
    #   3. El usuario indicado debe existir en el JSON.
    # Si todo pasa, delega la escritura a administrador_autenticacion y limpia el formulario.
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
 
        usuarios = administrador_autenticacion.obtener_lista_usuarios()
        if not any(user["username"].lower() == u.lower() for user in usuarios):
            QMessageBox.critical(self.interface, "Error", f"El usuario '{u}' no existe.")
            return
 
        administrador_autenticacion.cambiar_contrasena(u, p1)
        QMessageBox.information(self.interface, "Éxito", f"Contraseña de '{u}' actualizada correctamente.")
 
        self.interface.right_panel.cp_user_input.clear()
        self.interface.right_panel.cp_new_input.clear()
        self.interface.right_panel.cp_confirm_input.clear()
 
