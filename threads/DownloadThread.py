import copy
import os
import shutil

import requests
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from utils import DEBUG


def get_links_single(series_id: int, product_id: int, _session: requests.Session):
    # test 56422254 - 57307905
    curr_items = []
    query = {
        "query": "query viewerInfo($seriesId: Long!, $productId: Long!) {\n  viewerInfo(seriesId: $seriesId, productId: $productId) {\n    item {\n      ...SingleFragment\n      __typename\n    }\n    seriesItem {\n      ...SeriesFragment\n      __typename\n    }\n    prevItem {\n      ...NearItemFragment\n      __typename\n    }\n    nextItem {\n      ...NearItemFragment\n      __typename\n    }\n    viewerData {\n      ...TextViewerData\n      ...TalkViewerData\n      ...ImageViewerData\n      ...VodViewerData\n      __typename\n    }\n    displayAd {\n      ...DisplayAd\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SingleFragment on Single {\n  id\n  productId\n  seriesId\n  title\n  thumbnail\n  badge\n  isFree\n  ageGrade\n  state\n  slideType\n  lastReleasedDate\n  size\n  pageCount\n  isHidden\n  remainText\n  isWaitfreeBlocked\n  saleState\n  series {\n    ...SeriesFragment\n    __typename\n  }\n  serviceProperty {\n    ...ServicePropertyFragment\n    __typename\n  }\n  operatorProperty {\n    ...OperatorPropertyFragment\n    __typename\n  }\n  assetProperty {\n    ...AssetPropertyFragment\n    __typename\n  }\n}\n\nfragment SeriesFragment on Series {\n  id\n  seriesId\n  title\n  thumbnail\n  categoryUid\n  category\n  categoryType\n  subcategoryUid\n  subcategory\n  badge\n  isAllFree\n  isWaitfree\n  is3HoursWaitfree\n  ageGrade\n  state\n  onIssue\n  authors\n  pubPeriod\n  freeSlideCount\n  lastSlideAddedDate\n  waitfreeBlockCount\n  waitfreePeriodByMinute\n  bm\n  saleState\n  serviceProperty {\n    ...ServicePropertyFragment\n    __typename\n  }\n  operatorProperty {\n    ...OperatorPropertyFragment\n    __typename\n  }\n  assetProperty {\n    ...AssetPropertyFragment\n    __typename\n  }\n}\n\nfragment ServicePropertyFragment on ServiceProperty {\n  viewCount\n  readCount\n  ratingCount\n  ratingSum\n  commentCount\n  pageContinue {\n    ...ContinueInfoFragment\n    __typename\n  }\n  todayGift {\n    ...TodayGift\n    __typename\n  }\n  waitfreeTicket {\n    ...WaitfreeTicketFragment\n    __typename\n  }\n  isAlarmOn\n  isLikeOn\n  ticketCount\n  purchasedDate\n  lastViewInfo {\n    ...LastViewInfoFragment\n    __typename\n  }\n  purchaseInfo {\n    ...PurchaseInfoFragment\n    __typename\n  }\n}\n\nfragment ContinueInfoFragment on ContinueInfo {\n  title\n  isFree\n  productId\n  lastReadProductId\n  scheme\n  continueProductType\n  hasNewSingle\n  hasUnreadSingle\n}\n\nfragment TodayGift on TodayGift {\n  id\n  uid\n  ticketType\n  ticketKind\n  ticketCount\n  ticketExpireAt\n  ticketExpiredText\n  isReceived\n}\n\nfragment WaitfreeTicketFragment on WaitfreeTicket {\n  chargedPeriod\n  chargedCount\n  chargedAt\n}\n\nfragment LastViewInfoFragment on LastViewInfo {\n  isDone\n  lastViewDate\n  rate\n  spineIndex\n}\n\nfragment PurchaseInfoFragment on PurchaseInfo {\n  purchaseType\n  rentExpireDate\n  expired\n}\n\nfragment OperatorPropertyFragment on OperatorProperty {\n  thumbnail\n  copy\n  torosImpId\n  torosFileHashKey\n  isTextViewer\n}\n\nfragment AssetPropertyFragment on AssetProperty {\n  bannerImage\n  cardImage\n  cardTextImage\n  cleanImage\n  ipxVideo\n}\n\nfragment NearItemFragment on NearItem {\n  productId\n  slideType\n  ageGrade\n  isFree\n  title\n  thumbnail\n}\n\nfragment TextViewerData on TextViewerData {\n  type\n  atsServerUrl\n  metaSecureUrl\n  contentsList {\n    chapterId\n    contentId\n    secureUrl\n    __typename\n  }\n}\n\nfragment TalkViewerData on TalkViewerData {\n  type\n  talkDownloadData {\n    dec\n    host\n    path\n    talkViewerType\n    __typename\n  }\n}\n\nfragment ImageViewerData on ImageViewerData {\n  type\n  imageDownloadData {\n    ...ImageDownloadData\n    __typename\n  }\n}\n\nfragment ImageDownloadData on ImageDownloadData {\n  files {\n    ...ImageDownloadFile\n    __typename\n  }\n  totalCount\n  totalSize\n  viewDirection\n  gapBetweenImages\n  readType\n}\n\nfragment ImageDownloadFile on ImageDownloadFile {\n  no\n  size\n  secureUrl\n  width\n  height\n}\n\nfragment VodViewerData on VodViewerData {\n  type\n  vodDownloadData {\n    contentId\n    drmType\n    endpointUrl\n    width\n    height\n    duration\n    __typename\n  }\n}\n\nfragment DisplayAd on DisplayAd {\n  sectionUid\n  bannerUid\n  treviUid\n  momentUid\n}\n",
        "operationName": "viewerInfo",
        "variables": {
            "seriesId": series_id,
            "productId": product_id
        }
    }
    endpoint = 'https://page.kakao.com/graphql'
    header = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        "Authority": "page.kakao.com",
        "Origin": "https://page.kakao.com",
        "Referer": f"https://page.kakao.com/content/{series_id}/viewer/{product_id}"
    }
    result = _session.post(endpoint, headers=header, json=query)
    try:
        print(result.json())
        for item in result.json()['data']['viewerInfo']['viewerData']['imageDownloadData']['files']:
            if isinstance(item, list):
                for item2 in item:
                    curr_items.append(item2['secureUrl'])
            else:
                curr_items.append(item['secureUrl'])
        return curr_items
    except Exception as e:
        if DEBUG:
            print(e)
        return []


