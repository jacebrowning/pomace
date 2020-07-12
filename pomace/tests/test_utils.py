# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import pytest

from .. import utils


def describe_fake():
    @pytest.fixture(scope='session')
    def fake():
        return utils.Fake()

    def describe_person():
        def it_includes_name_in_email(expect, fake):
            person = fake.person
            expect(person.email).icontains(person.last_name)

        def it_includes_honorific(expect, fake):
            expect(fake.person.honorific).is_not(None)
