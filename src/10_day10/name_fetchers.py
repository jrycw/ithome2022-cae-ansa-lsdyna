import uuid
from datetime import datetime

from schemas import GeneralEntityNames, name_mapping


def _get_datetime():
    return datetime.now().strftime('%Y%m%d_%H%M%s')


def _get_name(general_entity_name, name=None):
    return (name or (name_mapping.get(general_entity_name) +
                     _get_datetime() +
                     '_' +
                     uuid.uuid4().hex[:6]))


def get_one_part_name(name=None):
    return _get_name(GeneralEntityNames.PART.value, name)


def get_one_set_name(name=None):
    return _get_name(GeneralEntityNames.SET.value, name)


def get_one_contact_name(name=None):
    return _get_name(GeneralEntityNames.CONTACT.value, name)


def get_one_material_name(name=None):
    return _get_name(GeneralEntityNames.MATERIAL.value, name)


def get_one_proprty_name(name=None):
    return _get_name(GeneralEntityNames.PROPERTY.value, name)


def get_one_section_name(name=None):
    return _get_name(GeneralEntityNames.SECTION.value, name)


def get_one_curve_name(name=None):
    return _get_name(GeneralEntityNames.CURVE.value, name)
