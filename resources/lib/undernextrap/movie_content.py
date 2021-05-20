from __future__ import annotations


class MovieContent():
    def __init__(self, movie_url: str, movie_headers: dict[str, str],
                 protocol: str, drm: str, mime: str,
                 license_url: str, license_headers: dict[str, str],
                 license_post_data: str, license_response: str) -> None:
        self.__movie_url = movie_url
        self.__movie_headers = movie_headers
        self.__protocol = protocol
        self.__drm = drm
        self.__mime = mime
        self.__license_url = license_url
        self.__license_headers = license_headers
        self.__license_post_data = license_post_data
        self.__license_response = license_response

    def __str__(self):
        return {'movie_url': self.__movie_url,
                'movie_headers': self.__movie_headers,
                'protocol': self.__protocol,
                'drm': self.__drm,
                'mime': self.__mime,
                'license_url': self.__license_url,
                'license_headers': self.__license_headers,
                'license_post_data': self.__license_post_data,
                'license_response': self.__license_response}

    def __repr__(self):
        return '{0}.{1}("{2}","{3}","{4}","{5}","{6}","{7}","{8}","{9}","{10}")'.format(
            self.__module__, type(self).__drm__,
            self.__movie_url, self.__movie_headers, self.__protocol,
            self.__drm, self.__mime, self.__license_url,
            self.__license_headers, self.__license_post_data, self.__license_response
        )

    @property
    def movie_url(self) -> str:
        return self.__movie_url

    @property
    def movie_headers(self) -> dict[str, str]:
        return self.__movie_headers

    @property
    def protocol(self) -> str:
        return self.__protocol

    @property
    def drm(self) -> str:
        return self.__drm

    @property
    def mime(self) -> str:
        return self.__mime

    @property
    def license_url(self) -> str:
        return self.__license_url

    @property
    def license_headers(self) -> dict[str, str]:
        return self.__license_headers

    @property
    def license_post_data(self) -> str:
        return self.__license_post_data

    @property
    def license_response(self) -> str:
        return self.__license_response
