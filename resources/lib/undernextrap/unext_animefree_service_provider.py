from __future__ import annotations
from typing import Optional
import json
import re
import xbmc
import requests
from .title_content import TitleContent
import cwebdriverinstaller
if cwebdriverinstaller.CWebDriverInstallerHelper.append_import_path():
    from pyppeteer import launch
    from pyppeteer.browser import Browser
    from pyppeteer.page import Page


class UnextAnimeFreeServiceProvider():
    def __init__(self):
        """
        コンストラクタ
        """
        self.__browser = None
        self.__browser_share = False
        self.__browser_default_user_agent = None
        self.__page = None
        self.__session = None
        self.__session_share = False

    async def dispose(self) -> None:
        """
        リソース破棄
        """
        if (self.__session is not None) and (not self.__session_share):
            self.__session.close()
            self.__session = None
            self.__session_share = False
        if self.__page is not None:
            await self.__page.close()
            self.__page = None
        self.__browser_default_user_agent = None
        if (self.__browser is not None) and (not self.__browser_share):
            await self.__browser.close()
            self.__browser = None
            self.__browser_share = False

    @property
    def browser(self) -> Optional[Browser]:
        """
        ブラウザ

        Returns
        -------
        result : Optional[Browser]
            ブラウザ
        """
        return self.__browser

    @browser.setter
    def browser(self, value: Optional[Browser]) -> None:
        """
        ブラウザ

        Parameters
        -------
        value : Optional[Browser]
            ブラウザ
        """
        if (self.__browser is not None) and (not self.__browser_share):
            self.__browser.close()
        self.__browser = value
        self.__browser_share = value is not None

    @property
    def session(self) -> Optional[requests.Session]:
        """
        セッション

        Returns
        -------
        result : Optional[requests.Session]
            セッション
        """
        return self.__session

    @session.setter
    def session(self, value: Optional[requests.Session]) -> None:
        """
        セッション

        Parameters
        -------
        value : Optional[requests.Session]
            セッション
        """
        if (self.__session is not None) and (not self.__session_share):
            self.__session.close()
        self.__session = value
        self.__session_share = value is not None

    async def get_top_contents(self) -> Optional[list[TitleContent]]:
        """
        トップコンテンツの取得

        Returns
        -------
        value : Optional[list[TitleContent]]
            タイトル情報群
        """
        page = await self._page
        url = r'https://video.unext.jp/feature/cp/animefree/'
        await page.goto(url)
        a_tags = await page.querySelectorAll(r'div#js-contentsArea a[class*="p-titlePanel"]')
        noname_contents = []
        for a_tag in a_tags:
            href = await page.evaluate('x => x.getAttribute("href")', a_tag)
            img_tag = await a_tag.querySelector(r'img')
            thumbnail = await page.evaluate('x => x.getAttribute("src")', img_tag)
            title_code = UnextAnimeFreeServiceProvider.__get_title_code_from_url(href)
            noname_contents.append({'title_code': title_code, 'thumbnail': thumbnail})

        title_codes = ','.join([i['title_code'] for i in noname_contents])
        url = r'https://video-api.unext.jp/api/1/cmsuser/title/meta?title_codes=' + title_codes
        meta_api_get = self._session.get(url, headers=UnextAnimeFreeServiceProvider.__HEADERS)
        if meta_api_get.status_code != 200:
            xbmc.log('Error:' + str(meta_api_get.status_code) + '\nサーバーからエラーステータスが返されました', xbmc.LOGDEBUG)
            return
        meta_api_result = json.loads(meta_api_get.text)
        title_contents = []
        for i in noname_contents:
            title_code = i['title_code']
            name = next((meta['display_name'] for meta in meta_api_result if meta['title_code'] == title_code), {'display_name': ''})
            thumbnail = i['thumbnail']
            title_contents.append(TitleContent(title_code, name,  thumbnail))
        return title_contents

    @property
    async def _browser(self) -> Browser:
        """
        ブラウザ

        Returns
        -------
        result : Browser
            ブラウザ
        """
        if self.__browser is None:
            browser_path = cwebdriverinstaller.CWebDriverInstaller.chrome_browser_path()
            self.__browser = await launch({
                'args': ['--no-sandbox'],
                'executablePath': browser_path,
                'handleSIGINT': False,
                'handleSIGTERM': False,
                'handleSIGHUP': False,
            })
        return self.__browser

    @property
    async def _page(self) -> Page:
        if self.__page is None:
            browser = await self._browser
            page = await browser.newPage()
            if self.__browser_default_user_agent is None:
                self.__browser_default_user_agent = await page.evaluate('() => navigator.userAgent')
            user_agent = UnextAnimeFreeServiceProvider.__CUSTOM_USER_AGENT + ' ' + xbmc.getUserAgent() + ' ' + self.__browser_default_user_agent
            await page.setUserAgent(user_agent)
            self.__page = page
        return self.__page

    @property
    def _session(self) -> requests.Session:
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

    __CUSTOM_USER_AGENT: str = 'under-nex-trap-animefree/0.0.1'
    """
    カスタムUser-Agent
    """

    __HEADERS: dict[str, str] = {'User-Agent': __CUSTOM_USER_AGENT + ' ' + requests.utils.default_user_agent() + ' ' + xbmc.getUserAgent()}
    """
    User-Agent改変用ヘッダー
    """

    __TITLE_CODE_FROM_URL: re.Pattern = re.compile(r'SID\d+')
    """
    URLからタイトルコードを取得する正規表現
    """

    @ staticmethod
    def __get_title_code_from_url(url: str) -> str:
        """
        URLからタイトルコードを取得する

        Parameters
        -------
        url : str
            URL

        Returns
        -------
        result : str
            タイトルコード
        """
        title_code = UnextAnimeFreeServiceProvider.__TITLE_CODE_FROM_URL.search(url).group(0)
        return title_code

    async def __aenter__(self) -> UnextAnimeFreeServiceProvider:
        """
        With句開始

        Returns
        -------
        result : UnextAnimeFreeServiceProvider
            自身
        """
        return self

    async def __aexit__(self, exception_type, exception_value, traceback) -> bool:
        """
        With句終了

        Returns
        -------
        result : bool
            True:例外を再スローしない, False:例外を再スローする
        """
        await self.dispose()
        return False
