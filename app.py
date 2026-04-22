import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication

from gui.login import LoginScreen
from gui.Form_Consulta import Consulta


def main():
    app = QApplication(sys.argv)

    login = LoginScreen()

    def on_login(username, role):
        login.close()
        abrir_app(username, role)

    login.login_exitoso.connect(on_login)
    login.show()

    sys.exit(app.exec())


def abrir_app(username: str, role: str):
    global _consulta

    # Consulta recibe el rol para decidir qué botones mostrar
    # y qué páginas incluir en el QStackedWidget
    _consulta = Consulta(role=role)
    _consulta.setWindowTitle(f"DataPipeline AI — {username}")

    def ir_consulta():
        _consulta.switch_tab(0)

    def ir_scripts():
        _consulta.switch_tab(3)

    def ir_admin():
        _consulta.switch_tab(4)

    _consulta.set_nav_callbacks(ir_consulta, ir_scripts, ir_admin)
    _consulta.show()


if __name__ == "__main__":
    main()