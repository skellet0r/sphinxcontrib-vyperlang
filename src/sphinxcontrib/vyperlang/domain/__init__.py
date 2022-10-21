from typing import Dict, NamedTuple

from sphinx.domains import Domain, ObjType
from sphinx.locale import _

from sphinxcontrib.vyperlang.domain.directives import VyContract, VyCurrentContract


class ContractEntry(NamedTuple):
    docname: str
    node_id: str


class VyperDomain(Domain):
    """Vyper language domain."""

    name = "vy"
    label = "Vyper"
    object_types = {"contract": ObjType(_("contract"))}
    directives = {"contract": VyContract, "currentcontract": VyCurrentContract}
    initial_data: Dict[str, Dict[str, NamedTuple]] = {"contracts": {}}

    @property
    def contracts(self) -> Dict:
        return self.data.setdefault("contracts", {})

    def add_contract(self, name: str, docname: str, node_id: str) -> None:
        self.contracts[name] = ContractEntry(docname, node_id)

    def clear_doc(self, docname: str) -> None:
        for contract, entry in self.contracts.items():
            if entry.docname == docname:
                del self.contracts[contract]
