import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QStackedWidget, QFrame)
from PyQt6.QtCore import Qt

class Consulta(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Consulta") 
        self.resize(800, 500) 
        self.setStyleSheet("background-color: #1e1e1e; color: white; font-family: Arial;")

        # --- CONTENEDOR PRINCIPAL ---
        self.main_container = QWidget()
        self.setCentralWidget(self.main_container)
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- BARRA DE MENÚ SUPERIOR ---
        self.setup_menu()

        # Widget que contendrá las pantallas
        self.central_widget = QStackedWidget()
        self.main_layout.addWidget(self.central_widget)

        # Inicializamos las pantallas (El orden aquí define el índice)
        self.init_pantalla_1()      # Índice 0: Subir CSV
        self.init_pantalla_2()      # Índice 1: Consulta activa
        self.init_pantalla_3()      # Índice 2: Resultado
        self.init_pantalla_scripts() # Índice 3: Scripts (Blanco)
        self.init_pantalla_admin()   # Índice 4: Admin

        # Iniciamos en la pantalla 0
        self.switch_tab(0)

    def setup_menu(self):
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #333;")
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(30, 15, 30, 5)

        self.btn_nav_consulta = QPushButton("Consulta")
        self.btn_nav_scripts = QPushButton("Scripts")
        self.btn_nav_admin = QPushButton("Administración")

        self.menu_buttons = [self.btn_nav_consulta, self.btn_nav_scripts, self.btn_nav_admin]
        
        # Conexiones explícitas para evitar errores de lambda
        self.btn_nav_consulta.clicked.connect(lambda: self.switch_tab(0))
        self.btn_nav_scripts.clicked.connect(lambda: self.switch_tab(3))
        self.btn_nav_admin.clicked.connect(lambda: self.switch_tab(4))

        for btn in self.menu_buttons:
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        self.main_layout.addWidget(nav_frame)

    def switch_tab(self, index):
        """Cambia de pantalla y actualiza el estilo visual"""
        self.central_widget.setCurrentIndex(index)
        
        for i, btn in enumerate(self.menu_buttons):
            # Lógica de iluminación de pestañas
            is_active = (index < 3 and i == 0) or (index == 3 and i == 1) or (index == 4 and i == 2)
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    font-weight: bold;
                    font-size: 13px;
                    color: {"#FFF" if is_active else "#666"};
                    border-bottom: {"2px solid white" if is_active else "none"};
                    padding-bottom: 5px;
                    margin-right: 20px;
                    border-top: none; border-left: none; border-right: none;
                }}
            """)

    # --- TUS PANTALLAS (Mantenidas íntegras) ---
    def init_pantalla_1(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        banner = QLabel("⚠️ Suba un dataset antes de realizar una consulta.")
        banner.setStyleSheet("background-color: #4a3a1e; color: #ffcc00; padding: 12px; border-radius: 8px;")
        
        btn_subir = QPushButton("↑ Subir CSV")
        btn_subir.setFixedHeight(40)
        btn_subir.setStyleSheet("background-color: #333; border: 1px solid #555; border-radius: 5px;")
        btn_subir.clicked.connect(lambda: self.central_widget.setCurrentIndex(1))

        input_chat = QTextEdit()
        input_chat.setPlaceholderText("Ej: Muestre la distribución de ventas por región...")
        input_chat.setReadOnly(True)
        input_chat.setMaximumHeight(120) 
        input_chat.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 10px;")
        
        layout.addWidget(banner)
        layout.addWidget(QLabel("<b>Dataset</b>"))
        layout.addWidget(btn_subir)
        layout.addWidget(input_chat)
        layout.addStretch() 
        self.central_widget.addWidget(page)

    def init_pantalla_2(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        status = QLabel("✅ ventas_2024.csv conectado")
        status.setStyleSheet("color: #76b900; font-weight: bold; font-size: 15px;")

        btn_cambiar = QPushButton("↑ Cambiar dataset")
        btn_cambiar.setFixedHeight(35)
        btn_cambiar.clicked.connect(lambda: self.central_widget.setCurrentIndex(0))

        self.input_real = QTextEdit()
        self.input_real.setPlaceholderText("¿Qué desea consultar?")
        self.input_real.setMaximumHeight(120)
        self.input_real.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 10px;")

        btn_ejecutar = QPushButton("Ejecutar Consulta")
        btn_ejecutar.setFixedHeight(40)
        btn_ejecutar.setStyleSheet("background-color: #0078d4; font-weight: bold; border-radius: 5px;")
        btn_ejecutar.clicked.connect(lambda: self.central_widget.setCurrentIndex(2))

        layout.addWidget(status)
        layout.addWidget(btn_cambiar)
        layout.addWidget(self.input_real)
        layout.addWidget(btn_ejecutar)
        layout.addStretch()
        self.central_widget.addWidget(page)

    def init_pantalla_3(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        header = QLabel("🟢 Consulta procesada correctamente")
        header.setStyleSheet("color: #76b900; font-weight: bold; background-color: #1a2e1a; padding: 8px; border-radius: 5px;")

        grafico = QFrame()
        grafico.setMinimumHeight(200) 
        grafico.setStyleSheet("background-color: #2a2a2a; border: 1px dashed #555; border-radius: 12px;")

        botones = QHBoxLayout()
        btn_guardar = QPushButton("Guardar")
        btn_descartar = QPushButton("Descartar")
        btn_descartar.clicked.connect(lambda: self.central_widget.setCurrentIndex(1))
        botones.addWidget(btn_guardar)
        botones.addWidget(btn_descartar)

        layout.addWidget(header)
        layout.addWidget(QLabel("<b>Ejemplo</b>"))
        layout.addWidget(grafico)
        layout.addLayout(botones)
        layout.addStretch()
        self.central_widget.addWidget(page)

    def init_pantalla_scripts(self):
        page = QWidget() # Totalmente en blanco
        self.central_widget.addWidget(page)

    def init_pantalla_admin(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.addWidget(QLabel("<h2>Panel de Administración</h2>"))
        layout.addStretch()
        self.central_widget.addWidget(page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Consulta()
    window.show()
    sys.exit(app.exec())