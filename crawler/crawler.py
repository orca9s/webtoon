import os
import re

import requests
from bs4 import BeautifulSoup

from data import Episode, Webtoon


class Crawler:
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
        file_path = os.path.join(root, 'saved_data', 'weekday.html')

        if os.path.exists():
            # 경로가 존재하면
            # 해당 경로의 파일을 읽기
            html = open(file_path, 'rt').read()
        else:
            # 경로가 존재하지 않으면
            # HTTP요청결과를 가져오고, 이후 다시 요청시 읽기위한 파일 기록
            response = requests.get('https://comic.naver.com/webtoon/weekday.nhn')
            html = response.text
            open(file_path, 'wt').write()
        return html

    def show_webtoon_list(self):
        """
        전체 웹툰 제목을 출력해줌

        1. requests를 사용해서 웹툰 목록 URL의 내용을 가져옴
        2. BeautifulSoup을 사용해서 가져온 HTML데이터를 파싱
        3. 파싱한 결과를 사용해서 Webtoon클래스 인스턴스들을 생성
        4. 생성한 인스턴스 목록을 dict에 제목을 key를 사용해서 할당
        5. dict를 순회하며 제목들을 출력
       :return:
        """
        html = self.get_html()
        soup = BeautifulSoup(html, 'lxml')
        col_list = soup.select_one('div.list_area.daily_all').select('.col')
        li_list = []
        for col in col_list:
            col_li_list = col.select('.col_inner ul > li')
            li_list.extend(col_li_list)

        webtoon_dict = {}
        for li in li_list:
            href = li.select_one('a.title')['href']
            m = re.search(r'titleId=(\d+)', href)
            webtoon_id = m.group(1)
            title = li.select_one('a.title').get_text(strip=True)
            url_thumbnail = li.select_one('.thumb > a > img')['src']

            if title not in webtoon_dict:
                new_webtoon = Webtoon(webtoon_id, title, url_thumbnail)
                webtoon_dict[title] = new_webtoon

        for title, webtoon in webtoon_dict.items():
            print(title)


if __name__ == '__main__':
    # 붕어빵 틀
    crawler = Crawler()
    # 만들어질 붕어
    crawler.show_webtoon_list()


