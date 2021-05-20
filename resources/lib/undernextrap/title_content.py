from __future__ import annotations


class TitleContent():
    def __init__(self, code: str, name: str, thumbnail_url: str) -> None:
        self.__code = code
        self.__name = name
        self.__thumbnail_url = thumbnail_url

    def __str__(self):
        return {'code': self.code, 'name': self.name, 'thumbnail_url': self.thumbnail_url}

    def __repr__(self):
        return '{0}.{1}("{2}","{3}","{4}")'.format(
            self.__module__, type(self).__name__,
            self.__code, self.__name, self.__thumbnail_url
        )

    @property
    def code(self) -> str:
        return self.__code

    @property
    def name(self) -> str:
        return self.__name

    @property
    def thumbnail_url(self) -> str:
        return self.__thumbnail_url
