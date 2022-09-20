from enum import Enum


class GeneralEntityNames(str, Enum):
    PART: str = 'part'
    SET: str = 'set'
    CONTACT: str = 'contact'
    MATERIAL: str = 'material'
    PROPERTY: str = 'property'
    SECTION: str = 'section'
    CURVE: str = 'curve'


class AutoCreatedEntityNames(str, Enum):
    PART: str = 'auto_part_'
    SET: str = 'auto_set_'
    CONTACT: str = 'auto_contact_'
    MATERIAL: str = 'auto_material_'
    PROPERTY: str = 'auto_property_'
    SECTION: str = 'auto_section_'
    CURVE: str = 'auto_curve_'


class MatType(str, Enum):
    MAT1_MAT_ELASTIC: str = 'MAT1 MAT_ELASTIC'


class ContactType(str, Enum):
    TYPE0_SEGMENT_SET: str = '0: Segment set'
    TYPE1_SHELL_SET: str = '1: Shell set'
    TYPE2_PART_SET: str = '2: Part set'
    TYPE3_PART_ID: str = '3: Part id'
    TYPE4_NODE_SET: str = '4: Node set'
    TYPE5_ALL: str = '5: All'
    TYPE6_EXEMPTED: str = '6: Exempted'


class ContactTypeName(str, Enum):
    AUTOMATIC_SURFACE_TO_SURFACE: str = 'AUTOMATIC_SURFACE_TO_SURFACE'


class LSDYNAType(str, Enum):
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


class SecType(str, Enum):
    SECTION_SHELL: str = 'SECTION_SHELL'
    SECTION_SOLID: str = 'SECTION_SOLID'


class ControlCardType(str, Enum):
    CONTROL: str = 'CONTROL'
    DATABASE: str = 'DATABASE'


class BCType(str, Enum):
    BOUNDARY_SPC_SET: str = 'BOUNDARY_SPC(SET)'
    INITIAL_VELOCITY_SET: str = 'INITIAL_VELOCITY_SET'


name_mapping = dict(zip([member.value for member in GeneralEntityNames], [
    member.value for member in AutoCreatedEntityNames]))
