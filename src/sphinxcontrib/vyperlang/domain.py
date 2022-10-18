import re

from docutils.parsers.rst import directives
from sphinx import addnodes
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
    allow_nesting = False
    needs_arglist = False

    def get_signature_prefix(self):
        return []

    def handle_signature(self, sig, signode):
        mo = VY_SIG_RE.match(sig)
        if mo is None:
            raise ValueError
        name, arglist, retann = mo.groups()

        cname = self.env.ref_context.get("vy:contract")
        iname = self.env.ref_context.get("vy:interface", "")
        if iname:
            add_contract = False
            fullname = iname + "." + name
        else:
            add_contract = True
            fullname = name

        signode["contract"] = cname
        signode["interface"] = iname
        signode["fullname"] = fullname

        sig_prefix = self.get_signature_prefix()
        if sig_prefix:
            signode += addnodes.desc_annotation(str(sig_prefix), "", *sig_prefix)

        if add_contract and self.env.config.add_contract_names:
            nodetext = cname + "."
            signode += addnodes.desc_addname(nodetext, nodetext)

        signode += addnodes.desc_name(name, name)
        if arglist:
            # TODO: parse the parameter list
            signode += addnodes.desc_parameterlist()
        else:
            if self.needs_arglist:
                signode += addnodes.desc_parameterlist()

        if retann:
            # TODO: parse annotation
            children = []
            signode += addnodes.desc_returns(retann, "", *children)

        return fullname


class VyContractLike(VyObject):
    allow_nesting = True


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
        "contract": VyContractLike,
        "interface": VyContractLike,
        "event": VyEvent,
        "enum": VyEnum,
        "struct": VyStruct,
        "immutable": VyGlobalLike,
        "statevar": VyGlobalLike,
        "constant": VyConstant,
        "function": VyFunction,
    }
