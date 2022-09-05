import os
import shutil

from PyQt5.QtCore import QThread, pyqtSignal
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}


class DownloadThread(QThread):
    item_signal = pyqtSignal(int)
    chapter_init = pyqtSignal(str)
    chapter_start = pyqtSignal(str)
    error_chapter = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self, parent, driver, session, items, root):
        super(DownloadThread, self).__init__(parent=parent)
        self.__parent = parent
        self.driver: Chrome = driver
        self.session = session
        self.items = items
        self.root = root

    def run(self) -> None:
        if not os.path.isdir(self.root):
            os.mkdir(self.root)
        for item in self.items:
            if os.path.isdir(self.root + f'\\{item[1]}'):
                shutil.rmtree(self.root + f'\\{item[1]}')
            os.mkdir(self.root + f'\\{item[1]}')
            self.chapter_init.emit(item[1])
            self.driver.get(f'https://page.kakao.com/viewer?productId={item[0]}')
            QThread.msleep(10000)
            css_items = self.driver.find_elements(By.CSS_SELECTOR, '.css-88gyaf > div > img')
            self.chapter_start.emit(item[1])
            if len(css_items) > 0:
                for i, itm in enumerate(css_items):
                    link = itm.get_attribute('src')
                    resp = self.session.get(link, headers=headers)
                    with open(self.root + f'\\{item[1]}\\{i + 1}.jpg', 'wb') as jpg:
                        jpg.write(resp.content)
                    self.item_signal.emit(1)
            else:
                self.item_signal.emit(int(item[2]))
                self.error_chapter.emit(item[1])
                shutil.rmtree(self.root + f'\\{item[1]}')
        self.done.emit()

    def download_chapter(self, c_id):
        pass
