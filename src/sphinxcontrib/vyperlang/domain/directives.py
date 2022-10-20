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
