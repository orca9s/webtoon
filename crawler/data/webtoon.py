import re
from collections import OrderedDict

import requests
from bs4 import BeautifulSoup

from . import Episode

__all__ = (
    'Webtoon',
    'WebtoonNotExist',
)


class Webtoon:
    TEST_WEBTOON_ID = 714843
    EPISODE_LIST_BASE_URL = 'https://comic.naver.com/webtoon/list.nhn'

    def __init__(self, webtoon_id, title, url_thumbnail):
        self.webtoon_id = webtoon_id
        self.title = title
        self.url_thumbnail = url_thumbnail
        self._episode_dict = OrderedDict()

    def __repr__(self):
        return self.title

    def get_episode_list_url_params_dict(self, **kwargs):
        # 기본적으로 {'titleId': <자신의 webtoon_id>} 인 dict를 리턴
        # 키워드인자가 주어지면 해당 키워드 인자를 추가한 dict를 리턴
        # 기본 dict뒤에 page넘버가 붙은 딕트를 리턴시킴
        params = {'titleId': self.webtoon_id}
        # dict 두개를 합칠 때 사용
        params.update(kwargs)
        return params

    @property
    def episode_dict(self):
        # 특정 페이지의 에피소드들을 dict에 담아서 리턴해줌
        # 리턴된 dict를 webtoon클래스의 self._episode_dict에 업데이트 시켜준다.
        def get_page_episode_dict(page):
            """

            :param page: 크롤링 할 페이지
            :return: {'has_next': <다음 페이지가 있는지>',
                    'episode_dict': episode_id를 키, Episode인스턴스를 값으로 쓰는 dict
            """
            # 위에서 만든 get_episode_list_url_params_dict에서 리턴된 dict를 사용,
            # requests를 이용한 요청에 GET parameters를 전달
            response = requests.get(
                self.EPISODE_LIST_BASE_URL,
                params=self.get_episode_list_url_params_dict(page=page)
            )
            soup = BeautifulSoup(response.text, 'lxml')

            # 이 page에 해당하는 Episode들을 담을 dict
            page_episode_dict = OrderedDict()

            # 에피소드 목록이 table.viewList의 각 'tr'요소 하나씩에 해당함
            table = soup.select_one('table.viewList')
            tr_list = table.select('tr')[1:]

            for tr in tr_list:
                # 이 루프 내부의 'tr'하나당 에피소드 하나를 만들어야 함
                try:
                    # 데이터 파싱
                    td_list = tr.select('td')
                    href = td_list[0].select_one('a')['href']
                    no = re.search(r'no=(\d+)', href).group(1)
                    url_thumbnail = td_list[0].select_one('img')['src']
                    title = td_list[1].select_one('a').get_text(strip=True)
                    rating = td_list[2].select_one('strong').get_text()
                    created_date = td_list[3].get_text(strip=True)

                    # 파싱한 데이터로 새 Episode인스턴스 생성
                    episode = Episode(
                        episode_id=no,
                        title=title,
                        url_thumbnail=url_thumbnail,
                        rating=rating,
                        created_date=created_date
                    )

                    # 리턴해줄 dict변수에  값 할당
                    page_episode_dict[no] = episode
                except:
                    # 위 파싱에 실패하는 경우에는 무시 (tr이 의도와 다르게 생겼을때 실패함)
                    # 기왕이면 실패 로그를 쌓으면 좋음 (어떤 웹툰의 몇 번째 페이지 몇 번째 row시도중 실패했다를 텍스트 파일에)
                    pass
            next_btn = soup.select_one('.paginate a.next')
            return {
                'episode_dict': page_episode_dict,
                'has_next': bool(next_btn),
            }
        if not self._episode_dict:
            # 비어있는 경우
            # self.url (목록페이지 URL)에 HTTP요청 후, 받은 결과를 파싱 시작
            page = 1
            while True:
                # while문을 반복하며 증가되는 page값을 사용해서 크롤링한 결과 dict및
                # 다음 페이지 존재여부를 가져옴
                result = get_page_episode_dict(page)
                page_episode_dict = result['episode_dict']

                # 결과 dict를 인스턴스의 _episode_dict에 업데이트
                self._episode_dict.update(page_episode_dict)

                # 다음 loop에서 증가한 page값을 사용하기 위해 값 설정
                page += 1

                # 결과에서 다음 페이지 존재여부를 판단, 없다면 break로 반복문 탈출
                has_next = result['has_next']
                if not has_next:
                    break
        return self._episode_dict


class WebtoonNotExist(Exception):
    def __init__(self, title):
        self.title = title

    def __str__(self):
        return f'Webtoon(title: {self.title})을 찾을 수 없습니다.'
