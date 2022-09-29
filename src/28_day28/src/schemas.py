from enum import Enum

from pydantic import BaseModel


class NodeEntityModel(BaseModel):
    X: float
    Y: float
    Z: float


class LSDYNAType(str, Enum):
    ALL: str = '__ALL_ENTITIES__'
    PART: str = 'ANSAPART'
    NODE: str = 'NODE'
    ELEMENT: str = '__ELEMENTS__'
    SOLID: str = 'ELEMENT_SOLID'
    SHELL: str = 'ELEMENT_SHELL'
    PROPERTY: str = '__PROPERTIES__'
    MATERIAL: str = '__MATERIALS__'
    SET: str = 'SET'
    CONTACT: str = 'CONTACT'
    SEGMENT: str = 'SEGMENT'
