import ast
import re
from inspect import Parameter
from typing import List, Optional, Tuple, Type

from docutils import nodes
from docutils.nodes import Node
from docutils.parsers.rst import directives
from docutils.parsers.rst.states import Inliner
from sphinx import addnodes
from sphinx.addnodes import pending_xref
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.locale import _
from sphinx.util.docfields import Field, GroupedField, TypedField
from sphinx.util.inspect import signature_from_str
from sphinx.util.nodes import make_id
from sphinx.util.typing import TextlikeNode

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
        refdomain="vy",
        reftype=reftype,
        reftarget=target,
        refspecific=refspecific,
        **kwargs,
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


# copied from sphinx/domains/python.py with minor modifications
def _parse_arglist(
    arglist: str, env: Optional[BuildEnvironment] = None
) -> addnodes.desc_parameterlist:
    """Parse a list of arguments using AST parser"""
    params = addnodes.desc_parameterlist(arglist)
    sig = signature_from_str("(%s)" % arglist)
    last_kind = None
    for param in sig.parameters.values():
        if param.kind != param.POSITIONAL_ONLY and last_kind == param.POSITIONAL_ONLY:
            # PEP-570: Separator for Positional Only Parameter: /
            params += addnodes.desc_parameter(
                "", "", addnodes.desc_sig_operator("", "/")
            )
        if param.kind == param.KEYWORD_ONLY and last_kind in (
            param.POSITIONAL_OR_KEYWORD,
            param.POSITIONAL_ONLY,
            None,
        ):
            # PEP-3102: Separator for Keyword Only Parameter: *
            params += addnodes.desc_parameter(
                "", "", addnodes.desc_sig_operator("", "*")
            )

        node = addnodes.desc_parameter()
        if param.kind == param.VAR_POSITIONAL:
            node += addnodes.desc_sig_operator("", "*")
            node += addnodes.desc_sig_name("", param.name)
        elif param.kind == param.VAR_KEYWORD:
            node += addnodes.desc_sig_operator("", "**")
            node += addnodes.desc_sig_name("", param.name)
        else:
            node += addnodes.desc_sig_name("", param.name)

        if param.annotation is not param.empty:
            children = _parse_annotation(param.annotation, env)
            node += addnodes.desc_sig_punctuation("", ":")
            node += addnodes.desc_sig_space()
            node += addnodes.desc_sig_name("", "", *children)  # type: ignore
        if param.default is not param.empty:
            if param.annotation is not param.empty:
                node += addnodes.desc_sig_space()
                node += addnodes.desc_sig_operator("", "=")
                node += addnodes.desc_sig_space()
            else:
                node += addnodes.desc_sig_operator("", "=")
            node += nodes.inline(
                "", param.default, classes=["default_value"], support_smartquotes=False
            )

        params += node
        last_kind = param.kind

    if last_kind == Parameter.POSITIONAL_ONLY:
        # PEP-570: Separator for Positional Only Parameter: /
        params += addnodes.desc_parameter("", "", addnodes.desc_sig_operator("", "/"))

    return params


# copied from sphinx/domains/python.py with minor modifications
class VyXrefMixin:
    def make_xref(
        self,
        rolename: str,
        domain: str,
        target: str,
        innernode: Type[TextlikeNode] = nodes.emphasis,
        contnode: Node = None,
        env: BuildEnvironment = None,
        inliner: Inliner = None,
        location: Node = None,
    ) -> Node:
        # we use inliner=None to make sure we get the old behaviour with a single
        # pending_xref node
        result = super().make_xref(
            rolename,
            domain,
            target,  # type: ignore
            innernode,
            contnode,
            env,
            inliner=None,
            location=None,
        )
        if isinstance(result, pending_xref):
            result["refspecific"] = True
            result["vy:contract"] = env.ref_context.get("vy:contract")
            result["vy:interface"] = env.ref_context.get("vy:interface")

            reftype, reftarget, reftitle, _ = parse_reftarget(target)
            if reftarget != reftitle:
                result["reftype"] = reftype
                result["reftarget"] = reftarget

                result.clear()
                result += innernode(reftitle, reftitle)

        return result

    def make_xrefs(
        self,
        rolename: str,
        domain: str,
        target: str,
        innernode: Type[TextlikeNode] = nodes.emphasis,
        contnode: Node = None,
        env: BuildEnvironment = None,
        inliner: Inliner = None,
        location: Node = None,
    ) -> List[Node]:
        delims = r"(\s*[\[\]\(\),](?:\s*o[rf]\s)?\s*|\s+o[rf]\s+|\s*\|\s*|\.\.\.)"
        delims_re = re.compile(delims)
        sub_targets = re.split(delims, target)

        split_contnode = bool(contnode and contnode.astext() == target)

        in_literal = False
        results = []
        for sub_target in filter(None, sub_targets):
            if split_contnode:
                contnode = nodes.Text(sub_target)

            if in_literal or delims_re.match(sub_target):
                results.append(contnode or innernode(sub_target, sub_target))
            else:
                results.append(
                    self.make_xref(
                        rolename,
                        domain,
                        sub_target,
                        innernode,
                        contnode,
                        env,
                        inliner,
                        location,
                    )
                )

        return results


