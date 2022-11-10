The Vyper Domain
================

Directives
----------

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

.. rst:directive:: .. vy:enum:: name

    Describes an enum.

    .. rubric:: Info Fields

    * ``element``: Description of an element.

    .. code-block:: rst

        .. vy:enum:: Roles

            :element Admin: An account with special privileges.
            :element Custodian: An account with privilege to call custodial functions.
            :element User: An account allowed to call user-facing functions.

    This will render like this:

    .. vy:enum:: Roles

        :element Admin: An account with special privileges.
        :element Custodian: An account with privilege to call custodial functions.
        :element User: An account allowed to call user-facing functions.

.. rst:directive:: .. vy:event:: name

    Describes an event.

    .. rubric:: Info Fields

    * ``topic``: Description of an indexed parameter.
    * ``topictype``: Type of a topic.
    * ``data``: Description of a non-indexed parameter.
    * ``datatype``: Type of data.

    .. code-block:: rst

        .. vy:event:: Transfer

            :topic address sender: The account tokens originated from.
            :topic address receiver: The account tokens were credited to.
            :data uint256 value: The amount of tokens transferred.

    This will render like this:

    .. vy:event:: Transfer

        :topic address sender: The account tokens originated from.
        :topic address receiver: The account tokens were credited to.
        :data uint256 value: The amount of tokens transferred.

Roles
-----

The following roles are provided for cross-referencing objects and are hyperlinked if a
matching identifier is found:

.. rst:role:: vy:contract

    Reference a contract.

.. rst:role:: vy:enum

    Reference an enum.

.. rst:role:: vy:event

    Reference an event.
