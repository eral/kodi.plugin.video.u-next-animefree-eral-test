# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class TitleContent():
    def __init__(self, code, name, thumbnail_url):
        # type: (TitleContent, str, str, str) -> None
        self.__code = code
        self.__name = name
        self.__thumbnail_url = thumbnail_url

    def __str__(self):
        # type: (TitleContent) -> dict
        return {'code': self.code, 'name': self.name, 'thumbnail_url': self.thumbnail_url}

    def __repr__(self):
        # type: (TitleContent) -> str
        return '{0}.{1}("{2}","{3}","{4}")'.format(
            self.__module__, type(self).__name__,
            self.__code, self.__name, self.__thumbnail_url
        )

    @property
    def code(self):
        # type: (TitleContent) -> str
        return self.__code

    @property
    def name(self):
        # type: (TitleContent) -> str
        return self.__name

    @property
    def thumbnail_url(self):
        # type: (TitleContent) -> str
        return self.__thumbnail_url
