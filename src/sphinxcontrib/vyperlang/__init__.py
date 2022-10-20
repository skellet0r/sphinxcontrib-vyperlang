from sphinx.application import Sphinx

from sphinxcontrib.vyperlang.domain import VyperDomain


def setup(app: Sphinx):
    app.add_domain(VyperDomain)
