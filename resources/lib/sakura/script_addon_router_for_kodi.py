from __future__ import annotations
from typing import Union, Tuple, Callable
import sys
import urllib.parse
import pickle
import base64


class ScriptAddonRouterForKodi(object):
    def __init__(self, entrance_funciton: str = 'entrance', *args: list[object]) -> None:
        """
        コンストラクタ
        """
        self.__url = sys.argv[0]
        self.__handle = int(sys.argv[1])
        self.__query = sys.argv[2][1:]
        self.__entrance_funciton_name = ScriptAddonRouterForKodi.__get_attr_name(entrance_funciton)
        self.__entrance_funciton_args = args

    def __call__(self) -> None:
        """
        表示
        """
        attr_name, args = ScriptAddonRouterForKodi.parse_url_query(self.__query)
        if not attr_name:
            attr_name = self.__entrance_funciton_name
            args = self.__entrance_funciton_args
        funciton = getattr(self, attr_name)
        funciton(*args)

    @ property
    def url(self) -> str:
        """
        URL

        Returns
        -------
        url : str
            URL
        """
        return self.__url

    @ property
    def handle(self) -> int:
        """
        ハンドル

        Returns
        -------
        handle : int
            ハンドル
        """
        return self.__handle

    def get_url(self, funciton: Union[str, Callable], *args: list[object]) -> str:
        """
        URLの取得

        Parameters
        ----------
        funciton : Union[str, Callable]
        インスタンスメソッド、もしくは関数名

        args :  list[object]
        インスタンスメソッドに渡す引数

        Returns
        -------
        url : str
            URL
        """
        result = self.url + '?' + ScriptAddonRouterForKodi.get_url_query(funciton, *args)
        return result

    @ staticmethod
    def get_url_query(funciton: Union[str, Callable], *args: list[object]) -> str:
        """
        URLクエリの取得

        Parameters
        ----------
        funciton : Union[str, Callable]
        インスタンスメソッド、もしくは関数名

        args :  list[object]
        インスタンスメソッドに渡す引数

        Returns
        -------
        url_query : str
            URLクエリ
        """
        result = 'f=' + urllib.parse.quote(ScriptAddonRouterForKodi.__get_attr_name(funciton))
        for i, value in enumerate(args):
            i = str(i)
            value = ScriptAddonRouterForKodi.__serialize_query_value(value)
            result += '&' + i + '=' + value
        return result

    @ staticmethod
    def parse_url_query(url_query: str) -> Tuple[str, list[str]]:
        """
        URLクエリの取得

        Parameters
        ----------
        url_query : str
        URLクエリ

        Returns
        -------
        attr_name : str
            getattr用名称

        args : list[str]
            引数
        """
        query = urllib.parse.parse_qs(url_query)
        if 'f' in query:
            attr_name = query['f'][0]
        else:
            attr_name = None
        args = []
        for i in range(len(query)):
            i = str(i)
            if i in query:
                value = query[i][0]
                value = ScriptAddonRouterForKodi.__deserialize_query_value(value)
                args.append(value)
            else:
                break
        return attr_name, args

    @ staticmethod
    def __get_attr_name(value: Union[str, Callable]) -> str:
        """
        getattr用名称の取得

        Parameters
        ----------
        value : Union[str, Callable]
        名称を取得するインスタンスメソッド、もしくは名称そのもの

        Returns
        -------
        attr_name : str
            getattr用名称
        """
        if isinstance(value, str):
            return value
        elif callable(value):
            return value.__name__
        else:
            raise ValueError('value')

    @ staticmethod
    def __serialize_query_value(value: object) -> str:
        """
        クエリ値のシリアライズ

        Parameters
        ----------
        value : object
        シリアライズするオブジェクト

        Returns
        -------
        value : str
            シリアライズテキスト
        """
        if isinstance(value, str):
            value = 's' + urllib.parse.quote(value)
        elif isinstance(value, bool):
            value = 'b' + str(value)
        elif isinstance(value, int):
            value = 'i' + str(value)
        elif isinstance(value, float):
            value = 'f' + str(value)
        else:
            value_bytes = pickle.dumps(value)
            value_base64urlsafe = base64.b64encode(value_bytes, b'-_').replace(b'=', b'.')
            value = 'o' + value_base64urlsafe.decode()
        return value

    @ staticmethod
    def __deserialize_query_value(value: str) -> object:
        """
        クエリ値のデシリアライズ

        Parameters
        ----------
        value : str
        デシリアライズするテキスト

        Returns
        -------
        value : object
            オブジェクト
        """
        if value[0] == 's':
            value = str(urllib.parse.unquote(value[1:]))
        elif value[0] == 'b':
            value = bool(value[1:])
        elif value[0] == 'i':
            value = int(value[1:])
        elif value[0] == 'f':
            value = float(value[1:])
        elif value[0] == 'o':
            value_base64urlsafe = value[1:].replace('.', '=')
            value_bytes = base64.b64decode(value_base64urlsafe, '-_')
            value = pickle.loads(value_bytes)
        return value
