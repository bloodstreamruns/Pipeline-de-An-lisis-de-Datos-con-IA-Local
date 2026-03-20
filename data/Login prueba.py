import tkinter as tk
from tkinter import messagebox
from tkinter import font as tkfont
import json
import os
import hashlib

class CortexAIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CÓRTEX AI - Portal de Acceso")
        self.root.geometry("600x650")
        self.root.configure(bg="#010103") 

        self.archivo = "usuarios.json"

        self.colors = {
            "ia_neon": "#a3ff12",      
            "fondo": "#010103",       
            "tarjeta": "#0a0a0c",     
            "texto_p": "#ffffff",     
            "texto_s": "#555555",     
            "input_bg": "#111113",    
            "btn_active": "#ccff66"   
        }

        self.font_ia = tkfont.Font(family="Courier New", size=36, weight="bold") 
        self.font_tag = tkfont.Font(family="Verdana", size=9, weight="bold")
        self.font_main = tkfont.Font(family="Segoe UI", size=11)
        self.font_btn = tkfont.Font(family="Segoe UI", size=12, weight="bold")

        self.setup_ui()

    # 🔐 Encriptar contraseña
    def encriptar(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # 💾 Guardar usuario
    def guardar_usuario(self, usuario, password):
        if os.path.exists(self.archivo):
            with open(self.archivo, "r") as f:
                datos = json.load(f)
        else:
            datos = {"usuarios": []}

        datos["usuarios"].append({
            "usuario": usuario,
            "password": self.encriptar(password)
        })

        with open(self.archivo, "w") as f:
            json.dump(datos, f, indent=4)

    # 🔎 Validar login
    def validar_login(self, usuario, password):
        if not os.path.exists(self.archivo):
            return False

        with open(self.archivo, "r") as f:
            datos = json.load(f)

        for u in datos["usuarios"]:
            if u["usuario"] == usuario and u["password"] == self.encriptar(password):
                return True

        return False

    def setup_ui(self):
        self.panel = tk.Frame(self.root, bg=self.colors["tarjeta"], padx=55, pady=60,
                             highlightbackground="#1a1a1c", highlightthickness=1)
        self.panel.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.panel, text="NÚCLEO NEURAL ACTIVO", font=self.font_tag, 
                 fg=self.colors["ia_neon"], bg=self.colors["tarjeta"]).pack()
        
        tk.Label(self.panel, text="Córtex AI", font=self.font_ia, 
                 fg=self.colors["texto_p"], bg=self.colors["tarjeta"]).pack(pady=(10, 0))
        
        tk.Label(self.panel, text="Sistema Cognitivo Avanzado", font=("Verdana", 10), 
                 fg=self.colors["texto_s"], bg=self.colors["tarjeta"]).pack(pady=(0, 45))

        self.user_input = self.crear_campo("NOMBRE DE USUARIO", "ej. oper_ia_central")
        self.pass_input = self.crear_campo("CLAVE DE ACCESO", "••••••••", es_pass=True)

        self.btn_acceso = tk.Button(self.panel, text="INICIAR / REGISTRAR", font=self.font_btn,
                                   bg=self.colors["ia_neon"], fg="#000000", 
                                   activebackground=self.colors["btn_active"], relief="flat", 
                                   cursor="hand2", command=self.procesar_login)
        self.btn_acceso.pack(fill="x", pady=(45, 10), ipady=14)

        self.root.bind('<Return>', lambda e: self.procesar_login())

    def crear_campo(self, titulo, sugerencia, es_pass=False):
        tk.Label(self.panel, text=titulo, font=self.font_tag, 
                 fg=self.colors["texto_p"], bg=self.colors["tarjeta"]).pack(anchor="w", pady=(20, 0))
        
        entrada = tk.Entry(self.panel, font=self.font_main, fg=self.colors["texto_s"],
                         bg=self.colors["input_bg"], relief="flat", 
                         insertbackground=self.colors["ia_neon"], bd=10) 
        entrada.insert(0, sugerencia)
        entrada.pack(fill="x", pady=5)

        entrada.bind("<FocusIn>", lambda e: self.en_foco(entrada, sugerencia, es_pass))
        entrada.bind("<FocusOut>", lambda e: self.fuera_foco(entrada, sugerencia, es_pass))
        return entrada

    def en_foco(self, entrada, sugerencia, es_pass):
        if entrada.get() == sugerencia:
            entrada.delete(0, tk.END)
            entrada.config(fg=self.colors["texto_p"])
            if es_pass: entrada.config(show="*")

    def fuera_foco(self, entrada, sugerencia, es_pass):
        if not entrada.get():
            entrada.insert(0, sugerencia)
            entrada.config(fg=self.colors["texto_s"])
            if es_pass: entrada.config(show="")

    # 🚀 LOGIN + REGISTRO AUTOMÁTICO
    def procesar_login(self):
        usuario = self.user_input.get()
        password = self.pass_input.get()

        if usuario in ["", "ej. oper_ia_central"] or password in ["", "••••••••"]:
            messagebox.showwarning("Atención", "Complete usuario y contraseña.")
            return

        if self.validar_login(usuario, password):
            messagebox.showinfo("Córtex OS", f"Bienvenido nuevamente, {usuario}")
        else:
            # Si no existe → lo registra
            self.guardar_usuario(usuario, password)
            messagebox.showinfo("Córtex OS", f"Usuario registrado: {usuario}")

if __name__ == "__main__":
    ventana = tk.Tk()
    app = CortexAIApp(ventana)
    ventana.mainloop()