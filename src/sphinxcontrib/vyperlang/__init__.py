from sphinx.application import Sphinx

from sphinxcontrib.vyperlang.domain import VyperDomain


def setup(app: Sphinx):
    app.add_config_value("vy_add_contract_names", False, "env")

    app.add_domain(VyperDomain)
