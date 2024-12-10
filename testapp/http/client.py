import logging
from typing import Literal

from aiohttp import ClientSession, TCPConnector

logger = logging.getLogger(__name__)

HTTPClientNamespace = Literal[
    "Testapp",
]


class _HttpClient:
    """
    Manages a global persistent aiohttp session. Class exported as a
    singleton so that we reuse the session. Clients who
    have special connection pool requirements should create their
    own persistent session.
    """

    def __init__(
        self,
        namespace: HTTPClientNamespace = "Testapp",
        limit_per_host: int = 0,
    ) -> None:
        self._session: ClientSession | None = None
        self.namespace = namespace
        self.limit_per_host = limit_per_host

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            raise ValueError("HTTP client not initialized.")
        return self._session

    async def initialize(self) -> None:
        """
        Client must be initialized inside an async method
        https://stackoverflow.com/a/61741161
        """
        logger.info(f"Initializing aiohttp session for {self.namespace=}")
        tcp_connector = TCPConnector(
            # default to unlimited, which is capped by limit
            limit_per_host=self.limit_per_host,
            limit=100,  # this is the default -- allows 100 connections in total
        )
        self._session = ClientSession(
            connector=tcp_connector,
        )

    async def cleanup(self) -> None:
        logger.info("Closing aiohttp session")
        if self.session and not self.session.closed:
            await self.session.close()