# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from __future__ import annotations
import json
import urllib
import urlparse
import xbmc
import requests
from .episode_content import EpisodeContent
from .movie_content import MovieContent


class UnextServiceProvider():
    def __init__(self):
        """
        コンストラクタ
        """
        self.__session = None
        self.__session_share = False

    def dispose(self):
        # type: () -> None
        """
        リソース破棄
        """
        if (self.__session is not None) and (not self.__session_share):
            self.__session.close()

    @property
    def session(self):
        # type: (UnextServiceProvider) -> requests.Session, None
        """
        セッション

        Returns
        -------
        result : requests.Session, None
            セッション
        """
        return self.__session

    @session.setter
    def session(self, value):
        # type: (UnextServiceProvider, requests.Session) -> None
        """
        セッション

        Parameters
        -------
        value : requests.Session, None
            セッション
        """
        if (self.__session is not None) and (not self.__session_share):
            self.__session.close()
        if value is not None:
            self.__session = value
            self.__session_share = True
        else:
            self.__session = None
            self.__session_share = False

    def get_title_contents(self, title_code):
        # type: (UnextServiceProvider, str) -> list[EpisodeContent], None
        """
        タイトルコンテンツの取得

        Parameters
        -------
        title_code : str
            タイトルコード

        Returns
        -------
        value : list[EpisodeContent], None
            エピソード情報群
        """
        url = r'https://video-api.unext.jp/api/1/title'
        current_episode_get = self._session.get(url, headers=self.__HEADERS, params={
            'entity[]': ['episodes'],
            'title_code': [title_code]
        })
        if current_episode_get.status_code != 200:
            xbmc.log('Error:' + unicode(str(current_episode_get.status_code)) + '\nサーバーからエラーステータスが返されました', xbmc.LOGDEBUG)
            return
        episode_contents = []
        if current_episode_get.text is not None:
            current_episode_api_result = json.loads(current_episode_get.text)
            if current_episode_api_result['common']['result']['errorCode'] != '':
                xbmc.log('Error:' + current_episode_api_result['common']['result']['errorCode'] + '\nサーバーからエラーレスポンスが返されました', xbmc.LOGDEBUG)
                return
            title_name = ''
            episodes = current_episode_api_result['data']['entities_data']['episodes']['episode']
            for episode in episodes:
                episode_content = UnextServiceProvider.__create_episode_content(episode, title_code, title_name)
                episode_contents.append(episode_content)
        return episode_contents

    def get_title_current_contents(self, title_code):
        # type: (UnextServiceProvider, str) -> list[EpisodeContent], None
        """
        タイトルコンテンツの取得

        Parameters
        -------
        title_code : str
            タイトルコード

        Returns
        -------
        value : list[EpisodeContent], None
            エピソード情報群
        """
        url = r'https://video-api.unext.jp/api/1/title'
        current_episode_get = self._session.get(url, headers=self.__HEADERS, params={
            'entity[]': ['current_episode'],
            'title_code': [title_code]
        })
        if current_episode_get.status_code != 200:
            xbmc.log('Error:' + unicode(str(current_episode_get.status_code)) + '\nサーバーからエラーステータスが返されました', xbmc.LOGDEBUG)
            return
        episode_contents = []
        if current_episode_get.text is not None:
            current_episode_api_result = json.loads(current_episode_get.text)
            if current_episode_api_result['common']['result']['errorCode'] != '':
                xbmc.log('Error:' + current_episode_api_result['common']['result']['errorCode'] + '\nサーバーからエラーレスポンスが返されました', xbmc.LOGDEBUG)
                return
            current_episode = current_episode_api_result['data']['entities_data']['current_episode']
            episode = current_episode['episode']
            title_name = current_episode['title_name']
            episode_content = UnextServiceProvider.__create_episode_content(episode, title_code, title_name)
            episode_contents.append(episode_content)
        return episode_contents

    def get_movie_content(self, title_code, episode_code):
        # type: (UnextServiceProvider, str, str) -> MovieContent, None
        """
        タイトルコンテンツの取得

        Parameters
        -------
        title_code : str
            タイトルコード
        episode_code : str
            エピソードコード

        Returns
        -------
        value : MovieContent, None
            エピソード情報群
        """
        url = r'https://video-api.unext.jp/api/1/player'
        player_get = self._session.get(url, headers=self.__HEADERS, params={
            'entity[]': ['playlist_url'],
            'title_code': [title_code],
            'episode_code': [episode_code]
        })
        if player_get.status_code != 200:
            xbmc.log('Error:' + unicode(str(player_get.status_code)) + '\nサーバーからエラーステータスが返されました', xbmc.LOGDEBUG)
            return
        player = json.loads(player_get.text)
        if player['common']['result']['errorCode'] != '':
            xbmc.log('Error:' + player['common']['result']['errorCode'] + '\nサーバーからエラーレスポンスが返されました', xbmc.LOGDEBUG)
            return
        entity = player['data']['entities_data']['playlist_url']
        if entity['result_status'] != 200:
            xbmc.log('Error:' + unicode(str(entity['result_status'])) + '\nサーバーからエラーデータが返されました', xbmc.LOGDEBUG)
            return
        play_token = entity['play_token']
        movie_profile = entity['url_info'][0]['movie_profile']['dash']
        playlist_url_list = list(urlparse.urlparse(movie_profile['playlist_url']))
        playlist_url_query = urlparse.parse_qs(playlist_url_list[4])
        playlist_url_query['play_token'] = [play_token]
        playlist_url_list[4] = urllib.urlencode({k: str(v[0]) for k, v in playlist_url_query.items()})

        license_url_list = list(urlparse.urlparse(movie_profile['license_url_list']['widevine']))
        license_url_query = {'play_token': [play_token]}
        license_url_list[4] = urllib.urlencode({k: str(v[0]) for k, v in license_url_query.items()})

        movie_url = urlparse.urlunparse(playlist_url_list)
        movie_headers = []
        protocol = 'mpd'
        drm = 'com.widevine.alpha'
        mime = 'application/dash+xml'
        license_url = urlparse.urlunparse(license_url_list)
        license_headers = []
        license_post_data = 'R{SSM}'
        license_response = ''
        movie_content = MovieContent(movie_url, movie_headers, protocol, drm, mime, license_url, license_headers, license_post_data, license_response)
        return movie_content

    @property
    def _session(self):
        # type: (UnextServiceProvider) -> requests.Session
        """
        セッション

        Returns
        -------
        result : requests.Session
            セッション
        """
        if self.__session is None:
            self.__session = requests.Session()
        return self.__session

    __HEADERS = {'User-Agent': 'under-nex-trap/0.0.1 ' + requests.utils.default_user_agent()}
    # type: dict
    """
    User-Agent改変用ヘッダー
    """

    @ staticmethod
    def __create_episode_content(src, title_code, title_name):
        # type: (object, str, str) -> EpisodeContent
        """
        EpisodeContentの生成

        Parameters
        -------
        src : object
            ソース
        title_code : str
            タイトルコード
        title_name : str
            タイトル名

        Returns
        -------
        result : EpisodeContent
            EpisodeContent
        """
        episode_code = src['episode_code']
        episode_name = src['episode_name']
        no = int(src['no'])
        display_no = src['display_no']
        introduction = src['introduction']
        isnew = src['isnew']
        islock = src['payment_badge_code'] != ''
        thumbnail_url = r'https://' + src['thumbnail']['standard']
        episode_content = EpisodeContent(episode_code, title_code, episode_name, title_name, no, display_no, introduction, isnew, islock, thumbnail_url)
        return episode_content

    def __enter__(self):
        # type: (UnextServiceProvider) -> UnextServiceProvider
        """
        With句開始

        Returns
        -------
        result : UnextAnimeFreeServiceProvider
            自身
        """
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        # type: (UnextServiceProvider) -> bool
        """
        With句終了

        Returns
        -------
        result : bool
            True:例外を再スローしない, False:例外を再スローする
        """
        self.dispose()
        return False
