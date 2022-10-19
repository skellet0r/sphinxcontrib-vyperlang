import re

from docutils.parsers.rst import directives
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.locale import _
from sphinx.util.docfields import Field, GroupedField, TypedField

MUTABILITY = ("nonpayable", "payable", "pure", "view")
VISIBILITY = ("external", "internal")

VY_SIG_RE = re.compile(
    r"""
    ^(?: (\w+)\. )?             # scope
    (\w+)\s*                    # name
    (?:                         # optional:
        \(\s*(.*?)\s*\)         #   arguments
        (?:\s* -> \s* (.+))?    #   return annotation
    )?$
    """,
    re.VERBOSE,
)


class VyObject(ObjectDescription):
    needs_arglist = False


class VyGlobalLike(VyObject):
    option_spec = {
        "type": directives.unchanged_required,
        "public": directives.flag,
        **VyObject.option_spec,
    }


class VyConstant(VyGlobalLike):
    option_spec = {"value": directives.unchanged_required, **VyGlobalLike.option_spec}


class VyEvent(VyObject):
    doc_field_types = [
        TypedField(
            "topic",
            names=("topic",),
            typenames=("type", "ttype"),
            label=_("Topics"),
            typerolename="obj",
            can_collapse=True,
        ),
        TypedField(
            "data",
            names=("data",),
            typenames=("type", "dtype"),
            label=_("Data"),
            typerolename="obj",
            can_collapse=True,
        ),
    ]


class VyEnum(VyObject):
    doc_field_types = [
        GroupedField(
            "element", names=("element", "elem"), label=_("Elements"), can_collapse=True
        )
    ]


class VyStruct(VyObject):
    doc_field_types = [
        TypedField(
            "member",
            names=("member",),
            typenames=("type", "mtype"),
            label=_("Members"),
            typerolename="obj",
            can_collapse=True,
        )
    ]


class VyFunction(VyObject):
    needs_arglist = True
    option_spec = {
        "mutability": lambda arg: directives.choice(arg, MUTABILITY),
        "visibility": lambda arg: directives.choice(arg, VISIBILITY),
        **VyObject.option_spec,
    }
    doc_field_types = [
        TypedField(
            "parameter",
            names=("parameter", "param", "argument", "arg"),
            typenames=("type", "paramtype"),
            label=_("Parameters"),
            typerolename="obj",
            can_collapse=True,
        ),
        GroupedField(
            "revert",
            names=("revert", "except", "raise"),
            label=_("Reverts"),
            can_collapse=True,
        ),
        Field(
            "returnvalue",
            names=("return", "returns"),
            label=_("Returns"),
            has_arg=False,
        ),
        Field(
            "returntype",
            names=("rtype",),
            label=_("Return type"),
            has_arg=False,
            bodyrolename="obj",
        ),
    ]


class VyperDomain(Domain):
    """Vyper language domain."""

    name = "vy"
    label = "Vyper"
    object_types = {
        "contract": ObjType(_("contract"), "contr", "obj"),
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
        "contract": VyObject,
        "interface": VyObject,
        "event": VyEvent,
        "enum": VyEnum,
        "struct": VyStruct,
        "immutable": VyGlobalLike,
        "statevar": VyGlobalLike,
        "constant": VyConstant,
        "function": VyFunction,
    }
