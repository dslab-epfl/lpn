from enum import IntEnum

class CstStr(IntEnum):
    END_OF_MESSAGE = 0
    NONSCALAR = 1
    END_OF_MESSAGE_TOP_LEVEL = 2
    SCALAR = 3
    SUBMESSAGE = 4
    NONSUBMESSAGE = 5
    
    'identifiers for mem req'
    SCALAR_DISPATCH_REQ = 0
    STRING_GETPTR_REQ = 1
    STRING_LOADDATA_REQ = 2
    UNPACKED_REP_GETPTR_REQ = 3
    LOAD_NEW_SUBMESSAGE = 4
    LOAD_HASBITS_AND_IS_SUBMESSAGE = 5
    LOAD_EACH_FIELD = 6
    WRITE_OUT = 7

    READ = 0
    WRITE = 1



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

