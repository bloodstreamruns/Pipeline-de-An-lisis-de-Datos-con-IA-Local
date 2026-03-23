import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLineEdit, QPushButton, QLabel,
                            QFrame, QTreeWidget, QTreeWidgetItem, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QSize

class Script(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Formulario Script")
        self.setMinimumSize(1100, 700)

        # Estilo Global (Dark Theme)
        self.setStyleSheet("""
            QMainWindow { background-color: #0F0F0F; }
            QWidget { color: #BABABA; font-family: 'Segoe UI', Arial; }
            QLabel { border: none; }
            QPushButton { border-radius: 4px; padding: 6px; }
        """)

        # Main Widget y Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. SIDEBAR IZQUIERDO (Navegación de archivos) ---
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(280)
        sidebar_widget.setStyleSheet("background-color: #121212; border-right: 1px solid #2A2A2A;")
        sidebar_layout = QVBoxLayout(sidebar_widget)

        # Buscador
        search_bar = QLineEdit()
        search_bar.setPlaceholderText(" 🔍 Buscar resultados")
        search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 8px;
                color: white;
            }
        """)
        sidebar_layout.addWidget(search_bar)

        # Árbol de archivos (QTreeWidget)
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)
        self.tree.setStyleSheet("""
            QTreeWidget { background: transparent; border: none; font-size: 14px; }
            QTreeWidget::item { padding: 8px; color: #AAA; }
            QTreeWidget::item:selected { background-color: #2A2A2A; color: white; border-radius: 4px; }
        """)

        # Llenado de datos (Mockup)
        item_ventas = QTreeWidgetItem(self.tree, ["📁 Ventas"])
        item_ventas.addChild(QTreeWidgetItem(["   📄 distribucion_region"]))
        item_ventas.addChild(QTreeWidgetItem(["   📄 tendencia_mensual"]))
        item_ventas.setExpanded(True)

        self.tree.addTopLevelItem(item_ventas)
        self.tree.addTopLevelItem(QTreeWidgetItem(["📁 Clientes"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["📁 Inventario"]))
        sidebar_layout.addWidget(self.tree)

        # Botones de Acción inferior
        actions_layout = QHBoxLayout()
        btn_abrir = QPushButton("Abrir")
        btn_eliminar = QPushButton("Eliminar")
        for btn in [btn_abrir, btn_eliminar]:
            btn.setStyleSheet("background: #252525; color: white; border: 1px solid #444; padding: 10px;")
            actions_layout.addWidget(btn)
        sidebar_layout.addLayout(actions_layout)

        # --- 2. PANEL DERECHO (Contenido Principal) ---
        main_content = QVBoxLayout()
        main_content.setContentsMargins(30, 20, 30, 20)

        # Tabs Superiores
        tabs_layout = QHBoxLayout()
        for text in ["Consulta", "Scripts", "Administración"]:
            tab = QPushButton(text)
            is_active = text == "Scripts"
            tab.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    font-weight: bold;
                    font-size: 16px;
                    color: {"#FFF" if is_active else "#666"};
                    border-bottom: { "2px solid white" if is_active else "none" };
                    padding-bottom: 5px;
                    margin-right: 20px;
                }}
            """)
            tabs_layout.addWidget(tab)
        tabs_layout.addStretch()
        main_content.addLayout(tabs_layout)

        # Header de la Sección que el titulo
        header_layout = QHBoxLayout()
        title = QLabel("Distribución por región")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; margin-top: 20px;")

        btn_exportar = QPushButton("Exportar")
        btn_exportar.setStyleSheet("""
            background-color: white; color: black; font-weight: bold;
            padding: 8px 25px; border-radius: 8px; margin-top: 20px;
        """)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_exportar)
        main_content.addLayout(header_layout)

        # Etiquetas de Metadata en la parte de arriba abajito del distribucion de region
        meta_layout = QHBoxLayout()
        meta_layout.addWidget(QLabel("🏷️ Ventas    📄 ventas_2024.csv    📅 14 mar 2025 · 10:32"))
        main_content.addLayout(meta_layout)

        # Sección Consulta en la parte de descripcion
        main_content.addWidget(QLabel("\nConsulta"))
        consulta_box = QLabel("¿Cuál es la distribución de ventas por región?")
        consulta_box.setStyleSheet("""
            background-color: #181818; border: 1px solid #2A2A2A;
            padding: 15px; border-radius: 8px; color: #DDD; font-size: 15px;
        """)
        main_content.addWidget(consulta_box)

        # Sección Resultado (Gráfico)
        main_content.addWidget(QLabel("\nResultado"))
        self.graph_frame = QFrame()
        self.graph_frame.setStyleSheet("""
            background-color: #181818; border: 1px solid #2A2A2A; border-radius: 12px;
        """)
        self.graph_frame.setMinimumHeight(300)

        # (Aquí podrías meter un QVBoxLayout para insertar un gráfico de Matplotlib)
        main_content.addWidget(self.graph_frame)

        # descripcion de abajo
        footer = QLabel("")
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.setStyleSheet("color: #555; font-size: 11px;")
        main_content.addWidget(footer)

        # Ensamblar todo
        main_layout.addWidget(sidebar_widget)
        main_layout.addLayout(main_content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Script()
    window.show()
    sys.exit(app.exec())