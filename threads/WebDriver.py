import json
import time


from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from requests import Session

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QWidget


class LoginThread(QThread):

    def __init__(self, parent, driver):
        super().__init__(parent=parent)
        self.__parent = parent
        self.driver = driver

    def run(self) -> None:
        self.driver.get('https://page.kakao.com/main')
        test = self.driver.find_element(By.CSS_SELECTOR, '.css-vurnku')
        test.click()


class ProcessThread(QThread):

    done = pyqtSignal()

    def __init__(self, parent, driver):
        super().__init__(parent=parent)
        self.__parent = parent
        self.driver = driver

    def run(self) -> None:
        self.driver.get('https://page.kakao.com/main')
        cookies = get_cookie_from_driver(self.driver, 'kakao.com')
        with open(f'temp\\cookies.json', 'w', encoding='utf-8') as json_f:
            json.dump(cookies, json_f)
        self.done.emit()
        # self.driver.quit()


def get_cookie_from_driver(dr, domain):
    cookies = []
    for i in dr.get_cookies():
        if domain in i['domain']:
            cookies.append({
                'domain': i['domain'],
                'name': i['name'],
                'value': i['value'],
            })
    return cookies
