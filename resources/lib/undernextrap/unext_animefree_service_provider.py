from __future__ import annotations
from typing import Optional
import json
import re
import xbmc
import requests
from .title_content import TitleContent
import cwebdriverinstaller
if cwebdriverinstaller.CWebDriverInstallerHelper.append_import_path():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    import chromedriver_binary  # noqa:F401 # webdriverをChromeに設定


class UnextAnimeFreeServiceProvider():
    def __init__(self):
        """
        コンストラクタ
        """
        self.__browser = None
        self.__browser_share = False
        self.__browser_default_user_agent = None
        self.__browser_wait = None
        self.__session = None
        self.__session_share = False

    def dispose(self) -> None:
        """
        リソース破棄
        """
        if (self.__session is not None) and (not self.__session_share):
            self.__session.close()
            self.__session = None
        self.__browser_default_user_agent = None
        self.__browser_wait = None
        if (self.__browser is not None) and (not self.__browser_share):
            self.__browser.quit()
            self.__browser = None

    @property
    def browser(self) -> Optional[webdriver.remote.webdriver.WebDriver]:
        """
        ブラウザ

        Returns
        -------
        result : webdriver.remote.webdriver.WebDriver, None
            ブラウザ
        """
        return self.__browser

    @browser.setter
    def browser(self, value: webdriver.remote.webdriver.WebDriver) -> None:
        """
        ブラウザ

        Parameters
        -------
        value : webdriver.remote.webdriver.WebDriver, None
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
        result : requests.Session, None
            セッション
        """
        return self.__session

    @session.setter
    def session(self, value: requests.Session) -> None:
        """
        セッション

        Parameters
        -------
        value : requests.Session, None
            セッション
        """
        if (self.__session is not None) and (not self.__session_share):
            self.__session.close()
        self.__session = value
        self.__session_share = value is not None

    def get_top_contents(self) -> list[TitleContent]:
        """
        トップコンテンツの取得

        Returns
        -------
        value : list[TitleContent], None
            タイトル情報群
        """
        url = r'https://video.unext.jp/feature/cp/animefree/'
        self._browser.get(url)
        locator = (By.CSS_SELECTOR, r'div#js-contentsArea a[class*="p-titlePanel"]')
        self._browser_wait.until(EC.presence_of_element_located(locator))
        a_tags = self._browser.find_elements(*locator)
        noname_contents = []
        for a_tag in a_tags:
            href = a_tag.get_attribute(r'href')
            img_tag = a_tag.find_element(By.CSS_SELECTOR, r'img')
            thumbnail = img_tag.get_attribute(r'src')
            title_code = UnextAnimeFreeServiceProvider.__get_title_code_from_url(href)
            noname_contents.append({'title_code': title_code, 'thumbnail': thumbnail})

        title_codes = ','.join([i['title_code'] for i in noname_contents])
        url = r'https://video-api.unext.jp/api/1/cmsuser/title/meta?title_codes=' + title_codes
        meta_api_get = self._session.get(url, headers=UnextAnimeFreeServiceProvider.__HEADERS)
        if meta_api_get.status_code != 200:
            xbmc.log('Error:' + unicode(str(meta_api_get.status_code)) + '\nサーバーからエラーステータスが返されました', xbmc.LOGDEBUG)
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
    def _browser(self) -> webdriver.remote.webdriver.WebDriver:
        """
        ブラウザ

        Returns
        -------
        result : webdriver.remote.webdriver.WebDriver
            ブラウザ
        """
        if self.__browser is None:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-gpu')
            options.page_load_strategy = 'eager'
            options.binary_location = cwebdriverinstaller.CWebDriverInstaller.chrome_browser_path()
            if self.__browser_default_user_agent is None:
                with webdriver.Chrome(options=options) as default_browser:
                    self.__browser_default_user_agent = default_browser.execute_script("return navigator.userAgent")
            options.add_argument(
                '--user-agent=' + UnextAnimeFreeServiceProvider.__CUSTOM_USER_AGENT + ' ' + xbmc.getUserAgent() + ' ' + self.__browser_default_user_agent)
            self.__browser = webdriver.Chrome(options=options)
        return self.__browser

    @ property
    def _browser_wait(self) -> WebDriverWait:
        if self.__browser_wait is None:
            self.__browser_wait = WebDriverWait(self._browser, 10)
        return self.__browser_wait

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

    def __enter__(self) -> UnextAnimeFreeServiceProvider:
        """
        With句開始

        Returns
        -------
        result : UnextAnimeFreeServiceProvider
            自身
        """
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> bool:
        """
        With句終了

        Returns
        -------
        result : bool
            True:例外を再スローしない, False:例外を再スローする
        """
        self.dispose()
        return False
