# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

from ..enums import Verb


def describe_verb():
    def describe_get_default_locators():
        def when_click(expect):
            verb = Verb("click")
            locators = list(verb.get_default_locators("send_email"))
            expect(locators) == [
                ("text", "Send Email"),
                ("text", "Send email"),
                ("text", "send email"),
                ("value", "Send Email"),
                ("value", "Send email"),
                ("value", "send email"),
            ]

        def when_fill(expect):
            verb = Verb("fill")
            locators = list(verb.get_default_locators("first_name"))
            expect(locators) == [
                ("name", "first_name"),
                ("name", "first-name"),
                ("id", "first_name"),
                ("id", "first-name"),
                ("aria-label", "First Name"),
                ("css", '[placeholder="First Name"]'),
                ("id", "FirstName"),
            ]
