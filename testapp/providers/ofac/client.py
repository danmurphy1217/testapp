from .resources.ofac_changes_resource import OFACChangesResource
from .resources.ofac_entities_resource import OFACEntitiesResource


class _OFACClient:
    # NOTE: this is a singleton class, hence the prefix
    def __init__(self) -> None:
        self.ofac_entities_resource = OFACEntitiesResource()
        self.ofac_changes_resource = OFACChangesResource()

    @property
    def entities(self) -> OFACEntitiesResource:
        return self.ofac_entities_resource

    @property
    def changes(self) -> OFACChangesResource:
        return self.ofac_changes_resource


ofac_client = _OFACClient()