import random
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

import faker
import log
import us
import zipcodes
from parse import parse


__all__ = ["URL"]


class URL:

    ROOT = "@"

    def __init__(self, url_or_domain: str, path: Optional[str] = None):
        if path == self.ROOT:
            self.value = f"https://{url_or_domain}"
        elif path:
            path = ("/" + path).rstrip("/").replace("//", "/")
            self.value = f"https://{url_or_domain}" + path
        else:
            self.value = str(url_or_domain).rstrip("/")

    def __repr__(self):
        return f"URL({self.value!r})"

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return str(self) == str(other).strip("/")

        if self.domain != other.domain:
            return False
        if self.path == other.path:
            return True

        result = parse(self.path, other.path)
        if not result:
            return False

        for value in result.named.values():
            if value == self.ROOT or "/" in value:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __contains__(self, value):
        return value in self.value

    @property
    def domain(self) -> str:
        return urlparse(self.value).netloc

    @property
    def path(self) -> str:
        path = urlparse(self.value).path.strip("/")
        return path if path else self.ROOT

    @property
    def fragment(self) -> str:
        return urlparse(self.value).fragment.replace("/", "_").strip("_")


ALIASES = {
    "birthday": "date_of_birth",
    "cell_phone": "phone_number",
    "email_address": "email",
    "email": "email_address",
    "phone": "phone_number",
    "prefix": "honorific",
    "street_address": "address",
    "zip_code": "postcode",
    "zip": "zip_code",
}

STREETS = ["First", "Second", "Third", "Fourth", "Park", "Main"]


@dataclass
class Person:
    honorific: str
    first_name: str
    last_name: str
    date_of_birth: str
    phone_number: str
    email_address: str
    address: str
    city: str
    state: str
    state_abbr: str
    county: str
    zip_code: str

    @classmethod
    def random(cls, fake) -> "Person":
        if random.random() > 0.5:
            prefix, first_name, last_name = (
                fake.prefix_female,
                fake.first_name_female,
                fake.last_name,
            )
        else:
            prefix, first_name, last_name = (
                fake.prefix_male,
                fake.first_name_male,
                fake.last_name,
            )

        phone_number = str(random.randint(1000000000, 9999999999))
        email_address = f"{first_name}{last_name}@{fake.free_email_domain}".lower()

        while True:
            place = random.choice(zipcodes.filter_by())
            state = us.states.lookup(place["state"])
            if state and state.statehood_year:
                break

        if random.random() < 0.75:
            number = random.randint(50, 200)
            street = random.choice(STREETS)
            place["address"] = f"{number} {street} St."
        else:
            place["address"] = fake.street_address

        return cls(
            prefix,
            first_name,
            last_name,
            fake.birthday,
            phone_number,
            email_address,
            place["address"],
            place["city"],
            state.name,
            state.abbr,
            place["county"],
            place["zip_code"],
        )

    def __str__(self):
        return f"{self.name} <{self.email}>"

    def __getattr__(self, name):
        try:
            alias = ALIASES[name]
        except KeyError:
            return super().__getattribute__(name)
        else:
            log.debug(f"Mapped fake attribute {alias!r} to {name!r}")
            return getattr(self, alias)

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Fake:
    def __init__(self):
        self._generator = faker.Faker()

    def __getattr__(self, name):
        try:
            method = getattr(self._generator, name)
        except AttributeError:
            try:
                alias = ALIASES[name]
            except KeyError:
                return super().__getattribute__(name)
            else:
                log.debug(f"Mapped fake attribute {alias!r} to {name!r}")
                method = getattr(self._generator, alias)
        return method()

    @property
    def person(self) -> Person:
        return Person.random(self)

    @property
    def birthday(self) -> str:
        return self._generator.date_of_birth(minimum_age=18, maximum_age=80).strftime(
            "%m/%d/%Y"
        )
