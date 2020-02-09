from enum import Enum


class Verb(Enum):
    CLICK = 'click'
    FILL = 'fill'
    SELECT = 'select'
    CHOOSE = 'choose'

    @classmethod
    def validate(cls, value: str) -> bool:
        return value in [e.value for e in cls]

    @property
    def delay(self) -> float:
        if self is self.CLICK:
            return 0.5
        return 0.0
