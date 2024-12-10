import logging
from datetime import UTC, datetime

from .base import BaseResource

logger = logging.getLogger(__name__)


class OFACChangesResource(BaseResource):
    @property
    def resource(self) -> str:
        return "/changes/history"

    async def get_latest_ofac_version(self) -> int:
        current_year = datetime.now(UTC).year
        response = await self.get(
            self.resource + f"/{current_year}",
            headers={"Accept": "application/json"},
        )
        # if no updates for current year, check previous year
        if len(await response.json()) == 0:
            response = await self.get(
                self.resource + f"/{current_year - 1}", headers=self.headers
            )

        json_resp = await response.json()

        latest_version: int = json_resp[-1]["publicationID"]
        return latest_version