import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from lógica.logica_scripts import (
    obtener_arbol,
    crear_carpeta,
    renombrar_carpeta,
    eliminar_carpeta,
    eliminar_script,
    mover_script,
    ejecutar_script,
    ruta_script,
)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFrame, QTreeWidget,
    QTreeWidgetItem, QMessageBox, QInputDialog, QDialog,
    QScrollArea, QSizePolicy, QMenu
)
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


# ─────────────────────────────────────────────────────────────────────────────
# Diálogo de resultado (ventana expandida al ejecutar)
# ─────────────────────────────────────────────────────────────────────────────

class DialogoResultado(QDialog):
    """Ventana independiente que muestra el gráfico o texto del script ejecutado."""

    def __init__(self, titulo: str, resultado, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Resultado — {titulo}")
        self.setMinimumSize(860, 560)
        self.setStyleSheet("background-color: #111;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Título
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(
            "color: white; font-size: 18px; font-weight: bold;"
        )
        layout.addWidget(lbl_titulo)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #2A2A2A;")
        layout.addWidget(sep)

        # Contenido: figura o texto
        if isinstance(resultado, Figure):
            canvas = FigureCanvas(resultado)
            canvas.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            layout.addWidget(canvas)
            canvas.draw()
        else:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet(
                "QScrollArea { border: none; background: transparent; }"
            )
            lbl = QLabel(str(resultado))
            lbl.setStyleSheet(
                "color: #CCC; font-family: 'Courier New', monospace;"
                "font-size: 13px; padding: 10px;"
            )
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            scroll.setWidget(lbl)
            layout.addWidget(scroll)

        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setFixedWidth(100)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A; color: #CCC;
                border: none; border-radius: 6px; padding: 7px 16px; font-size: 13px;
            }
            QPushButton:hover { background-color: #3A3A3A; }
        """)
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)


# ─────────────────────────────────────────────────────────────────────────────
# Ventana principal
# ─────────────────────────────────────────────────────────────────────────────

class Script(QMainWindow):
    def __init__(self, dataframe: pd.DataFrame = None):
        """
        Parameters
        ----------
        dataframe : pd.DataFrame, optional
            DataFrame inyectado desde la pantalla anterior.
            Si se omite se usa uno de prueba al correr directamente.
        """
        super().__init__()
        self.setWindowTitle("Scripts")
        self.setMinimumSize(1100, 700)

        self.current_data: pd.DataFrame = (
            dataframe if dataframe is not None else pd.DataFrame()
        )
        self._carpeta_sel: str = ""
        self._script_sel:  str = ""

        # ── Widget central ────────────────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── SIDEBAR ───────────────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(
            "background-color: #121212; border-right: 1px solid #2A2A2A;"
        )
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(10, 14, 10, 12)
        sb.setSpacing(8)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍  Buscar script")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E1E; color: #CCC;
                border: 1px solid #333; border-radius: 6px;
                padding: 6px 10px; font-size: 13px;
            }
        """)
        self.search_bar.textChanged.connect(self._filtrar_arbol)
        sb.addWidget(self.search_bar)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(14)
        self.tree.setStyleSheet("""
            QTreeWidget { background: transparent; border: none; font-size: 13px; }
            QTreeWidget::item { padding: 7px; color: #AAA; }
            QTreeWidget::item:selected {
                background-color: #2A2A2A; color: white; border-radius: 4px;
            }
        """)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._menu_contextual)
        self.tree.currentItemChanged.connect(self._al_seleccionar)
        sb.addWidget(self.tree)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self.btn_nueva_sub = QPushButton("＋ Subcarpeta")
        self.btn_nueva_sub.setToolTip("Crear nueva subcarpeta")
        self.btn_nueva_sub.setStyleSheet(self._estilo_btn_sb())
        self.btn_nueva_sub.clicked.connect(self._crear_subcarpeta)
        self.btn_eliminar = QPushButton("🗑")
        self.btn_eliminar.setToolTip("Eliminar selección")
        self.btn_eliminar.setStyleSheet(self._estilo_btn_sb("#7A1C1C"))
        self.btn_eliminar.clicked.connect(self._eliminar_seleccionado)
        btn_row.addWidget(self.btn_nueva_sub)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_eliminar)
        sb.addLayout(btn_row)

        # ── PANEL DERECHO ─────────────────────────────────────────────────────
        panel = QWidget()
        panel.setStyleSheet("background-color: #0F0F0F;")
        p = QVBoxLayout(panel)
        p.setContentsMargins(32, 22, 32, 22)
        p.setSpacing(10)

        # Tabs decorativos
        tabs_row = QHBoxLayout()
        for texto in ["Consulta", "Scripts", "Administración"]:
            activo = texto == "Scripts"
            btn = QPushButton(texto)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; font-weight: bold; font-size: 15px;
                    color: {"#FFF" if activo else "#555"};
                    border-bottom: {"2px solid white" if activo else "none"};
                    border-left: none; border-right: none; border-top: none;
                    padding-bottom: 5px; margin-right: 20px;
                }}
            """)
            tabs_row.addWidget(btn)
        tabs_row.addStretch()
        p.addLayout(tabs_row)

        # Título + ayuda
        title_row = QHBoxLayout()
        self.lbl_titulo = QLabel("Selecciona un script")
        self.lbl_titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: white;"
        )
        lbl_ayuda = QLabel("❔")
        lbl_ayuda.setCursor(Qt.CursorShape.PointingHandCursor)
        lbl_ayuda.setToolTip(
            "INSTRUCCIONES:\n"
            "• Selecciona un script del panel izquierdo\n"
            "• Clic derecho en el árbol para renombrar o mover\n"
            "• Presiona ▶ Ejecutar para ver el resultado en pantalla completa"
        )
        lbl_ayuda.setStyleSheet(
            "font-size: 15px; color: #FFD700; padding-left: 8px;"
        )
        title_row.addWidget(self.lbl_titulo)
        title_row.addWidget(lbl_ayuda)
        title_row.addStretch()
        p.addLayout(title_row)

        # Metadata
        self.lbl_meta = QLabel("")
        self.lbl_meta.setStyleSheet("color: #555; font-size: 12px;")
        p.addWidget(self.lbl_meta)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setStyleSheet("color: #2A2A2A;")
        p.addWidget(sep1)

        # Consulta (placeholder)
        lbl_sec_consulta = QLabel("Consulta")
        lbl_sec_consulta.setStyleSheet(
            "color: #888; font-size: 12px; font-weight: bold; margin-top: 4px;"
        )
        p.addWidget(lbl_sec_consulta)

        self.lbl_consulta = QLabel("—")
        self.lbl_consulta.setStyleSheet("""
            background-color: #181818; border: 1px solid #2A2A2A;
            border-radius: 8px; padding: 14px; color: #666; font-size: 13px;
        """)
        self.lbl_consulta.setWordWrap(True)
        p.addWidget(self.lbl_consulta)

        # Resultado (preview compacta)
        lbl_sec_resultado = QLabel("Resultado")
        lbl_sec_resultado.setStyleSheet(
            "color: #888; font-size: 12px; font-weight: bold; margin-top: 4px;"
        )
        p.addWidget(lbl_sec_resultado)

        self.graph_frame = QFrame()
        self.graph_frame.setStyleSheet("""
            QFrame {
                background-color: #181818;
                border: 1px solid #2A2A2A;
                border-radius: 12px;
            }
        """)
        self.graph_frame.setMinimumHeight(260)
        self.graph_layout = QVBoxLayout(self.graph_frame)
        self.graph_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p.addWidget(self.graph_frame)

        self._mostrar_placeholder("Selecciona un script y presiona  ▶ Ejecutar")

        # Botón ejecutar
        run_row = QHBoxLayout()
        run_row.addStretch()
        self.btn_ejecutar = QPushButton("▶  Ejecutar")
        self.btn_ejecutar.setEnabled(False)
        self.btn_ejecutar.setStyleSheet("""
            QPushButton {
                background-color: #1DB954; color: white; font-size: 14px;
                font-weight: bold; border: none; border-radius: 7px;
                padding: 9px 28px;
            }
            QPushButton:disabled { background-color: #1E3A2A; color: #444; }
            QPushButton:hover:!disabled { background-color: #17a349; }
        """)
        self.btn_ejecutar.clicked.connect(self._ejecutar_script)
        run_row.addWidget(self.btn_ejecutar)
        p.addLayout(run_row)

        footer = QLabel(
            "Clic derecho en el árbol para renombrar · mover · eliminar"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        footer.setStyleSheet("color: #2A2A2A; font-size: 11px;")
        p.addWidget(footer)

        root.addWidget(sidebar)
        root.addWidget(panel)

        self._refrescar_arbol()

    # ── Estilos ───────────────────────────────────────────────────────────────

    def _estilo_btn_sb(self, color="#2A2A2A") -> str:
        return f"""
            QPushButton {{
                background-color: {color}; color: #CCC;
                border: none; border-radius: 5px;
                padding: 6px 12px; font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #3A3A3A; }}
        """

    # ── Árbol ─────────────────────────────────────────────────────────────────

    def _refrescar_arbol(self, expandir: str = ""):
        self.tree.blockSignals(True)
        self.tree.clear()
        arbol = obtener_arbol()
        for carpeta, scripts in arbol.items():
            item_carp = QTreeWidgetItem(self.tree, [f"📁  {carpeta}"])
            item_carp.setData(
                0, Qt.ItemDataRole.UserRole,
                {"tipo": "subcarpeta", "carpeta": carpeta}
            )
            for nombre in scripts:
                item_sc = QTreeWidgetItem(item_carp, [f"📄  {nombre}"])
                item_sc.setData(
                    0, Qt.ItemDataRole.UserRole,
                    {"tipo": "script", "carpeta": carpeta, "nombre": nombre}
                )
            # Expandir si corresponde
            item_carp.setExpanded(carpeta == expandir or not expandir)
        self.tree.blockSignals(False)

    def _filtrar_arbol(self, texto: str):
        texto = texto.lower().strip()
        for i in range(self.tree.topLevelItemCount()):
            carp = self.tree.topLevelItem(i)
            hay_visible = False
            for j in range(carp.childCount()):
                sc = carp.child(j)
                data = sc.data(0, Qt.ItemDataRole.UserRole) or {}
                coincide = texto in data.get("nombre", "").lower()
                sc.setHidden(not coincide)
                if coincide:
                    hay_visible = True
            carp.setHidden(bool(texto) and not hay_visible)
            if hay_visible:
                carp.setExpanded(True)

    def _al_seleccionar(self, item: QTreeWidgetItem, _prev):
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data["tipo"] != "script":
            self.btn_ejecutar.setEnabled(False)
            return
        self._carpeta_sel = data["carpeta"]
        self._script_sel  = data["nombre"]
        self.lbl_titulo.setText(data["nombre"])
        self.lbl_meta.setText(
            f"Subcarpeta: {data['carpeta']}   ·   {data['carpeta']}/{data['nombre']}.py"
        )
        self.lbl_consulta.setText("(sin consulta asociada aún)")
        self.lbl_consulta.setStyleSheet("""
            background-color: #181818; border: 1px solid #2A2A2A;
            border-radius: 8px; padding: 14px;
            color: #555; font-size: 13px; font-style: italic;
        """)
        self._mostrar_placeholder("Presiona  ▶ Ejecutar  para ver el resultado")
        self.btn_ejecutar.setEnabled(not self.current_data.empty)

    # ── Menú contextual ───────────────────────────────────────────────────────

    def _menu_contextual(self, pos):
        item = self.tree.itemAt(pos)
        if not item:
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1E1E1E; color: #CCC;
                border: 1px solid #333; border-radius: 6px;
            }
            QMenu::item { padding: 7px 20px; }
            QMenu::item:selected { background-color: #2A2A2A; border-radius: 4px; }
        """)

        if data["tipo"] == "subcarpeta":
            act_rename = menu.addAction("✏  Renombrar subcarpeta")
            act_delete = menu.addAction("🗑  Eliminar subcarpeta")
            accion = menu.exec(self.tree.viewport().mapToGlobal(pos))
            if accion == act_rename:
                self._renombrar_subcarpeta(data["carpeta"])
            elif accion == act_delete:
                self._eliminar_subcarpeta(data["carpeta"])

        elif data["tipo"] == "script":
            act_rename = menu.addAction("✏  Renombrar script")
            act_mover  = menu.addAction("📁  Mover a otra subcarpeta")
            menu.addSeparator()
            act_delete = menu.addAction("🗑  Eliminar script")
            accion = menu.exec(self.tree.viewport().mapToGlobal(pos))
            if accion == act_rename:
                self._renombrar_script(data["carpeta"], data["nombre"])
            elif accion == act_mover:
                self._mover_script(data["carpeta"], data["nombre"])
            elif accion == act_delete:
                self._eliminar_script_confirm(data["carpeta"], data["nombre"])

    # ── CRUD subcarpetas ──────────────────────────────────────────────────────

    def _crear_subcarpeta(self):
        nombre, ok = QInputDialog.getText(
            self, "Nueva subcarpeta", "Nombre de la subcarpeta:"
        )
        if not ok or not nombre.strip():
            return
        exito, resultado = crear_carpeta(nombre.strip())
        if exito:
            self._refrescar_arbol(expandir=resultado)
        else:
            QMessageBox.warning(self, "Error", resultado)

    def _renombrar_subcarpeta(self, nombre_actual: str):
        nuevo, ok = QInputDialog.getText(
            self, "Renombrar subcarpeta", "Nuevo nombre:", text=nombre_actual
        )
        if not ok or not nuevo.strip():
            return
        exito, resultado = renombrar_carpeta(nombre_actual, nuevo.strip())
        if exito:
            if self._carpeta_sel == nombre_actual:
                self._carpeta_sel = resultado
                self.lbl_meta.setText(
                    f"Subcarpeta: {resultado}   ·   {resultado}/{self._script_sel}.py"
                )
            self._refrescar_arbol(expandir=resultado)
        else:
            QMessageBox.warning(self, "Error", resultado)

    def _eliminar_subcarpeta(self, nombre: str):
        resp = QMessageBox.question(
            self, "Eliminar subcarpeta",
            f"¿Eliminar la subcarpeta '{nombre}' y todos sus scripts?\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        exito, mensaje = eliminar_carpeta(nombre)
        if exito:
            if self._carpeta_sel == nombre:
                self._limpiar_panel()
            self._refrescar_arbol()
        else:
            QMessageBox.warning(self, "Error", mensaje)

    # ── CRUD scripts ──────────────────────────────────────────────────────────

    def _renombrar_script(self, carpeta: str, nombre: str):
        nuevo, ok = QInputDialog.getText(
            self, "Renombrar script", "Nuevo nombre (sin .py):", text=nombre
        )
        if not ok or not nuevo.strip():
            return
        nuevo = nuevo.strip()
        origen  = ruta_script(carpeta, nombre)
        destino = ruta_script(carpeta, nuevo)
        if os.path.exists(destino):
            QMessageBox.warning(
                self, "Error",
                f"Ya existe un script llamado '{nuevo}' en '{carpeta}'."
            )
            return
        try:
            os.rename(origen, destino)
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return
        if self._carpeta_sel == carpeta and self._script_sel == nombre:
            self._script_sel = nuevo
            self.lbl_titulo.setText(nuevo)
            self.lbl_meta.setText(
                f"Subcarpeta: {carpeta}   ·   {carpeta}/{nuevo}.py"
            )
        self._refrescar_arbol(expandir=carpeta)

    def _mover_script(self, carpeta_origen: str, nombre: str):
        arbol    = obtener_arbol()
        destinos = [c for c in arbol if c != carpeta_origen]
        if not destinos:
            QMessageBox.warning(
                self, "Sin destinos",
                "No hay otras subcarpetas disponibles.\n"
                "Crea primero otra subcarpeta con '＋ Subcarpeta'."
            )
            return
        dest, ok = QInputDialog.getItem(
            self, "Mover script", f"Mover '{nombre}' a:", destinos, 0, False
        )
        if not ok:
            return
        exito, mensaje = mover_script(carpeta_origen, nombre, dest)
        if exito:
            if self._carpeta_sel == carpeta_origen and self._script_sel == nombre:
                self._carpeta_sel = dest
                self.lbl_meta.setText(
                    f"Subcarpeta: {dest}   ·   {dest}/{nombre}.py"
                )
            self._refrescar_arbol(expandir=dest)
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def _eliminar_script_confirm(self, carpeta: str, nombre: str):
        resp = QMessageBox.question(
            self, "Eliminar script",
            f"¿Eliminar '{nombre}' de la subcarpeta '{carpeta}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        exito, mensaje = eliminar_script(carpeta, nombre)
        if exito:
            if self._carpeta_sel == carpeta and self._script_sel == nombre:
                self._limpiar_panel()
            self._refrescar_arbol(expandir=carpeta)
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def _eliminar_seleccionado(self):
        """Botón 🗑 del sidebar — elimina el ítem seleccionado."""
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(self, "Aviso", "Selecciona un elemento primero.")
            return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        if data["tipo"] == "subcarpeta":
            self._eliminar_subcarpeta(data["carpeta"])
        else:
            self._eliminar_script_confirm(data["carpeta"], data["nombre"])

    # ── Ejecución ─────────────────────────────────────────────────────────────

    def _ejecutar_script(self):
        if not self._carpeta_sel or not self._script_sel:
            return
        if self.current_data.empty:
            QMessageBox.warning(
                self, "Sin datos",
                "No hay un DataFrame cargado.\n"
                "Regresa a la pantalla anterior para cargar un archivo."
            )
            return

        self._mostrar_placeholder("Ejecutando…")
        QApplication.processEvents()

        exito, resultado = ejecutar_script(
            self._carpeta_sel, self._script_sel, self.current_data
        )

        if not exito:
            self._mostrar_placeholder(f"⚠  {resultado}", error=True)
            QMessageBox.warning(self, "Error de ejecución", str(resultado))
            return

        # Abrir resultado en ventana expandida
        dialogo = DialogoResultado(self._script_sel, resultado, parent=self)
        dialogo.exec()

        # Preview compacta que queda en el panel
        self._mostrar_preview(resultado)

    # ── Utilidades de UI ──────────────────────────────────────────────────────

    def _limpiar_graph_frame(self):
        for i in reversed(range(self.graph_layout.count())):
            w = self.graph_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

    def _mostrar_placeholder(self, texto: str, error: bool = False):
        self._limpiar_graph_frame()
        lbl = QLabel(texto)
        lbl.setStyleSheet(
            f"color: {'#FF6B6B' if error else '#333'};"
            "font-size: 13px; font-style: italic;"
        )
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_layout.addWidget(lbl)

    def _mostrar_preview(self, resultado):
        """Preview compacta del resultado que queda en el panel tras cerrar el diálogo."""
        self._limpiar_graph_frame()
        if isinstance(resultado, Figure):
            canvas = FigureCanvas(resultado)
            canvas.setMaximumHeight(220)
            self.graph_layout.addWidget(canvas)
            canvas.draw()
            lbl = QLabel("Presiona  ▶ Ejecutar  para abrir en pantalla completa")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #444; font-size: 11px; margin-top: 4px;")
            self.graph_layout.addWidget(lbl)
        else:
            texto = str(resultado)
            recortado = texto[:300] + ("…" if len(texto) > 300 else "")
            lbl = QLabel(recortado)
            lbl.setStyleSheet(
                "color: #CCC; font-family: 'Courier New', monospace;"
                "font-size: 12px; padding: 10px;"
            )
            lbl.setWordWrap(True)
            self.graph_layout.addWidget(lbl)

    def _limpiar_panel(self):
        self._carpeta_sel = ""
        self._script_sel  = ""
        self.lbl_titulo.setText("Selecciona un script")
        self.lbl_meta.setText("")
        self.lbl_consulta.setText("—")
        self.lbl_consulta.setStyleSheet("""
            background-color: #181818; border: 1px solid #2A2A2A;
            border-radius: 8px; padding: 14px; color: #666; font-size: 13px;
        """)
        self.btn_ejecutar.setEnabled(False)
        self._mostrar_placeholder("Selecciona un script y presiona  ▶ Ejecutar")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # DataFrame de prueba para correr la pantalla de forma independiente
    df_prueba = pd.DataFrame({
        "Region": ["Norte", "Sur", "Este", "Oeste"],
        "Ventas": [120, 95, 140, 80],
    })
    window = Script(dataframe=df_prueba)
    window.show()
    sys.exit(app.exec())