class DownloadThread(QThread):
    item_signal = pyqtSignal(int)
    chapter_init = pyqtSignal(str)
    chapter_start = pyqtSignal(str)
    buy_chapter = pyqtSignal(str)
    error_chapter = pyqtSignal(str)
    error_chapter_page = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self, parent, driver, session, items, root, selected):
        super(DownloadThread, self).__init__(parent=parent)
        self.__parent = parent
        self.driver: Chrome = driver
        self.session = session
        self.items = items
        self.root = root
        self.selected = selected

        self.threads = []

    def failed(self, item):
        # self.item_signal.emit(int(item[2]))
        self.error_chapter.emit(item[0])
        shutil.rmtree(self.root + f'/{item[1]}') if os.path.exists(self.root + f'/{item[1]}') else None

    def run(self) -> None:
        if not os.path.isdir(self.root):
            os.mkdir(self.root)
        for item in self.items:
            self.chapter_init.emit(item[0])
            QThread.msleep(3000)
            links = get_links_single(self.selected, item[1], self.session)
            if DEBUG:
                print(links)
            if links:
                self.download_chapter(item, links)
            else:
                self.failed(item)
        self.done.emit()

    # def run2(self) -> None:
    #     if not os.path.isdir(self.root):
    #         os.mkdir(self.root)
    #     for item in self.items:
    #         if not self.download_chapter(item):
    #             self.buy_chapter.emit(item[1])
    #             try:
    #                 elem = self.driver.find_element(By.CSS_SELECTOR, '.css-1bfkcue-Button')
    #                 if elem:
    #                     elem.click()
    #                     QThread.msleep(3000)
    #                     try:
    #                         btn = self.driver.find_elements(By.CSS_SELECTOR,
    #                                                         '.css-gecc4z-DialogButton-TicketBuyAndUseDialog')
    #                     except Exception:
    #                         if not self.download_chapter(item):
    #                             print('failed2')
    #                             self.failed(item)
    #                         continue
    #                     btn[0].click()
    #                     QThread.msleep(5000)
    #                     self.driver.get(f'https://page.kakao.com/content/{self.selected}/viewer/{item[0]}')
    #                     if not self.download_chapter(item):
    #                         self.failed(item)
    #                         print('failed 1')
    #                 else:
    #
    #                     print('failed 3')
    #                     self.failed(item)
    #             except Exception as e:
    #                 print('failed 4')
    #                 print(e)
    #                 self.failed(item)
    #     self.done.emit()

    def download_chapter(self, item, links):
        self.chapter_start.emit(item[0])
        if os.path.isdir(self.root + f'/{item[0]}'):
            shutil.rmtree(self.root + f'/{item[0]}')
        os.mkdir(self.root + f'/{item[0]}')
        print(f'\nГлава {item[0]} - старт')
        for i, link in enumerate(links):
            QThread.msleep(200)
            save_to = self.root + f'/{item[0]}/{i + 1}.jpg'
            cpap_id, chap_page = item[0], i + 1
            thread = QThread()
            worker = RequestThread(link, save_to, cpap_id, chap_page, self.session)

            worker.moveToThread(thread)

            # worker.error.connect(lambda x: self.error_chapter_page.emit(x))
            # worker.done.connect(lambda: print('123'))
            # worker.done_qt.connect(thread.quit)

            thread.started.connect(worker.run)
            thread.start()
            self.threads.append((thread, worker))

    # def download_chapter2(self, c_id):
    #     if os.path.isdir(self.root + f'/{c_id[1]}'):
    #         shutil.rmtree(self.root + f'/{c_id[1]}')
    #     os.mkdir(self.root + f'\\{c_id[1]}')
    #     self.chapter_init.emit(c_id[1])
    #     self.driver.get(f'https://page.kakao.com/content/{self.selected}/viewer/{c_id[0]}')
    #     QThread.msleep(10000)
    #     try:
    #         self.driver.find_element(By.CSS_SELECTOR, '.css-znhlra-ViewerSlideSwiperMain')
    #         print(f'\nButton chapter detected: {c_id[0]} - ch{c_id[1]}')
    #         QThread.msleep(500)
    #         self.driver.find_element(By.CSS_SELECTOR, '.css-u0e2y5-ViewerContainer').click()
    #         QThread.msleep(500)
    #         self.driver.find_elements(By.CSS_SELECTOR,
    #                                   '.css-psy1a9-List-List-ViewerSettingScroll'
    #                                   'ableItem-ViewerSettingScrollableItem > li')[1].click()
    #     except Exception as e:
    #         pass
    #     css_items = self.driver.find_elements(By.CSS_SELECTOR, '.css-3q7n7r-ScrollImageViewerImage')
    #     self.chapter_start.emit(c_id[1])
    #     if len(css_items) > 0:
    #         print(f'\nГлава {c_id[1]} - старт')
    #         for i, itm in enumerate(css_items):
    #             QThread.msleep(150)
    #             try:
    #                 link = itm.get_attribute('src')
    #             except AttributeError:
    #                 link = itm
    #             save_to = self.root + f'\\{c_id[1]}\\{i + 1}.jpg'
    #             cpah_id, chap_page = c_id[1], i + 1
    #             thread = QThread()
    #             worker = RequestThread(link, save_to, cpah_id, chap_page, self.session)
    #
    #             worker.moveToThread(thread)
    #
    #             worker.error.connect(lambda x: self.error_chapter_page.emit(x))
    #             worker.done.connect(lambda: print('123'))
    #             worker.done_qt.connect(thread.quit)
    #
    #             thread.started.connect(worker.run)
    #             thread.start()
    #             self.threads.append((thread, worker))
    #
    #         return True
    #     return False


