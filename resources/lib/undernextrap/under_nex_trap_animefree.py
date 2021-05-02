# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from __future__ import annotations
import urllib
import xbmcgui
import xbmcplugin
import requests
import inputstreamhelper
from ..sakura.script_addon_router_for_kodi import ScriptAddonRouterForKodi
from .unext_animefree_service_provider import UnextAnimeFreeServiceProvider
from .unext_service_provider import UnextServiceProvider
from .title_content import TitleContent
from .episode_content import EpisodeContent


class UnderNexTrapAnimeFree(ScriptAddonRouterForKodi):
    def __init__(self):
        """
        コンストラクタ
        """
        super(UnderNexTrapAnimeFree, self).__init__(self.entrance)
        self.__session = None
        self.__unext_service_provider = None
        self.__unext_anime_free_service_provider = None

    def dispose(self):
        # type: () -> None
        """
        リソース破棄
        """
        if self.__unext_anime_free_service_provider is not None:
            self.__unext_anime_free_service_provider.dispose()
        if self.__unext_service_provider is not None:
            self.__unext_service_provider.dispose()
        if self.__session is not None:
            self.__session.close()

    def entrance(self):
        # type: (UnderNexTrapAnimeFree) -> None
        """
        初起動
        """
        self.top()

    def top(self):
        # type: (UnderNexTrapAnimeFree) -> None
        """
        トップコンテンツ
        """
        xbmcplugin.setPluginCategory(self.handle, 'Top')
        xbmcplugin.setContent(self.handle, 'videos')

        anime_free_top_contents = self._unext_anime_free_service_provider.get_top_contents()
        for content in anime_free_top_contents:
            list_item = UnderNexTrapAnimeFree.__create_xbmcgui_list_item(content)
            url = self.get_url(self.current_episode, content.code)
            xbmcplugin.addDirectoryItem(self.handle, url,
                                        list_item,
                                        isFolder=True)
        xbmcplugin.endOfDirectory(self.handle)

        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_NONE)

    def current_episode(self, title_code):
        # type: (UnderNexTrapAnimeFree, str) -> None
        """
        エピソード選択

        Parameters
        -------
        title_code : str
            タイトルコード
        """
        xbmcplugin.setPluginCategory(self.handle, 'Episode')
        xbmcplugin.setContent(self.handle, 'videos')

        title_contents = self._unext_service_provider.get_title_contents(title_code)
        for content in title_contents:
            list_item = UnderNexTrapAnimeFree.__create_xbmcgui_list_item(content)
            list_item.setProperty('IsPlayable', 'true')
            url = self.get_url(self.play_episode, content.title_code, content.episode_code)
            xbmcplugin.addDirectoryItem(self.handle, url,
                                        list_item,
                                        isFolder=False)
        xbmcplugin.endOfDirectory(self.handle)

        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_NONE)

    def play_episode(self, title_code, episode_code):
        # type: (UnderNexTrapAnimeFree, str, str) -> None
        """
        エピソード再生

        Parameters
        -------
        title_code : str
            タイトルコード
        episode_code : str
            エピソードコード
        """
        movie_content = self._unext_service_provider.get_movie_content(title_code, episode_code)
        if movie_content:
            self.__play_movie(movie_content.movie_url, movie_content.movie_headers,
                              movie_content.protocol, movie_content.drm, movie_content.mime,
                              movie_content.license_url, movie_content.license_headers,
                              movie_content.license_post_data, movie_content.license_response)

    @property
    def _session(self):
        # type: (UnextAnimeFreeServiceProvider) -> requests.Session
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

    @property
    def _unext_anime_free_service_provider(self):
        # type: (UnextAnimeFreeServiceProvider) -> UnextAnimeFreeServiceProvider
        """
        U-NEXT(無料配信)サービスプロバイダー

        Returns
        -------
        result : UnextAnimeFreeServiceProvider
            セッション
        """
        if self.__unext_anime_free_service_provider is None:
            self.__unext_anime_free_service_provider = UnextAnimeFreeServiceProvider()
            self.__unext_anime_free_service_provider.session = self._session
        return self.__unext_anime_free_service_provider

    @property
    def _unext_service_provider(self):
        # type: (UnextAnimeFreeServiceProvider) -> UnextServiceProvider
        """
        U-NEXTサービスプロバイダー

        Returns
        -------
        result : UnextServiceProvider
            セッション
        """
        if self.__unext_service_provider is None:
            self.__unext_service_provider = UnextServiceProvider()
            self.__unext_service_provider.session = self._session
        return self.__unext_service_provider

    def __play_movie(self, stream_url, stream_headers, protocol, drm, mime,
                     license_url, license_headers, license_post_data, license_response):
        # type: (UnderNexTrapAnimeFree, str, dict[str,str], str, str, str, str, dict[str,str], str, str) -> None
        """
        InputStream Helperでの再生
        """
        is_helper = inputstreamhelper.Helper(protocol, drm=drm)
        if is_helper.check_inputstream():
            play_item = xbmcgui.ListItem(path=stream_url)
            play_item.setContentLookup(False)
            if mime is not None:
                play_item.setMimeType(mime)
            play_item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
            if (stream_headers is not None) and (0 < len(stream_headers)):
                play_item.setProperty('inputstream.adaptive.stream_headers', urllib.urlencode(stream_headers))
            play_item.setProperty('inputstream.adaptive.manifest_type', protocol)
            play_item.setProperty('inputstream.adaptive.license_type', drm)
            license_key = license_url
            license_key += '|'
            if (license_headers is not None) and (0 < len(license_headers)):
                license_key += urllib.urlencode(license_headers)
            license_key += '|'
            if license_post_data is not None:
                license_key += license_post_data
            license_key += '|'
            if license_response is not None:
                license_key += license_response
            play_item.setProperty('inputstream.adaptive.license_key', license_key)
            xbmcplugin.setResolvedUrl(self.handle, True, play_item)

    @ staticmethod
    def __create_xbmcgui_list_item(src):
        # type: (object) -> xbmcgui.ListItem, None
        """
        リストアイテムの取得

        Parameters
        -------
        src : object
            ソース

        Returns
        -------
        result : xbmcgui.ListItem, None
            リストアイテム
        """
        if isinstance(src, TitleContent):
            return UnderNexTrapAnimeFree.__create_xbmcgui_list_item_for_title_content(src)
        elif isinstance(src, EpisodeContent):
            return UnderNexTrapAnimeFree.__create_xbmcgui_list_item_for_episode_content(src)
        return None

    @ staticmethod
    def __create_xbmcgui_list_item_for_title_content(src):
        # type: (TitleContent) -> xbmcgui.ListItem, None
        """
        リストアイテムの取得

        Parameters
        -------
        src : TitleContent
            ソース

        Returns
        -------
        result : xbmcgui.ListItem, None
            リストアイテム
        """
        list_item = xbmcgui.ListItem()
        list_item.setLabel(src.name)
        list_item.setArt({'thumb': src.thumbnail_url,
                          'icon': None,
                          'fanart': None})
        list_item.setInfo('video', {'title': list_item.getLabel(),
                                    'genre': 'Animation',
                                    'mediatype': 'season'})
        return list_item

    @ staticmethod
    def __create_xbmcgui_list_item_for_episode_content(src):
        # type: (EpisodeContent) -> xbmcgui.ListItem, None
        """
        リストアイテムの取得

        Parameters
        -------
        src : EpisodeContent
            ソース

        Returns
        -------
        result : xbmcgui.ListItem, None
            リストアイテム
        """
        list_item = xbmcgui.ListItem()
        list_item.setLabel(src.display_no + '  ' + src.episode_name)
        list_item.setArt({'thumb': src.thumbnail_url,
                          'icon': None,
                          'fanart': None})
        overlay = xbmcgui.ICON_OVERLAY_NONE
        if src.islock:
            overlay = xbmcgui.ICON_OVERLAY_LOCKED
        list_item.setInfo('video', {'title': list_item.getLabel(),
                                    'originaltitle': src.episode_name,
                                    'tvshowtitle': src.title_name,
                                    'genre': 'Animation',
                                    'mediatype': 'episode',
                                    'episode': src.no, 'sortepisode': src.no,
                                    'episodeguide': src.introduction,
                                    'plotoutline': src.introduction,
                                    'plot': src.introduction,
                                    'overlay': overlay
                                    })
        return list_item
