import tkinter as tk
from tkinter import messagebox, font as tkfont
import json
import os
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

    def guardar_usuario(self, usuario, password):
        datos = {"usuarios": []}
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, "r") as f:
                    datos = json.load(f)
            except: pass

        if any(u['usuario'] == usuario for u in datos['usuarios']):
            messagebox.showerror("Error", "El usuario ya existe en el núcleo")
            return False

        nuevo_id = len(datos["usuarios"]) + 1
        datos["usuarios"].append({
            "id": nuevo_id,
            "usuario": usuario,
            "password": self.encriptar(password),
            "estado": "activo",
            "es_admin": False
        })

        with open(self.archivo, "w") as f:
            json.dump(datos, f, indent=4)
        return True

    def setup_ui(self):
        contenedor = tk.Frame(self.root, bg=self.colors["tarjeta"], padx=40, pady=40,
                              highlightbackground="#1a1a1c", highlightthickness=1)
        contenedor.place(relx=0.5, rely=0.5, anchor="center", width=400)

        tk.Label(contenedor, text="REGISTRO DE NUEVO NODO", font=self.font_tag, 
                 fg=self.colors["ia_neon"], bg=self.colors["tarjeta"]).pack(pady=(0, 25))

        # Campos
        self.ent_user = self.crear_input(contenedor, "USUARIO")
        self.ent_pass = self.crear_input(contenedor, "CONTRASEÑA", True)
        self.ent_pass_conf = self.crear_input(contenedor, "CONFIRMAR CONTRASEÑA", True)

        tk.Button(contenedor, text="Registrar", font=self.font_btn,
                  bg=self.colors["ia_neon"], fg="black", command=self.procesar_registro,
                  relief="flat", cursor="hand2").pack(fill="x", pady=(30, 0), ipady=10)

    def crear_input(self, parent, label, es_pass=False):
        tk.Label(parent, text=label, fg="white", bg=self.colors["tarjeta"], 
                 font=("Verdana", 8)).pack(anchor="w", pady=(10, 0))
        entry = tk.Entry(parent, bg=self.colors["input_bg"], fg="white", 
                         insertbackground="white", relief="flat", font=("Segoe UI", 11))
        if es_pass: entry.config(show="*")
        entry.pack(fill="x", pady=5, ipady=8)
        return entry

    def procesar_registro(self):
        u, p, pc = self.ent_user.get(), self.ent_pass.get(), self.ent_pass_conf.get()
        
        if not u or not p:
            messagebox.showwarning("Atención", "Todos los campos son obligatorios")
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