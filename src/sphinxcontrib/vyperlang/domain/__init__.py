from sphinx.domains import Domain

from sphinxcontrib.vyperlang.domain.directives import VyContract, VyCurrentContract


class VyperDomain(Domain):
    """Vyper language domain."""

    name = "vy"
    label = "Vyper"
    directives = {"contract": VyContract, "currentcontract": VyCurrentContract}
