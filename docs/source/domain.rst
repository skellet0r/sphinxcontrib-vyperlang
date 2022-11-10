The Vyper Domain
================

The Vyper domain (name **vy**) provides the following directives:

.. rst:directive:: .. vy:contract:: name

    This directive marks the beginning of the description of a contract.

    .. rubric:: options

    .. rst:directive:option:: synopsis: purpose
        :type: text

        A single sentence describing the purpose of the contract.

.. rst:directive:: .. vy:currentcontract:: name

    This directive tells Sphinx that the objects documented from here are in the given
    contract (like :rst:dir:`vy:contract`), but it will not create index entries.
    This is helpful in situations where documentation for objects in a contract are
    spread over multiple files or sections.
