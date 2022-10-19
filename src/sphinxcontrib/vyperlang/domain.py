import ast
import re
from typing import List, Optional, Tuple

from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.addnodes import pending_xref
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
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


# copied from sphinx/domains/python.py with minor modifications
def parse_reftarget(
    reftarget: str, suppress_prefix: bool = False
) -> Tuple[str, str, str, bool]:
    """Parse a type string and return (reftype, reftarget, title, refspecific flag)"""
    refspecific = False
    if reftarget.startswith("."):
        reftarget = reftarget[1:]
        title = reftarget
        refspecific = True
    elif reftarget.startswith("~"):
        reftarget = reftarget[1:]
        title = reftarget.split(".")[-1]
    elif suppress_prefix:
        title = reftarget.split(".")[-1]
    else:
        title = reftarget

    return "obj", reftarget, title, refspecific


# copied from sphinx/domains/python.py with minor modifications
def type_to_xref(
    target: str, env: Optional[BuildEnvironment] = None, suppress_prefix: bool = False
) -> addnodes.pending_xref:
    """Convert a type string to a cross reference node."""
    if env:
        kwargs = {
            "vy:contract": env.ref_context.get("vy:contract"),
            "vy:interface": env.ref_context.get("vy:interface"),
        }
    else:
        kwargs = {}

    reftype, target, title, refspecific = parse_reftarget(target, suppress_prefix)
    return pending_xref(
        "",
        nodes.Text(title),
        refdomain="py",
        reftype=reftype,
        reftarget=target,
        refspecific=refspecific,
        **kwargs
    )


# copied from sphinx/domains/python.py with minor modifications
def _parse_annotation(annotation: str, env: BuildEnvironment) -> List[Node]:
    """Parse type annotation."""

    def unparse(node: ast.AST) -> List[Node]:
        if isinstance(node, ast.Attribute):
            return [nodes.Text("%s.%s" % (unparse(node.value)[0], node.attr))]
        elif isinstance(node, ast.BinOp):
            result: List[Node] = unparse(node.left)
            result.extend(unparse(node.op))
            result.extend(unparse(node.right))
            return result
        elif isinstance(node, ast.BitOr):
            return [
                addnodes.desc_sig_space(),
                addnodes.desc_sig_punctuation("", "|"),
                addnodes.desc_sig_space(),
            ]
        elif isinstance(node, ast.Constant):
            if node.value is Ellipsis:
                return [addnodes.desc_sig_punctuation("", "...")]
            elif isinstance(node.value, bool):
                return [addnodes.desc_sig_keyword("", repr(node.value))]
            elif isinstance(node.value, int):
                return [addnodes.desc_sig_literal_number("", repr(node.value))]
            elif isinstance(node.value, str):
                return [addnodes.desc_sig_literal_string("", repr(node.value))]
            else:
                # handles None, which is further handled by type_to_xref later
                # and fallback for other types that should be converted
                return [nodes.Text(repr(node.value))]
        elif isinstance(node, ast.Expr):
            return unparse(node.value)
        elif isinstance(node, ast.Index):
            return unparse(node.value)
        elif isinstance(node, ast.Invert):
            return [addnodes.desc_sig_punctuation("", "~")]
        elif isinstance(node, ast.List):
            result = [addnodes.desc_sig_punctuation("", "[")]
            if node.elts:
                # check if there are elements in node.elts to only pop the
                # last element of result if the for-loop was run at least
                # once
                for elem in node.elts:
                    result.extend(unparse(elem))
                    result.append(addnodes.desc_sig_punctuation("", ","))
                    result.append(addnodes.desc_sig_space())
                result.pop()
                result.pop()
            result.append(addnodes.desc_sig_punctuation("", "]"))
            return result
        elif isinstance(node, ast.Module):
            return sum((unparse(e) for e in node.body), [])
        elif isinstance(node, ast.Name):
            return [nodes.Text(node.id)]
        elif isinstance(node, ast.Subscript):
            result = unparse(node.value)
            result.append(addnodes.desc_sig_punctuation("", "["))
            result.extend(unparse(node.slice))
            result.append(addnodes.desc_sig_punctuation("", "]"))

            # Wrap the Text nodes inside brackets by literal node if
            # the subscript is a Literal
            if result[0] in ("Literal", "typing.Literal"):
                for i, subnode in enumerate(result[1:], start=1):
                    if isinstance(subnode, nodes.Text):
                        result[i] = nodes.literal("", "", subnode)
            return result
        elif isinstance(node, ast.UnaryOp):
            return unparse(node.op) + unparse(node.operand)
        elif isinstance(node, ast.Tuple):
            if node.elts:
                result = []
                for elem in node.elts:
                    result.extend(unparse(elem))
                    result.append(addnodes.desc_sig_punctuation("", ","))
                    result.append(addnodes.desc_sig_space())
                result.pop()
                result.pop()
            else:
                result = [
                    addnodes.desc_sig_punctuation("", "("),
                    addnodes.desc_sig_punctuation("", ")"),
                ]

            return result
        else:
            raise SyntaxError  # unsupported syntax

    try:
        tree = ast.parse(annotation, type_comments=True)
        result: List[Node] = []
        for node in unparse(tree):
            if isinstance(node, nodes.literal):
                result.append(node[0])
            elif isinstance(node, nodes.Text) and node.strip():
                if (
                    result
                    and isinstance(result[-1], addnodes.desc_sig_punctuation)
                    and result[-1].astext() == "~"
                ):
                    result.pop()
                    result.append(type_to_xref(str(node), env, suppress_prefix=True))
                else:
                    result.append(type_to_xref(str(node), env))
            else:
                result.append(node)
        return result
    except SyntaxError:
        return [type_to_xref(annotation, env)]


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
