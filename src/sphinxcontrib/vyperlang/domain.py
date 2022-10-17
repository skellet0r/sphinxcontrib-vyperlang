from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.locale import _


class VyObject(ObjectDescription):
    ...


class VyContract(VyObject):
    ...


class VyInterface(VyObject):
    ...


class VyEvent(VyObject):
    ...


class VyEnum(VyObject):
    ...


class VyStruct(VyObject):
    ...


class VyMember(VyObject):
    ...


class VyConstant(VyObject):
    ...


class VyImmutable(VyObject):
    ...


class VyStateVar(VyObject):
    ...


class VyFunction(VyObject):
    ...


class VyperDomain(Domain):
    """Vyper language domain."""

    name = "vy"
    label = "Vyper"
    object_types = {
        "contract": ObjType(_("contract"), "cont", "obj"),
        "interface": ObjType(_("interface"), "iface", "obj"),
        "event": ObjType(_("event"), "event", "obj"),
        "enum": ObjType(_("enum"), "enum", "obj"),
        "struct": ObjType(_("struct"), "struct", "obj"),
        "member": ObjType(_("member"), "memb", "obj"),
        "constant": ObjType(_("constant"), "const", "obj"),
        "immutable": ObjType(_("immutable"), "immut", "obj"),
        "statevar": ObjType(_("state variable"), "svar", "obj"),
        "function": ObjType(_("function"), "func", "obj"),
    }
    directives = {
        "contract": VyContract,
        "interface": VyInterface,
        "event": VyEvent,
        "enum": VyEnum,
        "struct": VyStruct,
        "member": VyMember,
        "constant": VyConstant,
        "immutable": VyImmutable,
        "statevar": VyStateVar,
        "function": VyFunction,
    }
