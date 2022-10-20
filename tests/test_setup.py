from sphinxcontrib.vyperlang.domain import VyperDomain


def test_add_vyper_domain(app):
    assert "vy" in app.registry.domains
    assert app.registry.domains["vy"] is VyperDomain
