import math

import pyquery as pq
import requests

from PyQt5.QtCore import QThread, pyqtSignal

from utils.clear_int import get_clear_int


class ChapterThread(QThread):

    sending = pyqtSignal()
    fetching = pyqtSignal()
    done = pyqtSignal()
    done_str = pyqtSignal(str)
    error = pyqtSignal()

    def __init__(self, parent, title, session):
        super(ChapterThread, self).__init__(parent=parent)
        self.__parent = parent
        self.title = title
        self.session = session

        self.items = []

    def run(self) -> None:
        self.sending.emit()
        endpoint = 'https://api2-page.kakao.com/api/v5/store/singles'
        link = endpoint + f'?page=0&direction=abs&page_size=20&without_hidden=true&' \
                                             f'seriesid={self.title}'
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
        }
        total = self.session.post(link, headers=headers)
        total = total.json()
        if total.get('total_count') > 0:
            self.fetching.emit()
            count = 0
            while True:
                chapters = self.session.post(endpoint +
                                             f'?page={count}&direction=abs&page_size=20'
                                             f'&without_hidden=true&seriesid={self.title}',
                                             headers=headers).json().get('singles')
                if not chapters:
                    break
                for j, item in enumerate(chapters):
                    self.items.append(f'{item.get("id")} - Глава {item.get("order_value")} - {item.get("page_count")} Страниц '
                                      f'- {item.get("title")}')
                count += 1
            self.done.emit()
            self.done_str.emit(';'.join(self.items))
        else:
            self.error.emit()

