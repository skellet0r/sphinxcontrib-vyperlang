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

        contracts = self.domain.objects.setdefault("contract", {})
        for name, entry in contracts.items():
            if docnames and entry.docname not in docnames:
                continue

            entry = IndexEntry(
                name,
                0,
                entry.docname,
                entry.node_id,
                "",
                "",
                entry.metadata["synopsis"],
            )
            content.setdefault(name[0].lower(), []).append(entry)

        return sorted(content.items()), False
