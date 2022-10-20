from typing import List

from docutils import nodes
from sphinx.util.docutils import SphinxDirective, switch_source_input
from sphinx.util.nodes import nested_parse_with_titles


class VyContract(SphinxDirective):
    """Directive marking the description of a new contract."""

    required_arguments = 1
    has_content = True

    def run(self) -> List[nodes.Node]:
        self.env.ref_context["vy:contract"] = self.arguments[0]

        content_node = nodes.section()
        with switch_source_input(self.state, self.content):
            content_node.document = self.state.document
            nested_parse_with_titles(self.state, self.content, content_node)

        return content_node.children


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
