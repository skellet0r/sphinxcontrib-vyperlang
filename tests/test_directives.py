from sphinx.testing import restructuredtext


def test_vy_contract(app):
    text = ".. vy:contract:: sphinx"
    doctree = restructuredtext.parse(app, text)
    assert doctree.settings.env.ref_context.get("vy:contract") == "sphinx"


def test_vy_current_contract_updates_contract(app):
    text = """
    .. vy:contract:: sphinx

    .. vy:currentcontract:: foo
    """
    doctree = restructuredtext.parse(app, text)
    assert doctree.settings.env.ref_context.get("vy:contract") == "foo"


def test_vy_current_contract_clears_contract(app):
    text = """
    .. vy:contract:: sphinx

    .. vy:currentcontract:: None
    """
    doctree = restructuredtext.parse(app, text)
    assert doctree.settings.env.ref_context.get("vy:contract") is None
