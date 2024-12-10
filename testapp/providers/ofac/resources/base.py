import asyncio
import logging
from abc import abstractmethod
from typing import Dict

import aiohttp

from testapp import http
from testapp.domains.core import (
    constants as core_constants,
)

logger = logging.getLogger(__name__)


class BaseResource:
    def __init__(self) -> None:
        self.base_url = "https://sanctionslistservice.ofac.treas.gov"
        self.headers = {
            "Accept": "application/xml",
        }

    @property
    @abstractmethod
    def resource(self) -> str:
        raise NotImplementedError("Resource not implemented.")

    async def get(
        self,
        resource: str,
        headers: Dict[str, str] = dict(),
    ) -> aiohttp.ClientResponse:
        url = self.base_url + resource
        try:
            raw_response = await http.client.session.get(
                url,
                headers=self.headers | headers,
                timeout=aiohttp.ClientTimeout(
                    total=core_constants.DEFAULT_VENDOR_TIMEOUT_SECONDS * 3
                ),
            )

        except (
            asyncio.exceptions.TimeoutError,
            asyncio.exceptions.CancelledError,
        ) as e:
            logger.error(
                f"[OFAC] GET request to {url} failed",
                extra={
                    "error": str(e),
                },
            )
            raise TimeoutError("timeout error when calling OFAC provider")

        return raw_response