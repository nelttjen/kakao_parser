from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic

from threads.ChapterThread import ChapterThread


class ChapterChoose(QDialog):
    def __init__(self, parent, chapter_id, session):
        super().__init__(parent, Qt.WindowCloseButtonHint)
        uic.loadUi('ui\\chapter.ui', self)

        self.chapter_id = chapter_id
        self.session = session
        self.selected = []

        self.init()

        self.confirm.clicked.connect(self.done_select)

    def init(self):
        self.setWindowTitle('Выбор глав')
        self.info_label_2.setText(str(self.chapter_id))
        self.status_label_2.setText('Подготовка...')

        thread = ChapterThread(self, self.chapter_id, self.session)
        thread.sending.connect(lambda: self.status_label_2.setText('Отправка запроса...'))
        thread.fetching.connect(lambda: self.status_label_2.setText('Сбор информации о главах...'))
        thread.done.connect(lambda: self.status_label_2.setText('Готово! Выберите нужные главы ниже'))
        thread.done_str.connect(self.done_set_view)
        thread.error.connect(self.error_set_view)
        thread.start()

    def error_set_view(self):
        QMessageBox.critical(self, 'Ошибка', 'Что-то пошло не так, попробуйте ещё раз\n'
                                             'Скорее всего, указаного id не существует')
        self.status_label_2.setText('Ошибка!')
        self.reject()

    def done_set_view(self, text):
        chapters = text.split(';')
        for item in chapters:
            self.listWidget.addItem(item)

    def done_select(self):
        for item in self.listWidget.selectedItems():
            item_id, chapter, pages, _ = item.text().split(' - ')
            chapter = chapter.replace('Глава ', '')
            pages = pages.replace(' Страниц', '')
            self.selected.append([item_id, chapter, pages])
        self.accept()

    def exec_(self):
        super(ChapterChoose, self).exec_()
        return self.selected, self.chapter_id