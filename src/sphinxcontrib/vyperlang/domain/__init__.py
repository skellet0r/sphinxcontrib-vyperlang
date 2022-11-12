from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Tuple

from docutils import nodes
from sphinx.addnodes import pending_xref
from sphinx.builders import Builder
from sphinx.domains import Domain, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.locale import _, __
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.nodes import make_refnode

from sphinxcontrib.vyperlang.domain.directives import (
    VyContract,
    VyCurrentContract,
    VyEnum,
    VyEvent,
    VyStruct,
    VyVariable,
)
from sphinxcontrib.vyperlang.domain.indices import VyperContractIndex

logger = logging.getLogger(__name__)


class ObjectEntry(NamedTuple):
    docname: str
    node_id: str
    metadata: Dict[str, Any]


class VyperDomain(Domain):
    """Vyper language domain."""

    name = "vy"
    label = "Vyper"
    object_types = {
        "contract": ObjType(_("contract"), "contract"),
        "event": ObjType(_("event"), "event"),
        "enum": ObjType(_("enum"), "enum"),
        "struct": ObjType(_("struct"), "struct"),
        "constant": ObjType(_("constant"), "const"),
        "immutable": ObjType(_("immutable"), "immutable"),
        "storage": ObjType(_("storage variable"), "storage"),
    }
    directives = {
        "contract": VyContract,
        "currentcontract": VyCurrentContract,
        "event": VyEvent,
        "enum": VyEnum,
        "struct": VyStruct,
        "constant": VyVariable,
        "immutable": VyVariable,
        "storage": VyVariable,
    }
    roles = {
        "contract": XRefRole(),
        "event": XRefRole(),
        "enum": XRefRole(),
        "struct": XRefRole(),
        "const": XRefRole(),
        "immutable": XRefRole(),
        "storage": XRefRole(),
    }
    initial_data: Dict[str, Dict[str, ObjectEntry]] = {"objects": {}}
    indices = [VyperContractIndex]

    @property
    def objects(self) -> Dict:
        return self.data.setdefault("objects", {})

    def add_object(
        self, name: str, node_id: str, objtype: str, **metadata: Any
    ) -> None:
        """Add an object to the domain data."""
        objects = self.objects.setdefault(objtype, {})
        if name in objects:
            logger.warning(__(f"duplicate description of {name!r}"))
        objects[name] = ObjectEntry(self.env.docname, node_id, metadata)

    def clear_doc(self, docname: str) -> None:
        """Purge object entries from the domain data which were in a document."""
        for objtype, objects in self.objects.items():
            for name, entry in objects.copy().items():
                if entry.docname == docname:
                    del self.objects[objtype][name]

    def merge_domaindata(self, docnames: List[str], otherdata: Dict) -> None:
        """Merge domain data from a parallel process."""
        for objtype, objects in otherdata.items():
            for name, entry in objects.items():
                if entry.docname not in docnames:
                    continue
                elif name in self.objects.setdefault(objtype, {}):
                    logger.warning(__(f"duplicate description of {name!r}"))
                self.objects[objtype][name] = entry

    def get_objects(self) -> Iterable[Tuple[str, str, str, str, str, int]]:
        for objtype, objects in self.objects.items():
            for name, entry in objects.items():
                yield (name, name, objtype, entry.docname, entry.node_id, 0)

    def resolve_xref(
        self,
        env: BuildEnvironment,
        fromdocname: str,
        builder: Builder,
        typ: str,
        target: str,
        node: pending_xref,
        contnode: nodes.Element,
    ) -> Optional[nodes.Element]:
        objects = self.objects.setdefault(typ, {})
        if target not in objects:
            return None

        entry = objects[target]
        return make_refnode(
            builder, fromdocname, entry.docname, entry.node_id, contnode, target
        )
