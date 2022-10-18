from docutils.parsers.rst import directives
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.locale import _

MUTABILITY = ("nonpayable", "payable", "pure", "view")
VISIBILITY = ("external", "internal")


class VyObject(ObjectDescription):
    ...


class VyGlobal(VyObject):
    option_spec = {
        "type": directives.unchanged_required,
        "public": directives.flag,
        **VyObject.option_spec,
    }


class VyConstant(VyGlobal):
    option_spec = {"value": directives.unchanged_required, **VyGlobal.option_spec}


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


class VyFunction(VyObject):
    option_spec = {
        "mutability": lambda arg: directives.choice(arg, MUTABILITY),
        "visibility": lambda arg: directives.choice(arg, VISIBILITY),
        **VyObject.option_spec,
    }


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
        "immutable": ObjType(_("immutable"), "immut", "obj"),
        "statevar": ObjType(_("state variable"), "svar", "obj"),
        "constant": ObjType(_("constant"), "const", "obj"),
        "function": ObjType(_("function"), "func", "obj"),
    }
    directives = {
        "contract": VyContract,
        "interface": VyInterface,
        "event": VyEvent,
        "enum": VyEnum,
        "struct": VyStruct,
        "immutable": VyGlobal,
        "statevar": VyGlobal,
        "constant": VyConstant,
        "function": VyFunction,
    }
