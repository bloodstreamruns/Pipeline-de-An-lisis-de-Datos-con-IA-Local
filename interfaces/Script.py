import sys
import pandas as pd
import crud
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFrame, QTreeWidget,
    QTreeWidgetItem, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt

# matplotlib para graficar en PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Script(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Formulario Script")
        self.setMinimumSize(1100, 700)

        self.current_data = pd.DataFrame()  # DataFrame actual

        # ---------------- Main Layout ----------------
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------- SIDEBAR ----------------
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(280)
        sidebar_widget.setStyleSheet("background-color: #121212; border-right: 1px solid #2A2A2A;")
        sidebar_layout = QVBoxLayout(sidebar_widget)

        # Buscador
        search_bar = QLineEdit()
        search_bar.setPlaceholderText(" 🔍 Buscar resultados")
        sidebar_layout.addWidget(search_bar)

        # Árbol
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(15)
        self.tree.setStyleSheet("""
            QTreeWidget { background: transparent; border: none; font-size: 14px; }
            QTreeWidget::item { padding: 8px; color: #AAA; }
            QTreeWidget::item:selected { background-color: #2A2A2A; color: white; border-radius: 4px; }
        """)
        item_ventas = QTreeWidgetItem(self.tree, ["📁 Ventas"])
        item_ventas.addChild(QTreeWidgetItem(["📄 distribucion_region"]))
        item_ventas.addChild(QTreeWidgetItem(["📄 tendencia_mensual"]))
        item_ventas.setExpanded(True)
        self.tree.addTopLevelItem(item_ventas)
        self.tree.addTopLevelItem(QTreeWidgetItem(["📁 Clientes"]))
        self.tree.addTopLevelItem(QTreeWidgetItem(["📁 Inventario"]))
        sidebar_layout.addWidget(self.tree)

        # Botones
        actions_layout = QHBoxLayout()
        self.btn_abrir = QPushButton("Abrir")
        self.btn_abrir.clicked.connect(self.abrir_item)
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_item)
        self.btn_exportar = QPushButton("Exportar")
        self.btn_exportar.clicked.connect(self.exportar_archivo)
        actions_layout.addWidget(self.btn_abrir)
        actions_layout.addWidget(self.btn_eliminar)
        actions_layout.addWidget(self.btn_exportar)
        sidebar_layout.addLayout(actions_layout)

        # ---------------- PANEL DERECHO ----------------
        main_content = QVBoxLayout()
        main_content.setContentsMargins(30, 20, 30, 20)

        # Tabs
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
                    border-bottom: {"2px solid white" if is_active else "none"};
                    padding-bottom: 5px;
                    margin-right: 20px;
                }}
            """)
            tabs_layout.addWidget(tab)
        tabs_layout.addStretch()
        main_content.addLayout(tabs_layout)

        # ---------------- Header con icono independiente ----------------
        header_layout = QHBoxLayout()
        title_layout = QHBoxLayout()

        title = QLabel("Distribución por región")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
        """)

        help_icon = QLabel("❔")
        help_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        help_icon.setToolTip(
            "📌 INSTRUCCIONES:\n"
            "• Selecciona un archivo del panel izquierdo\n"
            "• Presiona 'Abrir' para cargarlo\n"
            "• Visualiza el resultado en el cuadro de resultados\n"
            "• Presiona 'Exportar' para guardar el archivo CSV"
        )
        help_icon.setStyleSheet("""
            font-size: 15px;
            color: #FFD700;
            padding-left: 10px;
        """)

        title_layout.addWidget(title)
        title_layout.addWidget(help_icon)
        title_layout.addStretch()

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_exportar)

        main_content.addLayout(header_layout)

        # Metadata
        meta_layout = QHBoxLayout()
        meta_layout.addWidget(QLabel("🏷️ Ventas    📄 ventas_2024.csv    📅 14 mar 2025 · 10:32"))
        main_content.addLayout(meta_layout)

        # Consulta
        main_content.addWidget(QLabel("\nConsulta"))
        consulta_box = QLabel("¿Cuál es la distribución de ventas por región?")
        consulta_box.setStyleSheet("""
            background-color: #181818; border: 1px solid #2A2A2A;
            padding: 15px; border-radius: 8px; color: #DDD;
        """)
        main_content.addWidget(consulta_box)

        # Resultado (graph_frame)
        main_content.addWidget(QLabel("\nResultado"))
        self.graph_frame = QFrame()
        self.graph_frame.setStyleSheet("""
            background-color: #181818; border: 1px solid #2A2A2A; border-radius: 12px;
        """)
        self.graph_frame.setMinimumHeight(300)
        self.graph_layout = QVBoxLayout()
        self.graph_frame.setLayout(self.graph_layout)
        main_content.addWidget(self.graph_frame)

        # Footer
        footer = QLabel("")
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.setStyleSheet("color: #555; font-size: 11px;")
        main_content.addWidget(footer)

        main_layout.addWidget(sidebar_widget)
        main_layout.addLayout(main_content)

    # ---------------- FUNCIONES ----------------
    def abrir_item(self):
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona un elemento primero")
            return
        ok, df = crud.abrir_item_logica(item.text(0))
        if ok:
            self.current_data = df
            self.dibujar_grafico(df)
        else:
            QMessageBox.warning(self, "Error", df)

    def eliminar_item(self):
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona un elemento para eliminar")
            return
        ok, mensaje = crud.eliminar_item_logica(self.tree, item)
        if ok:
            QMessageBox.information(self, "Éxito", mensaje)
            self.current_data = pd.DataFrame()
            self.limpiar_graph_frame()
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def exportar_archivo(self):
        if self.current_data.empty:
            QMessageBox.warning(self, "Aviso", "No hay datos para exportar")
            return
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "CSV (*.csv);;Todos los archivos (*)")
        if archivo:
            self.current_data.to_csv(archivo, index=False)
            QMessageBox.information(self, "Exportar", f"Archivo guardado en {archivo}")

    # ---------------- FUNCIONES DE GRAFICO ----------------
    def limpiar_graph_frame(self):
        for i in reversed(range(self.graph_layout.count())):
            widget = self.graph_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def dibujar_grafico(self, df):
        self.limpiar_graph_frame()

        fig = Figure(figsize=(5,3))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        if 'Region' in df.columns and 'Ventas' in df.columns:
            ax.bar(df['Region'], df['Ventas'], color='skyblue')
            ax.set_title("Distribución de ventas por región")
        elif 'Mes' in df.columns and 'Ventas' in df.columns:
            ax.plot(df['Mes'], df['Ventas'], marker='o', color='orange')
            ax.set_title("Tendencia mensual de ventas")
        else:
            ax.text(0.5, 0.5, 'No hay gráfico disponible', ha='center', va='center', fontsize=12)

        self.graph_layout.addWidget(canvas)
        canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Script()
    window.show()
    sys.exit(app.exec())