class VyField(VyXrefMixin, Field):
    pass


class VyGroupedField(VyXrefMixin, GroupedField):
    pass


class VyTypedField(VyXrefMixin, TypedField):
    pass


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

        objtype = self.objtype
        if objtype in ("contract", "interface"):
            # contracts and interfaces should only have a name
            is_valid_sig = name and not (prefix or arglist or retann)
            # interfaces can't be under interfaces
            # contracts can't be under contracts / interfaces
            is_valid_nesting = (
                not (contract_name or interface_name)
                if objtype == "contract"
                else not interface_name
            )
            if not (is_valid_sig or is_valid_nesting):
                raise ValueError

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
            signode += _parse_arglist(arglist, self.env)
        elif self.needs_arglist:
            signode += addnodes.desc_parameterlist()

        if retann:
            children = _parse_annotation(retann, self.env)
            signode += addnodes.desc_returns(retann, "", *children)

        return fullname, prefix

    def _object_hierarchy_parts(self, sig_node):
        if "fullname" not in sig_node:
            return ()
        contract_name = sig_node.get("contract")
        fullname = sig_node["fullname"]

        if contract_name:
            return (contract_name, *fullname.split("."))
        else:
            return tuple(fullname.split("."))

    def get_index_text(self, contract_name, name):
        raise NotImplementedError("Must be implemented in subclasses")

    def add_target_and_index(self, name_cls, sig, signode):
        contract_name = self.env.ref_context.get("vy:contract")
        fullname = (contract_name + "." if contract_name else "") + name_cls[0]

        node_id = make_id(self.env, self.state.document, "", fullname)
        signode["ids"].append(node_id)
        self.state.document.note_explicit_target(signode)

        domain = self.env.get_domain("vy")
        domain.note_object(fullname, self.objtype, node_id, location=signode)

        if "noindexentry" not in self.options:
            indextext = self.get_index_text(contract_name, name_cls)
            if indextext:
                self.indexnode["entries"].append(
                    ("single", indextext, node_id, "", None)
                )

    def before_content(self):
        if self.names:
            fullname, _ = self.names[-1]
            if self.objtype in ("contract", "interface"):
                self.env.ref_context[f"vy:{self.objtype}"] = fullname

    def after_content(self) -> None:
        if self.objtype in ("contract", "interface"):
            self.env.ref_context[f"vy:{self.objtype}"] = ""

    def _toc_entry_name(self, sig_node):
        if not sig_node.get("_toc_parts"):
            return ""

        config = self.env.app.config
        objtype = sig_node.parent.get("objtype")
        if config.add_function_parentheses and objtype == "function":
            parens = "()"
        else:
            parens = ""
        *parents, name = sig_node["_toc_parts"]
        if config.toc_object_entries_show_parents == "domain":
            return sig_node.get("fullname", name) + parens
        if config.toc_object_entries_show_parents == "hide":
            return name + parens
        if config.toc_object_entries_show_parents == "all":
            return ".".join(parents + [name + parens])
        return ""


