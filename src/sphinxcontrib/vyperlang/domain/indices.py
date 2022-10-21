from typing import Dict, Iterable, List, Tuple

from sphinx.domains import Index, IndexEntry
from sphinx.locale import _


class VyperContractIndex(Index):
    """Vyper Contract Index."""

    name = "contractindex"
    localname = _("Vyper Contract Index")
    shortname = _("contracts")

    def generate(
        self, docnames: Iterable[str] = None
    ) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
        content: Dict[str, List[IndexEntry]] = {}

        for contract, (docname, node_id, synopsis) in self.domain.contracts.items():
            if docnames and docname not in docnames:
                continue

            entry = IndexEntry(contract, 0, docname, node_id, "", "", synopsis)
            content.setdefault(contract[0].lower(), []).append(entry)

        return sorted(content.items()), False
