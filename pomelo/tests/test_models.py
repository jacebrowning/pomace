# pylint: disable=expression-not-assigned,unused-variable

from .. import models


def describe_url():
    def describe_init():
        def it_removes_escapted_path_characters(expect, monkeypatch):
            monkeypatch.setattr(models.URL, 'SLASH', '@')
            url = models.URL('www.example.com', '@foo@bar')
            expect(url.domain) == 'www.example.com'
            expect(url.path) == '/foo/bar'

    def describe_path_encoded():
        def it_replaces_paths_slashes_with_a_special_character(expect, monkeypatch):
            monkeypatch.setattr(models.URL, 'SLASH', '@')
            url = models.URL('http://www.example.com/foo/bar')
            expect(url.domain) == 'www.example.com'
            expect(url.path_encoded) == '@foo@bar'
