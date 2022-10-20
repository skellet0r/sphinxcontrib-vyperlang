from sphinx.testing import restructuredtext


def test_vy_contract(app):
    text = ".. vy:contract:: sphinx"
    doctree = restructuredtext.parse(app, text)
    assert doctree.astext() == ""
    assert doctree.settings.env.ref_context.get("vy:contract") == "sphinx"
