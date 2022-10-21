from typing import Dict, Iterable, List, NamedTuple, Tuple

from sphinx.domains import Domain, ObjType
from sphinx.locale import _
from sphinx.roles import XRefRole

from sphinxcontrib.vyperlang.domain.directives import VyContract, VyCurrentContract


class ContractEntry(NamedTuple):
    docname: str
    node_id: str


class VyperDomain(Domain):
    """Vyper language domain."""

    name = "vy"
    label = "Vyper"
    object_types = {"contract": ObjType(_("contract"), "contract")}
    directives = {"contract": VyContract, "currentcontract": VyCurrentContract}
    roles = {"contract": XRefRole()}
    initial_data: Dict[str, Dict[str, NamedTuple]] = {"contracts": {}}

    @property
    def contracts(self) -> Dict:
        return self.data.setdefault("contracts", {})

    def add_contract(self, name: str, node_id: str) -> None:
        self.contracts[name] = ContractEntry(self.env.docname, node_id)

    def clear_doc(self, docname: str) -> None:
        for contract, entry in self.contracts.items():
            if entry.docname == docname:
                del self.contracts[contract]

    def merge_domaindata(self, docnames: List[str], otherdata: Dict) -> None:
        for contract, entry in otherdata["contracts"].items():
            if entry.docname in docnames:
                self.contracts[contract] = entry

    def get_objects(self) -> Iterable[Tuple[str, str, str, str, str, int]]:
        for contract, entry in self.contracts.items():
            # (name, dispname, type, docname, anchor, priority)
            yield (contract, contract, "contract", entry.docname, entry.node_id, 0)
