
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTextEdit, QPushButton


class CookieDialogUI:
    def __init__(self):
        self.cookie_edit = QTextEdit(self)
        self.cookie_edit.setPlaceholderText('Скопируйте Cookie с браузера сюда')
        self.cookie_edit.setGeometry(25, 25, 550, 300)

        self.btn_ok = QPushButton(self)
        self.btn_ok.setText('OK')
        self.btn_ok.setGeometry(600 - 25 - 100, 400 - 25 - 40, 100, 40)

        self.btn_not = QPushButton(self)
        self.btn_not.setText('CANCEL')
        self.btn_not.setGeometry(25, 335, 100, 40)


class CookieDialog(QDialog, CookieDialogUI):
    def __init__(self, parent):
        super(CookieDialog, self).__init__(parent, Qt.WindowCloseButtonHint)

        self.initUI()

    def initUI(self):
        self.setFixedSize(600, 400)
        self.setWindowTitle('Cookie')

        self.btn_ok.clicked.connect(self.accept)
        self.btn_not.clicked.connect(self.reject)
