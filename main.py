import json
import os
import shutil
import sys

import requests
from requests import Session
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By

from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QPushButton

from threads.WebDriver import LoginThread, ProcessThread
from threads.DownloadThread import DownloadThread
from utils import CONFIG_DEFAULT
from widgets.ChapterChoose import ChapterChoose


FIRST = False


class Window(QMainWindow):
    def __init__(self, opt):
        super().__init__()

        self.VERSION = '1.1 beta'
        self.APP_NAME = 'Kakao parser'

        self.DEST_FOLDER = ''
        self.DEST_SET = False
        self.logged = False

        self.choosed_now = []
        self.title_now = None

        self.is_working = False

        self.session = Session()

        uic.loadUi('./ui/main.ui', self)
        self.setWindowTitle(f'{self.APP_NAME} v{self.VERSION}')
        self.setWindowIcon(QIcon('./ui/favicon.ico'))
        self.setObjectName('MainWindow')
        self.setFixedSize(self.width(), self.height())

        self.connect_buttons()
        self.start_login()

        self.opt = opt
        self.set_settings(opt)

        self.test_btn = QPushButton()
        self.download_bar.setVisible(False)

    def connect_buttons(self):
        self.chose_dest.clicked.connect(self.set_folder)
        self.login_proc.clicked.connect(self.proc_login)
        self.update_login_creds.clicked.connect(self.proc_login)

        self.choose_chapter.clicked.connect(self.choose_chapters)
        self.download_btn.clicked.connect(self.download_chapters)

    def set_settings(self, opt):
        if opt.get('save_directory'):
            self.DEST_FOLDER = opt.get('save_directory')
            self.DEST_SET = True
            self.set_dest_chosed()

    def start_login(self):
        login_t = LoginThread(self, driver)
        login_t.start()
        QMessageBox.information(self, 'Info', 'Сейчас появится окно с авторизацией\n'
                                              'После входа в аккаунт нажмите на кнопку "Завершить логин" сверху\n'
                                              'P.S. После пропажи окна подождите 3-4 секунды перед нажатием')

    def login_cookie(self):
        global FIRST
        with open(f'temp\\cookies.json', 'r', encoding='utf-8') as json_f:
            load_to_session(json_f, self.session)
        self.login_proc.hide()
        QMessageBox.information(self, 'Info', 'Вход завершен')
        self.logged = True
        if not FIRST:
            FIRST = True
            self.update_login_creds.setEnabled(True)

    def proc_login(self):
        if not self.is_working:
            proc_t = ProcessThread(self, driver)
            proc_t.done.connect(self.login_cookie)
            proc_t.start()

    def choose_chapters(self):
        if not self.logged:
            QMessageBox.critical(self, 'Ошибка', 'Сначала завершите логин', QMessageBox.Ok)
            return
        text = self.chapter_id.text()
        if text.startswith('https://'):
            text = text.replace('https://page.kakao.com/home?seriesId=', '')
        try:
            text = int(text)
        except ValueError:
            QMessageBox.critical(self, 'Ошибка', 'Неправильная ссылка', QMessageBox.Ok)
            return
        dialog = ChapterChoose(self, text, self.session)
        dialog.show()
        val, val2 = dialog.exec_()
        if val:
            self.chapters_selected_int.setText(str(len(val)))
            self.download_btn.setEnabled(True)
            self.choosed_now = val
            self.title_now = val2
            self.chapter_id.setText(str(self.title_now))

    def download_chapters(self):
        if self.is_working:
            return
        if not self.DEST_SET:
            QMessageBox.critical(self, 'Ошибка', 'Сначала укажите место, куда будут сохраняться\n'
                                                 'скачанные главы (правый верхний угол)')
            return
        if self.choosed_now and self.title_now:
            self.is_working = True
            total_download = sum(int(i[2]) for i in self.choosed_now)
            self.download_bar.setMaximum(total_download)
            self.download_bar.setValue(0)
            thread = DownloadThread(self, driver, self.session, self.choosed_now,
                                    self.DEST_FOLDER + f'\\{self.title_now}')
            thread.chapter_init.connect(lambda x: self.download_status_info.setText(f'Инициализация загрузки - Глава {x}'))
            thread.chapter_start.connect(lambda x: self.download_status_info.setText(f'Загрузка - Глава {x}'))
            thread.buy_chapter.connect(lambda x: self.download_status_info.setText(f'Покупка - Глава {x}'))
            thread.error_chapter.connect(lambda x:
                                         QMessageBox.critical(self, 'Ошибка загрузки',
                                                                    f'Невозможно загрузить {x} главу\n'                       
                                                                    f'Проверьте, чтобы она была доступна на аккаунте\n'
                                                                    f'Или хватало монет для её покупки'))
            thread.item_signal.connect(lambda x: self.download_bar.setValue(self.download_bar.value() + x))
            thread.done.connect(self.download_finish)
            thread.start()

    def download_finish(self):
        QMessageBox.information(self, 'Info', 'Очередь создана. Загрузка вскоре завершится.')
        self.download_status_info.setText('Очередь создана')
        self.is_working = False

    def set_folder(self):
        file = str(QFileDialog.getExistingDirectory(self, "Выбор папки..."))
        if file:
            try:
                with open(f'{file}\\test.temp', 'w'):
                    pass
                try:
                    os.remove(f'{file}\\test.temp')
                except:
                    pass
                self.DEST_FOLDER = file
                self.DEST_SET = True
                self.opt['save_directory'] = file
                self.save_opt()
                self.set_dest_chosed()
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка', f'Нет прав на запись файлов в эту папку\n{e}', QMessageBox.Ok)

    def save_opt(self):
        with open('.\\config.json', 'w', encoding='utf-8') as file:
            json.dump(self.opt, file)

    def set_dest_chosed(self):
        self.chose_dest_label.setText('Выбрана')


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def init():
    os.mkdir('.\\temp') if not os.path.exists('.\\temp') else None
    if not os.path.exists('.\\config.json'):
        with open(f".\\config.json", 'w', encoding='utf-8') as def_c:
            json.dump(CONFIG_DEFAULT, def_c)
            setts = CONFIG_DEFAULT
    else:
        with open(f'.\\config.json', 'r', encoding='utf-8') as load_j:
            setts = json.load(load_j)
    if setts.get('save_directory'):
        try:
            os.mkdir(setts.get('save_directory'))
        except Exception as e:
            print(e)
    return setts


def load_to_session(file, session):
    try:
        data = json.load(file)
        for i in data:
            session.cookies.set(name=i['name'], value=i['value'], domain=i['domain'])
    except:
        return


if __name__ == '__main__':
    settings = init()
    driver = Chrome('chromedriver.exe')
    driver.set_window_rect(0, -2000, 837, 1000)
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    f = Window(settings)
    f.show()
    app.exec_()
    try:
        driver.quit()
        sys.exit()
    except:
        sys.exit()
