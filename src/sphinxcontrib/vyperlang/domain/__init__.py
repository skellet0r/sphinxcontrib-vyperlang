from sphinx.domains import Domain, ObjType
from sphinx.locale import _

from sphinxcontrib.vyperlang.domain.directives import VyContract, VyCurrentContract


class VyperDomain(Domain):
    """Vyper language domain."""

    name = "vy"
    label = "Vyper"
    object_types = {"contract": ObjType(_("contract"))}
    directives = {"contract": VyContract, "currentcontract": VyCurrentContract}
