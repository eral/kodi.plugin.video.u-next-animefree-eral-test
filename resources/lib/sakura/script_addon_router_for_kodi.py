# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from __future__ import annotations
import sys
import urllib
import urlparse
import pickle
import base64


class ScriptAddonRouterForKodi(object):
    def __init__(self, entrance_funciton='entrance', *args):
        # type: (ScriptAddonRouterForKodi, unicode) -> None
        """
        コンストラクタ
        """
        self.__url = sys.argv[0]
        self.__handle = int(sys.argv[1])
        self.__query = sys.argv[2][1:]
        self.__entrance_funciton_name = ScriptAddonRouterForKodi.__get_attr_name(
            entrance_funciton)
        self.__entrance_funciton_args = args

    def __call__(self):
        # type: (ScriptAddonRouterForKodi) -> None
        """
        表示
        """
        attr_name, args = ScriptAddonRouterForKodi.parse_url_query(
            self.__query)
        if not attr_name:
            attr_name = self.__entrance_funciton_name
            args = self.__entrance_funciton_args
        funciton = getattr(self, attr_name)
        funciton(*args)

    @ property
    def url(self):
        # type: (ScriptAddonRouterForKodi) -> unicode
        """
        URL

        Returns
        -------
        url : unicode
            URL
        """
        return self.__url

    @ property
    def handle(self):
        # type: (ScriptAddonRouterForKodi) -> int
        """
        ハンドル

        Returns
        -------
        handle : int
            ハンドル
        """
        return self.__handle

    def get_url(self, funciton, *args):
        # type: (ScriptAddonRouterForKodi) -> unicode
        """
        URLの取得

        Parameters
        ----------
        funciton : (unicode, instancemethod)
        インスタンスメソッド、もしくは関数名

        args :  object[]
        インスタンスメソッドに渡す引数

        Returns
        -------
        url : unicode
            URL
        """
        result = self.url + '?' \
            + ScriptAddonRouterForKodi.get_url_query(funciton, *args)
        return result

    @ staticmethod
    def get_url_query(funciton, *args):
        # type: ((unicode, object), list[object]) -> unicode
        """
        URLクエリの取得

        Parameters
        ----------
        funciton : (unicode, instancemethod)
        インスタンスメソッド、もしくは関数名

        args :  list[object]
        インスタンスメソッドに渡す引数

        Returns
        -------
        url_query : unicode
            URLクエリ
        """
        result = 'f=' \
            + urllib.quote(ScriptAddonRouterForKodi.__get_attr_name(funciton))
        for i, value in enumerate(args):
            i = unicode(i)
            value = ScriptAddonRouterForKodi.__serialize_query_value(value)
            result += '&' + i + '=' + value
        return result

    @ staticmethod
    def parse_url_query(url_query):
        # type: (unicode) -> unicode, dict[unicode]
        """
        URLクエリの取得

        Parameters
        ----------
        url_query : unicode
        URLクエリ

        Returns
        -------
        attr_name : unicode
            getattr用名称

        args : list[unicode]
            引数
        """
        query = urlparse.parse_qs(url_query)
        if 'f' in query:
            attr_name = query['f'][0]
        else:
            attr_name = None
        args = []
        for i in range(len(query)):
            i = unicode(i)
            if i in query:
                value = query[i][0]
                value = ScriptAddonRouterForKodi.__deserialize_query_value(
                    value)
                args.append(value)
            else:
                break
        return attr_name, args

    @ staticmethod
    def __get_attr_name(value):
        # type: (object) -> unicode
        """
        getattr用名称の取得

        Parameters
        ----------
        value : (unicode, instancemethod)
        名称を取得するインスタンスメソッド、もしくは名称そのもの

        Returns
        -------
        attr_name : unicode
            getattr用名称
        """
        if isinstance(value, unicode):
            return value
        elif type(value).__name__ == 'instancemethod':
            return value.__name__
        else:
            raise ValueError('entrance_funciton')

    @ staticmethod
    def __serialize_query_value(value):
        # type: (object) -> unicode
        """
        クエリ値のシリアライズ

        Parameters
        ----------
        value : object
        シリアライズするオブジェクト

        Returns
        -------
        value : unicode
            シリアライズテキスト
        """
        if isinstance(value, unicode):
            value = 's' + urllib.quote(value)
        elif isinstance(value, bool):
            value = 'b' + unicode(value)
        elif isinstance(value, int):
            value = 'i' + unicode(value)
        elif isinstance(value, float):
            value = 'f' + unicode(value)
        else:
            value_bytes = pickle.dumps(value)
            value_base64urlsafe = base64.b64encode(
                value_bytes, '-_').replace('=', '.')
            value = 'o' + unicode(value_base64urlsafe)
        return value

    @ staticmethod
    def __deserialize_query_value(value):
        # type: (unicode) -> object
        """
        クエリ値のデシリアライズ

        Parameters
        ----------
        value : unicode
        デシリアライズするテキスト

        Returns
        -------
        value : object
            オブジェクト
        """
        if value[0] == 's':
            value = unicode(urlparse.unquote(value[1:]))
        elif value[0] == 'b':
            value = bool(value[1:])
        elif value[0] == 'i':
            value = int(value[1:])
        elif value[0] == 'f':
            value = float(value[1:])
        elif value[0] == 'o':
            value_base64urlsafe_unicode = value[1:]
            value_base64urlsafe_unicode = value_base64urlsafe_unicode.replace(
                '.', '=')
            value_base64urlsafe = str(value_base64urlsafe_unicode)
            value_bytes = base64.b64decode(value_base64urlsafe, '-_')
            value = pickle.loads(value_bytes)
        return value
