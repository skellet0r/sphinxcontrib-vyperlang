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
    needs_arglist = False

    @property
    def signature_prefix(self):
        return []

    def handle_signature(self, sig, signode):
        mo = VY_SIG_RE.match(sig)
        if mo is None:
            raise ValueError
        prefix, name, arglist, retann = mo.groups(default="")

        # determine the contract, interface (if applicable), and full name
        contract_name = self.env.ref_context.get("vy:contract", "")
        interface_name = self.env.ref_context.get("vy:interface", "")

        add_contract = False if interface_name else True
        if interface_name:
            if prefix and prefix != interface_name:
                raise ValueError
            prefix = ""
            fullname = interface_name + "." + name
        else:
            fullname = prefix + "." + name if prefix else name

        signode["contract"] = contract_name
        signode["interface"] = interface_name
        signode["fullname"] = fullname

        sig_prefix = self.signature_prefix
        if sig_prefix:
            signode += addnodes.desc_annotation(str(sig_prefix), "", *sig_prefix)

        if prefix:
            signode += addnodes.desc_addname(prefix, prefix)
        elif contract_name and add_contract and self.env.config.add_contract_names:
            nodetext = contract_name + "."
            signode += addnodes.desc_addname(nodetext, nodetext)

        signode += addnodes.desc_name(name, name)
        if arglist:
            # signode += _parse_arglist(arglist, self.env)
            pass
        elif self.needs_arglist:
            signode += addnodes.desc_parameterlist()

        if retann:
            # children = _parse_annotation(retann, self.env)
            # signode += addnodes.desc_returns(retann, '', *children)
            pass

        return prefix, fullname


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
