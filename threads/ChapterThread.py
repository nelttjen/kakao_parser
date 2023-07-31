import math

import pyquery as pq
import requests

from PyQt5.QtCore import QThread, pyqtSignal


def clear_int(_str):
    _new = ''
    for i in _str:
        if i == '화':
            break
        if i in '0123456789':
            _new += i
    return _new


def get_chapter_list(chapter_id: int, _session: requests.Session):
    endpoint = 'https://page.kakao.com/graphql'
    header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
              "Authority": "page.kakao.com", "Origin": "https://page.kakao.com", "Referer": f"https://page.kakao.com/content/{chapter_id}"}

    full_list = []
    for i in range(0, 1000, 20):
        query = {
            "query": "query contentHomeProductList($after: String, $before: String, $first: Int, $last: Int, $seriesId: Long!, $boughtOnly: Boolean, $sortType: String) {\n contentHomeProductList(\n seriesId: $seriesId\n after: $after\n before: $before\n first: $first\n last: $last\n boughtOnly: $boughtOnly\n sortType: $sortType\n ) {\n totalCount\n pageInfo {\n hasNextPage\n endCursor\n hasPreviousPage\n startCursor\n __typename\n }\n selectedSortOption {\n id\n name\n param\n __typename\n }\n sortOptionList {\n id\n name\n param\n __typename\n }\n edges {\n cursor\n node {\n ...SingleListViewItem\n __typename\n }\n __typename\n }\n __typename\n }\n}\n\nfragment SingleListViewItem on SingleListViewItem {\n id\n type\n thumbnail\n showPlayerIcon\n isCheckMode\n isChecked\n scheme\n row1 {\n badgeList\n title\n __typename\n }\n row2\n row3\n single {\n productId\n ageGrade\n id\n isFree\n thumbnail\n title\n slideType\n operatorProperty {\n isTextViewer\n __typename\n }\n __typename\n }\n isViewed\n purchaseInfoText\n eventLog {\n ...EventLogFragment\n __typename\n }\n}\n\nfragment EventLogFragment on EventLog {\n fromGraphql\n click {\n layer1\n layer2\n setnum\n ordnum\n copy\n imp_id\n imp_provider\n __typename\n }\n eventMeta {\n id\n name\n subcategory\n category\n series\n provider\n series_id\n type\n __typename\n }\n viewimp_contents {\n type\n name\n id\n imp_area_ordnum\n imp_id\n imp_provider\n imp_type\n layer1\n layer2\n __typename\n }\n customProps {\n landing_path\n view_type\n toros_imp_id\n toros_file_hash_key\n toros_event_meta_id\n content_cnt\n event_series_id\n event_ticket_type\n play_url\n banner_uid\n __typename\n }\n}\n",
            "operationName": "contentHomeProductList",
            "variables": {"seriesId": chapter_id, "after": f"{i}", "boughtOnly": False, "sortType": "desc"}}
        response = _session.post(endpoint, headers=header, json=query)
        if response.status_code == 200:
            items = response.json()['data']['contentHomeProductList']['edges']
            if items:
                full_list.extend(items)
            else:
                break
        else:
            print(response.status_code)
            print(response.text)

    array = []
    no_nums = 0
    used = []

    for i, item in enumerate(full_list[::-1]):
        chapter = clear_int(item["node"]["row1"]["title"])
        if chapter:
            number = chapter
        else:
            number = no_nums
            no_nums -= 1
        if f'{number} - {item["node"]["single"]["productId"]} - {item["node"]["row1"]["title"]}' in array:
            continue
        if str(number) in used:
            number = str(number) + '_'
        used.append(str(number))
        _string = f'{number} - {item["node"]["single"]["productId"]} - {item["node"]["row1"]["title"]}'
        array.append(_string)
    return sorted(array, key=lambda x: int(x.split(' - ')[0]))


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

        # self.items = []

    def run(self) -> None:
        self.fetching.emit()
        chapters = get_chapter_list(self.title, self.session)
        if chapters:
            self.done.emit()
            self.done_str.emit(';'.join(chapters))
        else:
            self.error.emit()
    # def run(self) -> None:
    #     self.sending.emit()
    #     endpoint = 'https://api2-page.kakao.com/api/v5/store/singles'
    #     link = endpoint + f'?page=0&direction=abs&page_size=20&without_hidden=true&' \
    #                                          f'seriesid={self.title}'
    #     headers = {
    #         'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    #                       '(KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'
    #     }
    #     total = self.session.post(link, headers=headers)
    #     print(total.text)
    #     total = total.json()
    #     if total.get('total_count') > 0:
    #         self.fetching.emit()
    #         count = 0
    #         while True:
    #             chapters = self.session.post(endpoint +
    #                                          f'?page={count}&direction=abs&page_size=20'
    #                                          f'&without_hidden=true&seriesid={self.title}',
    #                                          headers=headers).json().get('singles')
    #             if not chapters:
    #                 break
    #             for j, item in enumerate(chapters):
    #                 self.items.append(f'{item.get("id")} - Глава {item.get("order_value")} - {item.get("page_count")} Страниц '
    #                                   f'- {item.get("title")}')
    #             count += 1
    #         self.done.emit()
    #         self.done_str.emit(';'.join(self.items))
    #     else:
    #         self.error.emit()