class RequestThread(QObject):

    done = pyqtSignal()
    done_qt = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, link, save_to, c_id, c_page, session=requests.Session()):
        super(RequestThread, self).__init__()
        self.link = link
        self.session = session

        self.c_id = c_id
        self.c_page = c_page
        self.save_to = save_to

    def run(self) -> None:
        # print(f'running {self.c_page}')
        headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
        try:
            # print(self.link)
            resp = self.session.get(self.link, headers=headers)
            # print(f'resp {self.c_page} got')
        except Exception:
            QThread.msleep(10000)
            success = False
            for _ in range(5):
                try:
                    resp = self.session.get(self.link, headers=headers)
                    if resp.status_code == 200:
                        success = True
                        break
                except Exception:
                    QThread.msleep(5000)
                    continue
            if not success:
                self.error.emit(f'Ошибка загрузки: \nГлава - {self.c_id}, \nСтраница - {self.c_page}')
        try:
            print(f"Глава {self.c_id} - {self.c_page}: {resp.status_code}")
            if resp.status_code == 200:
                with open(self.save_to, 'wb') as jpg:
                    jpg.write(resp.content)
                    self.done.emit()
                    self.done_qt.emit()
                    # print(f'writed {self.c_page} to {self.save_to}')
            else:
                with open(self.save_to.replace('.jpg', '') + '_error.jpg', 'wb'):
                    pass
        except:
            with open(self.save_to.replace('.jpg', '') + '_error.jpg', 'wb'):
                pass
        self.done.emit()
        self.done_qt.emit()