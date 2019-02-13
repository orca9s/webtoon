import os
import re

import requests
from bs4 import BeautifulSoup

from data import Episode, Webtoon, WebtoonNotExist


class Crawler:
    def __init__(self):
        self._webtoon_dict = {}

    def get_html(self):
        """
        전체 웹툰 목록의 HTML을 리턴한다.
        만약에 파일로 저장되어 있다면, 해당 내용을 읽어온다.
        파일로 저장되어 있지 않다면, requests를 사용해 웹에서 받아와 리턴한다.
        :return:
        """
        # HTTP요청을 매번 할 필요가 없음
        # 파일로 저장해두고 필요할 때 갱신
        root = os.path.dirname(os.path.abspath(__file__))
        dir_path = os.path.join(root, 'saved_data')
        file_path = os.path.join(dir_path, 'weekday.html')

        if os.path.exists(file_path):
            # 경로가 존재하면
            # 해당 경로의 파일을 읽기
            html = open(file_path, 'rt').read()
        else:
            # 경로가 존재하지 않으면
            # HTTP요청결과를 가져오고, 이후 다시 요청시 읽기위한 파일 기록
            # 파일을 저장할 폴더를 생성, 이미 존재하는 경우 무시하기 위해 exist_ok인수추가
            os.makedirs(dir_path, exist_ok=True)
            response = requests.get('https://comic.naver.com/webtoon/weekday.nhn')
            html = response.text
            open(file_path, 'wt').write(html)
        return html

    @property
    def webtoon_dict(self):
        # 웹툰이 있는경우 그대로 리턴
        # 없으면 실행 없는경우는 초기화 메서드가 실행될 때
        if not self._webtoon_dict:
            html = self.get_html()
            soup = BeautifulSoup(html, 'lxml')
            col_list = soup.select_one('div.list_area.daily_all').select('.col')
            li_list = []
            for col in col_list:
                col_li_list = col.select('.col_inner ul > li')
                li_list.extend(col_li_list)

            for li in li_list:
                href = li.select_one('a.title')['href']
                m = re.search(r'titleId=(\d+)', href)
                webtoon_id = m.group(1)
                title = li.select_one('a.title').get_text(strip=True)
                url_thumbnail = li.select_one('.thumb > a > img')['src']

                if title not in self._webtoon_dict:
                    new_webtoon = Webtoon(webtoon_id, title, url_thumbnail)
                    self._webtoon_dict[title] = new_webtoon

        return self._webtoon_dict

    def get_webtoon(self, title):
        """
        title이 제목인 webtoon객체를 가져옴
        :param title:
        :return:
        """
        # 여기서 _webtoon_dict를 안불르는 이유는 아래의 코드를 실행하면
        # 위의 property함수가 실행되고 그 함수가 _webtoon_dict를 리턴
        try:
            return self.webtoon_dict[title]
        except KeyError:
            raise WebtoonNotExist(title)

    def show_webtoon_list(self):
        for title, webtoon in self.webtoon_dict.items():
            print(title)


if __name__ == '__main__':
    # 붕어빵 틀
    crawler = Crawler()
    # 만들어질 붕어
    # crawler.show_webtoon_list()
    w = crawler.get_webtoon('신의 탑')
    print(w.episode_dict)