class VyGlobalLike(VyObject):
    option_spec = {
        "type": directives.unchanged_required,
        "public": directives.flag,
        **VyObject.option_spec,
    }

    @property
    def signature_prefix(self):
        if "public" in self.options:
            return [addnodes.desc_sig_keyword("", "public"), addnodes.desc_sig_space()]
        else:
            return []

    def handle_signature(self, sig, signode):
        fullname, prefix = super().handle_signature(sig, signode)

        typ = self.options.get("type")
        if typ:
            annotations = _parse_annotation(typ, self.env)
            signode += addnodes.desc_annotation(
                typ,
                "",
                addnodes.desc_sig_punctuation("", ":"),
                addnodes.desc_sig_space(),
                *annotations,
            )

        return fullname, prefix

    def get_index_text(self, contract_name: str, name_cls: Tuple[str, str]) -> str:
        name, cls = name_cls
        if contract_name:
            return _("%s (in contract %s)") % (name, contract_name)
        else:
            return _(f"%s (built-in {self.objtype})") % name


class VyConstant(VyGlobalLike):
    option_spec = {"value": directives.unchanged_required, **VyGlobalLike.option_spec}

    def handle_signature(self, sig, signode):
        fullname, prefix = super().handle_signature(sig, signode)

        value = self.options.get("value")
        if value:
            signode += addnodes.desc_annotation(
                value,
                "",
                addnodes.desc_sig_space(),
                addnodes.desc_sig_punctuation("", "="),
                addnodes.desc_sig_space(),
                nodes.Text(value),
            )

        return fullname, prefix


class VyEvent(VyObject):
    doc_field_types = [
        VyTypedField(
            "topic",
            names=("topic",),
            typenames=("type", "ttype"),
            label=_("Topics"),
            typerolename="obj",
            can_collapse=True,
        ),
        VyTypedField(
            "data",
            names=("data",),
            typenames=("type", "dtype"),
            label=_("Data"),
            typerolename="obj",
            can_collapse=True,
        ),
    ]

    def get_index_text(self, contract_name, name_cls):
        if not contract_name:
            return _("%s (built-in event)") % name_cls[0]
        return _("%s (event in %s)") % (name_cls[0], contract_name)


class VyEnum(VyObject):
    doc_field_types = [
        VyGroupedField(
            "element", names=("element", "elem"), label=_("Elements"), can_collapse=True
        )
    ]

    def get_index_text(self, contract_name, name_cls):
        if not contract_name:
            return _("%s (built-in enum)") % name_cls[0]
        return _("%s (enum in %s)") % (name_cls[0], contract_name)


class VyStruct(VyObject):
    doc_field_types = [
        VyTypedField(
            "member",
            names=("member",),
            typenames=("type", "mtype"),
            label=_("Members"),
            typerolename="obj",
            can_collapse=True,
        )
    ]

    def get_index_text(self, contract_name, name_cls):
        if not contract_name:
            return _("%s (built-in struct)") % name_cls[0]
        return _("%s (struct in %s)") % (name_cls[0], contract_name)


class VyFunction(VyObject):
    needs_arglist = True
    option_spec = {
        "mutability": lambda arg: directives.choice(arg, MUTABILITY),
        "visibility": lambda arg: directives.choice(arg, VISIBILITY),
        **VyObject.option_spec,
    }
    doc_field_types = [
        VyTypedField(
            "parameter",
            names=("parameter", "param", "argument", "arg"),
            typenames=("type", "paramtype"),
            label=_("Parameters"),
            typerolename="obj",
            can_collapse=True,
        ),
        VyGroupedField(
            "revert",
            names=("revert", "except", "raise"),
            label=_("Reverts"),
            can_collapse=True,
        ),
        VyField(
            "returnvalue",
            names=("return", "returns"),
            label=_("Returns"),
            has_arg=False,
        ),
        VyField(
            "returntype",
            names=("rtype",),
            label=_("Return type"),
            has_arg=False,
            bodyrolename="obj",
        ),
    ]

    def add_target_and_index(self, name_cls, sig, signode):
        super().add_target_and_index(name_cls, sig, signode)
        if "noindexentry" not in self.options:
            contract_name = self.env.ref_context.get("vy:contract", "")
            node_id = signode["ids"][0]

            name, cls = name_cls
            if contract_name:
                text = _("%s() (in contract %s)") % (name, contract_name)
                self.indexnode["entries"].append(("single", text, node_id, "", None))
            else:
                text = "%s; %s()" % (_("built-in function"), name)
                self.indexnode["entries"].append(("pair", text, node_id, "", None))

    def get_index_text(self, modname, name_cls):
        # add index in own add_target_and_index() instead.
        return None


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
