# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class EpisodeContent():
    def __init__(self, episode_code, title_code, episode_name, title_name, no, display_no, introduction, isnew, islock, thumbnail_url):
        # type: (EpisodeContent, str, str, str, str, int, str, str, bool) -> None
        self.__episode_code = episode_code
        self.__title_code = title_code
        self.__episode_name = episode_name
        self.__title_name = title_name
        self.__no = no
        self.__display_no = display_no
        self.__introduction = introduction
        self.__isnew = isnew
        self.__islock = islock
        self.__thumbnail_url = thumbnail_url

    def __str__(self):
        # type: (EpisodeContent) -> dict
        return {'episode_code': self.__episode_code,
                'title_code': self.__title_code,
                'episode_name': self.__episode_name,
                'title_name': self.__title_name,
                'no': self.__no,
                'display_no': self.__display_no,
                'introduction': self.__introduction,
                'isnew': self.__isnew,
                'islock': self.__islock,
                'thumbnail_url': self.__thumbnail_url}

    def __repr__(self):
        # type: (EpisodeContent) -> str
        return '{0}.{1}("{2}","{3}","{4}","{5}","{6}","{7}","{8}","{9}","{10}","{11}")'.format(
            self.__module__, type(self).__name__,
            self.__episode_code, self.__title_code, self.__episode_name, self.__title_name,
            self.__no, self.__display_no, self.__introduction,
            self.__isnew, self.__islock, self.__thumbnail_url
        )

    @property
    def episode_code(self):
        # type: (EpisodeContent) -> str
        return self.__episode_code

    @property
    def title_code(self):
        # type: (EpisodeContent) -> str
        return self.__title_code

    @property
    def episode_name(self):
        # type: (EpisodeContent) -> str
        return self.__episode_name

    @property
    def title_name(self):
        # type: (EpisodeContent) -> str
        return self.__title_name

    @property
    def no(self):
        # type: (EpisodeContent) -> int
        return self.__no

    @property
    def display_no(self):
        # type: (EpisodeContent) -> str
        return self.__display_no

    @property
    def introduction(self):
        # type: (EpisodeContent) -> str
        return self.__introduction

    @property
    def isnew(self):
        # type: (EpisodeContent) -> bool
        return self.__isnew

    @property
    def islock(self):
        # type: (EpisodeContent) -> bool
        return self.__islock

    @property
    def thumbnail_url(self):
        # type: (EpisodeContent) -> str
        return self.__thumbnail_url
