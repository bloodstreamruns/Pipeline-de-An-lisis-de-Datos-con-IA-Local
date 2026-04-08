import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTextEdit,
                             QStackedWidget, QFrame, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from interfaces.Script import Script
from interfaces.Form_admin_de_usuarios import AdminScreen
from core.prompt_builder import construir_prompt
from core.ollama_client import OllamaWorker
from lógica.logica_scripts import guardar_script

import pandas as pd

class Consulta(QMainWindow):
    def __init__(self, role: str = "usuario"):
        super().__init__()
        self.role = role
        self.csv_ruta   = None
        self.csv_nombre = None
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
        self.init_pantalla_1()       # Índice 0: Subir CSV
        self.init_pantalla_2()       # Índice 1: Consulta activa
        self.init_pantalla_3()       # Índice 2: Resultado
        self.init_pantalla_scripts() # Índice 3: Scripts
        self.init_pantalla_admin()   # Índice 4: Admin (solo admin)

        # Iniciamos en la pantalla 0
        self.switch_tab(0)

    def setup_menu(self):
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #333;")
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(30, 15, 30, 5)

        self.btn_nav_consulta = QPushButton("Consulta")
        self.btn_nav_scripts  = QPushButton("Scripts")
        self.btn_nav_admin    = QPushButton("Administración")

        self.menu_buttons = [self.btn_nav_consulta, self.btn_nav_scripts, self.btn_nav_admin]

        self.btn_nav_consulta.clicked.connect(lambda: self.switch_tab(0))
        self.btn_nav_scripts.clicked.connect(lambda: self.switch_tab(3))
        self.btn_nav_admin.clicked.connect(lambda: self.switch_tab(4))

        nav_layout.addWidget(self.btn_nav_consulta)
        nav_layout.addWidget(self.btn_nav_scripts)

        # El botón de Administración solo se agrega si el rol es admin
        if self.role == "admin":
            nav_layout.addWidget(self.btn_nav_admin)

        nav_layout.addStretch()
        self.main_layout.addWidget(nav_frame)

    def switch_tab(self, index):
        """Cambia de pantalla y actualiza el estilo visual."""
        self.central_widget.setCurrentIndex(index)

        for i, btn in enumerate(self.menu_buttons):
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

    def set_nav_callbacks(self, consulta_fn, scripts_fn, admin_fn):
        """Conecta los botones de la topbar a las funciones de navegación
        provistas por app.py."""
        self.btn_nav_consulta.clicked.connect(consulta_fn)
        self.btn_nav_scripts.clicked.connect(scripts_fn)
        self.btn_nav_admin.clicked.connect(admin_fn)

    # --- LÓGICA DE CSV ---
    def subir_csv(self):
        """Abre el explorador de archivos filtrado a .csv y navega a pantalla 1 si tiene éxito."""
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo CSV",
            "",
            "Archivos CSV (*.csv)"
        )

        if not ruta:
            return  # Usuario canceló — no hacer nada

        # Validación defensiva por si el SO ignora el filtro del diálogo
        if not ruta.lower().endswith(".csv"):
            QMessageBox.warning(
                self,
                "Archivo inválido",
                "Solo se permiten archivos .csv\n\nPor favor seleccione un archivo con extensión .csv."
            )
            return

        # Guardar ruta y nombre para uso posterior (pandas, etc.)
        self.csv_ruta   = ruta
        self.csv_nombre = os.path.basename(ruta)

        # Actualizar el label de estado en pantalla 2 con el nombre real
        self.label_csv_conectado.setText(f"✅ {self.csv_nombre} conectado")

        # Navegar a pantalla 2 (consulta activa)
        self.central_widget.setCurrentIndex(1)
        self.switch_tab(1)  # índices 0-2 activan "Consulta" en el menú

    # --- PANTALLAS ---
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
        # Conectado a subir_csv en lugar del lambda anterior
        btn_subir.clicked.connect(self.subir_csv)

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

        # Atributo de instancia para actualizarlo desde subir_csv()
        self.label_csv_conectado = QLabel("✅ —")
        self.label_csv_conectado.setStyleSheet("color: #76b900; font-weight: bold; font-size: 15px;")

        btn_cambiar = QPushButton("↑ Cambiar dataset")
        btn_cambiar.setFixedHeight(35)
        # Vuelve a pantalla 0 para que el usuario pueda elegir otro CSV
        btn_cambiar.clicked.connect(lambda: self.switch_tab(0))

        self.input_real = QTextEdit()
        self.input_real.setPlaceholderText("¿Qué desea consultar?")
        self.input_real.setMaximumHeight(120)
        self.input_real.setStyleSheet("background-color: #252525; border-radius: 8px; padding: 10px;")

        btn_ejecutar = QPushButton("Ejecutar Consulta")
        btn_ejecutar.setFixedHeight(40)
        btn_ejecutar.setStyleSheet("background-color: #0078d4; font-weight: bold; border-radius: 5px;")
        btn_ejecutar.clicked.connect(lambda: self.central_widget.setCurrentIndex(2))
        btn_ejecutar.clicked.connect(self.ejecutar_consulta)

        layout.addWidget(self.label_csv_conectado)
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
        btn_guardar   = QPushButton("Guardar")
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
        # Script es QMainWindow; se extrae su centralWidget para incrustarlo en el stack.
        # La instancia se guarda en self para evitar que el GC la destruya.
        self._script_window = Script()
        page = self._script_window.centralWidget()
        self.central_widget.addWidget(page)

    def init_pantalla_admin(self):
        if self.role == "admin":
            # embedded=True suprime la TopBar interna; la navegación la maneja Consulta.
            # Se guarda en self para evitar que el GC la destruya.
            self._admin_screen = AdminScreen(embedded=True)
            self.central_widget.addWidget(self._admin_screen)
        else:
            # Página vacía como placeholder para mantener el índice 4 consistente
            self.central_widget.addWidget(QWidget())

    def ejecutar_consulta(self):
        # 1. Leer el CSV
        if not self.csv_ruta:
            QMessageBox.warning(self, "Sin archivo", "Primero debes subir un archivo CSV.")
            return
        try:
            df = pd.read_csv(self.csv_ruta)
        except Exception as e:
            QMessageBox.warning(self, "Error al leer CSV", str(e))
            return

        # 2. Construir el prompt
        consulta = self.input_real.toPlainText().strip()
        if not consulta:
            QMessageBox.warning(self, "Consulta vacía", "Por favor, escribe una consulta.")
            return
        prompt = construir_prompt(df, consulta)

        # 3. Mostrar indicador de carga
        self.loading_label = QLabel("Procesando consulta con IA, por favor espera...")
        widget = self.central_widget.widget(1)
        if widget is not None:
            page_layout = widget.layout()
            if page_layout is not None:
                page_layout.addWidget(self.loading_label)

        # 4. Instanciar y lanzar el worker
        self.worker = OllamaWorker(prompt)
        self.worker.exito.connect(lambda codigo: self._on_ollama_exito(codigo, df, consulta))
        self.worker.error.connect(self._on_ollama_error)
        self.worker.start()

    def _on_ollama_exito(self, codigo, df, consulta):
        # Quitar indicador de carga
        self.loading_label.deleteLater()
        # Guardar el script (puedes pedir carpeta/nombre o usar valores por defecto)
        exito, msg = guardar_script("consultas", f"consulta_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}", codigo)
        if not exito:
            QMessageBox.warning(self, "Error al guardar script", msg)
        # Navegar a pantalla 3
        self.central_widget.setCurrentIndex(2)
        self.switch_tab(2)

    def _on_ollama_error(self, error_msg):
        self.loading_label.deleteLater()
        QMessageBox.warning(self, "Error IA", error_msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Consulta()
    window.show()
    sys.exit(app.exec())