from typing import List

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.util.docutils import SphinxDirective, switch_source_input
from sphinx.util.nodes import make_id, nested_parse_with_titles


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
        domain.add_contract(cname, node_id, self.options.get("synopsis", ""))

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
