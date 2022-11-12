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
        :noindex:

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
            :topic receiver: The account tokens were credited to.
            :topictype receiver: address
            :data uint256 value: The amount of tokens transferred.

    This will render like this:

    .. vy:event:: Transfer
        :noindex:

        :topic address sender: The account tokens originated from.
        :topic receiver: The account tokens were credited to.
        :topictype receiver: address
        :data uint256 value: The amount of tokens transferred.

.. rst:directive:: .. vy:struct:: name

    Describes a struct.

    .. rubric:: Info Fields

    * ``member``: Description of a member.
    * ``membertype``: Type of a member.

    .. code-block:: rst

        .. vy:struct:: Point

            :member int256 x: The x-coordinate.
            :member y: The y-coordinate.
            :membertype y: int256

    This will render like this:

    .. vy:struct:: Point
        :noindex:

        :member int256 x: The x-coordinate.
        :member y: The y-coordinate.
        :membertype y: int256

.. rst:directive:: .. vy:variable:: name

    Describes a constant, immutable, or a storage variable.

    .. rubric:: options

    .. rst:directive:option:: type: type of the variable
        :type: text

    .. rst:directive:option:: value: value of the variable
        :type: text

    .. code-block:: rst

        .. vy:variable:: SIZE
            :type: uint256
            :value: 42

        .. vy:variable:: point
            :type: Point


    This will render like this:

    .. vy:variable:: SIZE
        :type: uint256
        :value: 42
        :noindex:

    .. vy:variable:: point
        :type: Point
        :noindex:

.. rst:directive:: .. vy:function:: name

    Describes a function.

    .. rubric:: Info Fields

    * ``param``, ``parameter``, ``arg``, ``argument``: Description of a parameter.
    * ``paramtype``, ``type``: Type of a parameter.
    * ``revert``, ``reverts``, ``raises``, ``except``, ``exception``: Description of a
        revert case.
    * ``returns``, ``return``, ``retval``: Description of the return value.
    * ``rtype``: Return type.

    .. code-block:: rst

        .. vy:function:: main(_x: uint256, _y: uint32) -> uint8

            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
            tempor incididunt ut labore et dolore magna aliqua.

            :param uint256 _x: The seed value.
            :param _y: A salt value.
            :type _y: uint32
            :returns: The value after computation.
            :rtype: uint8

    This will render like this:

    .. vy:function:: main(_x: uint256, _y: uint32) -> uint8
        :noindex:

        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod
        tempor incididunt ut labore et dolore magna aliqua.

        :param uint256 _x: The seed value.
        :param _y: A salt value.
        :type _y: uint32
        :returns: The value after computation.
        :rtype: uint8

Roles
-----

The following roles are provided for cross-referencing objects and are hyperlinked if a
matching identifier is found:

.. note::

    For roles other than :rst:role:`vy:contract`, the target is specified as ``contract.name``,
    for example::

        ... :vy:func:`ERC20.transfer` emits the :vy:event:`ERC20.Transfer` event.

.. rst:role:: vy:contract

    Reference a contract.

.. rst:role:: vy:enum

    Reference an enum.

.. rst:role:: vy:event

    Reference an event.

.. rst:role:: vy:struct

    Reference a struct.

.. rst:role:: vy:var

    Reference a variable.

.. rst:role:: vy:func

    Reference a function.

Indices
-------

The *Vyper Contract Index* is available by linking to ``vy-contractindex``, like so:

.. code-block:: rst

    :ref:`vy-contractindex`
