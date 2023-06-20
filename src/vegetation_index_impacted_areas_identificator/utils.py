from enum import Enum

def get_enum_member_from_name(enum_class, name):
    for member in enum_class.__members__.values():
        if member.name == name:
            return member
    raise ValueError(f"No matching enum member found for name {name}")

