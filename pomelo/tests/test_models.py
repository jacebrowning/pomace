# pylint: disable=expression-not-assigned,unused-variable

from .. import models


def describe_action():
    def describe_str():
        def default(expect):
            action = models.Action()
            expect(str(action)) == 'click_element'
