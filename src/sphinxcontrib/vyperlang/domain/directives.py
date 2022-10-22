import re
from typing import List, Tuple

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.locale import _, __
from sphinx.util import logging
from sphinx.util.docfields import GroupedField, TypedField
from sphinx.util.docutils import SphinxDirective, switch_source_input
from sphinx.util.nodes import make_id, nested_parse_with_titles

logger = logging.getLogger(__name__)

SIMPLE_SIG = re.compile(r"\w+")


class VyContract(SphinxDirective):
    """Directive marking the description of a new contract."""

    required_arguments = 1
    option_spec = {"noindex": directives.flag, "synopsis": directives.unchanged}
    has_content = True

    def run(self) -> List[nodes.Node]:
        cname = self.arguments[0]
        self.env.ref_context["vy:contract"] = cname

        content_node = nodes.section()
        with switch_source_input(self.state, self.content):
            content_node.document = self.state.document
            nested_parse_with_titles(self.state, self.content, content_node)

        if "noindex" in self.options:
            return content_node.children

        domain = self.env.get_domain("vy")
        node_id = make_id(self.env, self.state.document, "contract", cname)
        target = nodes.target("", "", ids=[node_id])
        index = addnodes.index(entries=[("single", cname, node_id, "", None)])

        self.set_source_info(target)
        self.state.document.note_explicit_target(target)
        domain.add_object(
            cname, node_id, "contract", synopsis=self.options.get("synopsis", "")
        )

        return [target, index, *content_node.children]


class VyCurrentContract(SphinxDirective):
    """Directive marking the description of a contract previously defined."""

    required_arguments = 1

    def run(self) -> List[nodes.Node]:
        cname = self.arguments[0]
        if cname == "None" and "vy:contract" in self.env.ref_context:
            del self.env.ref_context["vy:contract"]
        else:
            self.env.ref_context["vy:contract"] = cname

        return []


class VySimpleObjectBase(ObjectDescription):
    """Base class for VyEvent, VyEnum, and VyStruct."""

    def handle_signature(self, sig: str, signode: addnodes.desc_signature) -> str:
        mo = SIMPLE_SIG.fullmatch(sig)
        if mo is None:
            logger.warning(__(f"invalid {self.objtype} signature: {sig!r}"))
            raise ValueError

        cname = self.env.ref_context.get("vy:contract")
        if cname is None:
            logger.warning(
                __(f"{self.objtype} encountered outside of a contract: {sig!r}")
            )
            raise ValueError

        signode["contract"] = cname
        signode["fullname"] = fullname = f"{cname}.{sig}"

        if self.env.config.vy_add_contract_names:
            nodetext = cname + "."
            signode += addnodes.desc_addname(nodetext, nodetext)

        signode += addnodes.desc_name(sig, sig)
        return fullname

    def _object_hierarchy_parts(
        self, signode: addnodes.desc_signature
    ) -> Tuple[str, ...]:
        fullname = signode.get("fullname", "")
        return tuple(fullname.split("."))

    def _toc_entry_name(self, signode: addnodes.desc_signature) -> str:
        return signode.get("fullname", "")

    def add_target_and_index(
        self, fullname: str, sig: str, signode: addnodes.desc_signature
    ) -> None:
        cname = self.env.ref_context.get("vy:contract")
        domain = self.env.get_domain("vy")
        node_id = make_id(self.env, self.state.document, "", fullname)

        signode["ids"].append(node_id)
        self.state.document.note_explicit_target(signode)
        domain.add_object(fullname, node_id, self.objtype)

        if "noindexentry" not in self.options:
            indextext = _(f"{sig}; {cname}")
            self.indexnode["entries"].append(("pair", indextext, node_id, "", None))


class VyEvent(VySimpleObjectBase):
    """Directive marking the description of an event."""

    doc_field_types = [
        TypedField(
            "topics",
            names=("topic",),
            typenames=("topictype",),
            label=_("Topics"),
            can_collapse=True,
        ),
        TypedField(
            "data",
            names=("data",),
            typenames=("datatype",),
            label=_("Data"),
            can_collapse=True,
        ),
    ]


class VyEnum(VySimpleObjectBase):
    """Directive marking the description of an enum."""

    doc_field_types = [
        GroupedField(
            "elements",
            names=("element", "elem"),
            label=_("Elements"),
            can_collapse=True,
        )
    ]


class VyStruct(VySimpleObjectBase):
    """Directive marking the description of a struct."""

    doc_field_types = [
        TypedField(
            "members",
            names=("member",),
            typenames=("membertype",),
            label=_("Members"),
            can_collapse=True,
        )
    ]
