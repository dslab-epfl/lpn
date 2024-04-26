from enum import IntEnum

class CstStr(IntEnum):
    END_OF_MESSAGE = 0
    NONSCALAR = 1
    END_OF_MESSAGE_TOP_LEVEL = 2
    SCALAR = 3
    SUBMESSAGE = 4
    NONSUBMESSAGE = 5

def MetaInfoTranslate(name):
    if name == "nonscalar":
        return CstStr.NONSCALAR
    elif name == "scalar":
        return CstStr.SCALAR
    elif name == "submessage":
        return CstStr.SUBMESSAGE
    else:
        assert(isinstance(name, int))
        return name

