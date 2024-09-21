from dataclasses import dataclass
from typing import ClassVar

from constants import PROMPT



_KWARGS = {'slots': True, 'frozen': True, 'eq': False}



@dataclass(**_KWARGS)
class Treatment:
    name: str
    keywords: dict[str, int]
    _name_is_mass_noun: bool

    @classmethod
    def get_prompt(cls, city: str) -> str:
        plural = cls.name + 's' * (not cls._name_is_mass_noun)
        return PROMPT.format(
            plural,
            city,
            ('a' + 'n' * (cls.name[0].lower() in 'aeiou') + ' ') * (not cls._name_is_mass_noun) + cls.name,
            plural,
            city
        )



@dataclass(**_KWARGS)
class VibroacousticTherapy(Treatment):
    name: ClassVar[str] = 'Vibroacoustic Therapy'
    keywords: ClassVar[dict[str, int]] = {
        'vibroacoustic': 2,
        'VAT': 2
    }
    _name_is_mass_noun: ClassVar[bool] = True



@dataclass(**_KWARGS)
class RedLightTherapy(Treatment):
    name: ClassVar[str] = 'Red Light Therapy'
    keywords: ClassVar[dict[str, int]] = {
        'red light': 2,
        'photobiomodulation': 2
    }
    _name_is_mass_noun: ClassVar[bool] = True



@dataclass(**_KWARGS)
class PEMF(Treatment):
    name: ClassVar[str] = 'PEMF'
    keywords: ClassVar[dict[str, int]] = {
        'PEMF': 2,
        'pulsed electromagnetic': 2
    }
    _name_is_mass_noun: ClassVar[bool] = True



@dataclass(**_KWARGS)
class HyperbaricOxygenTherapy(Treatment):
    name: ClassVar[str] = 'Hyperbaric Oxygen Therapy'
    keywords: ClassVar[dict[str, int]] = {
        'HBOT': 2,
        'hyperbaric': 2
    }
    _name_is_mass_noun: ClassVar[bool] = True



@dataclass(**_KWARGS)
class Hocatt(Treatment):
    name: ClassVar[str] = 'Hocatt'
    keywords: ClassVar[dict[str, int]] = {
        'Hocatt': 2,
        'ozone': 2
    }
    _name_is_mass_noun: ClassVar[bool] = True



@dataclass(**_KWARGS)
class InfraredSauna(Treatment):
    name: ClassVar[str] = 'Infrared Sauna'
    keywords: ClassVar[dict[str, int]] = {
        'infrared': 2
    }
    _name_is_mass_noun: ClassVar[bool] = False



@dataclass(**_KWARGS)
class EES(Treatment):
    name: ClassVar[str] = 'EES'
    keywords: ClassVar[dict[str, int]] = {
        'EES': 2,
        'energy enhancement': 2
    }
    _name_is_mass_noun: ClassVar[bool] = True



@dataclass(**_KWARGS)
class Facial(Treatment):
    name: ClassVar[str] = 'Facial'
    keywords: ClassVar[dict[str, int]] = {
        'facial': 2
    }
    _name_is_mass_noun: ClassVar[bool] = False



TREATMENTS: tuple[Treatment, ...] = (VibroacousticTherapy, PEMF, RedLightTherapy, Hocatt, HyperbaricOxygenTherapy, EES, InfraredSauna, Facial) # type: ignore

