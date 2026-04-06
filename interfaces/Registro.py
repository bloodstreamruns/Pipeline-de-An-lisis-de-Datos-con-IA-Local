import tkinter as tk
from tkinter import messagebox, font as tkfont
import json
import hashlib

class RegistroCortex:
    def __init__(self, root):
        self.root = root
        self.root.title("Córtex AI - Registro de Nodo")
        self.root.geometry("500x600")
        self.root.configure(bg="#010103")

        self.archivo = "usuarios.json"

        self.colors = {
            "ia_neon": "#a3ff12",
            "tarjeta": "#0a0a0c",
            "texto_p": "#ffffff",
            "texto_s": "#555555",
            "input_bg": "#111113"
        }
        self.font_tag = tkfont.Font(family="Verdana", size=9, weight="bold")
        self.font_btn = tkfont.Font(family="Segoe UI", size=12, weight="bold")

        self.setup_ui()

    def encriptar(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _procesar_login(self):
        username = self.input_user.text().strip()
        password = self.input_pass.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Campos vacíos", "Ingrese usuario y contraseña.")
            return
        if p != pc:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        if len(p) < 4:
            messagebox.showerror("Error", "Seguridad insuficiente (mínimo 4 caracteres)")
            return

        if self.guardar_usuario(u, p):
            messagebox.showinfo("Éxito", f"Usuario {u} registrado correctamente")
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroCortex(root)
    root.mainloop()