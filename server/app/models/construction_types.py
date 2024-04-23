import enum

class CefrLevel(enum.Enum):
    a1 = 'A1'
    a2 = 'A2'
    b1 = 'B1'
    b2 = 'B2'
    c1 = 'C1'
    c2 = 'C2'

    @classmethod
    def parse(cls, value: str) -> 'CefrLevel':
        value = value.strip()
        value = value.translate(str.maketrans('АВС', 'ABC'))
        return CefrLevel(value)


class Language(enum.Enum):
    english = 'en'
    russian = 'ru'
    norwegian = 'no'

    @classmethod
    def parse(cls, value: str) -> 'Language':
        value = value.strip().lower()
        return cls({'eng': 'en', 'rus': 'ru', 'nor': 'no'}.get(value, value))


class UsageLabel(enum.Enum):
    colloquial = 'c'
    formal = 'f'
    obsolete = 'o'
    na = 'n'

    @staticmethod
    def parse(value: str) -> str | None:
        return {
            'na': 'n',
            'colloquial': 'c',
            'formal': 'f',
            'obsolete': 'o',
            '': None,
        }[value.strip().lower()]


class CommunicativeType(enum.Enum):
    interrogative = 'i'
    declarative = 'd'
    not_applicable = 'na'
    exclamatory = 'e'
    interrogative_exclamatory = 'ie'
    declarative_interrogative = 'di'
    declarative_exclamatory = 'de'
    interrogative_declarative = 'id'

    @staticmethod
    def parse(value: str) -> str | None:
        return {
            'interrogative': 'i',
            'declarative': 'd',
            'notapplicable': 'na',
            'exclamatory': 'e',
            'interrogative/exclamatory': 'ie',
            'interrogative/declarative': 'id',
            'declarative/interrogative': 'di',
            'declarative/exclamatory': 'de',
            '': None,
        }[value.lower().replace(' ', '')]
