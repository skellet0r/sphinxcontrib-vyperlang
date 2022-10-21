from sphinx.domains import Index
from sphinx.locale import _


class VyperContractIndex(Index):
    """Vyper Contract Index."""

    name = "contractindex"
    localname = _("Vyper Contract Index")
    shortname = _("contracts")
