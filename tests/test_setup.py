import pytest

from sphinxcontrib.vyperlang.domain import VyperDomain


@pytest.mark.sphinx(testroot="setup")
def test_add_vyper_domain(app):
    assert "vy" in app.registry.domains
    assert app.registry.domains["vy"] is VyperDomain
