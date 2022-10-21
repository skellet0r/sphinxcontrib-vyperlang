from sphinx.testing import restructuredtext


def test_contract(app):
    text = ".. vy:contract:: sphinx"
    doctree = restructuredtext.parse(app, text)
    assert doctree.settings.env.ref_context.get("vy:contract") == "sphinx"


def test_contract_updates_domain_data(app):
    text = ".. vy:contract:: sphinx"
    doctree = restructuredtext.parse(app, text)
    assert "sphinx" in doctree.settings.env.domains["vy"].contracts


def test_contract_rendered_text(app):
    text = ".. vy:contract:: sphinx"
    doctree = restructuredtext.parse(app, text)
    assert doctree.astext() == ""


def test_current_contract_updates_contract(app):
    text = """
    .. vy:contract:: sphinx

    .. vy:currentcontract:: foo
    """
    doctree = restructuredtext.parse(app, text)
    assert doctree.settings.env.ref_context.get("vy:contract") == "foo"


def test_current_contract_clears_contract(app):
    text = """
    .. vy:contract:: sphinx

    .. vy:currentcontract:: None
    """
    doctree = restructuredtext.parse(app, text)
    assert doctree.settings.env.ref_context.get("vy:contract") is None


def test_current_contract_rendered_text(app):
    text = ".. vy:currentcontract:: sphinx"
    doctree = restructuredtext.parse(app, text)
    assert doctree.astext() == ""
