import asyncio
from typing import Any, Optional

from httpx import AsyncClient, Headers, Response, codes
from loguru import logger
from websockets.legacy.client import Connect, WebSocketClientProtocol


class AsyncWebSocketClient:
    def __init__(
        self,
        uri: str,
        ping_interval: Optional[float] = None,
        delay_send: float = 0,
        delay_recv: float = 0,
        debug: bool = False,
    ) -> None:
        self.__con = Connect(uri, ping_interval=ping_interval)
        self.__ws: Optional[WebSocketClientProtocol] = None
        self.__delay_send = delay_send
        self.__delay_recv = delay_recv
        self.__debug = debug

    @property
    def _con(self) -> Connect:
        return self.__con

    @property
    def _ws(self) -> WebSocketClientProtocol:
        assert self.__ws is not None
        return self.__ws

    def _set_ws(self, ws: WebSocketClientProtocol) -> None:
        self.__ws = ws

    @property
    def _delay_send(self) -> float:
        return self.__delay_send

    @property
    def _delay_recv(self) -> float:
        return self.__delay_recv

    @property
    def _debug(self) -> bool:
        return self.__debug

    async def __aenter__(self) -> Any:
        self._set_ws(await self._con.__aenter__())
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._con.__aexit__(*args)

    async def _sleep_send(self) -> None:
        if self._delay_send > 0:
            await asyncio.sleep(self._delay_send)

    async def _sleep_recv(self) -> None:
        if self._delay_recv > 0:
            await asyncio.sleep(self._delay_recv)

    async def send(self, message: Any) -> None:
        await self._sleep_send()
        await self._ws.send(message)
        if self._debug:
            logger.debug(str(message))

    async def recv(self) -> Any:
        await self._sleep_recv()
        r = await self._ws.recv()
        if self._debug:
            logger.debug(str(r))
        return r


class AsyncHttpClient:
    def __init__(
        self,
        base_url: str = "",
        timeout: Optional[float] = None,
        delay: float = 0,
        debug: bool = False,
    ) -> None:
        self.__client = AsyncClient(base_url=base_url, timeout=timeout)
        self.__delay = delay
        self.__debug = debug

    @property
    def _client(self) -> AsyncClient:
        return self.__client

    @property
    def _delay(self) -> float:
        return self.__delay

    @property
    def _debug(self) -> bool:
        return self.__debug

    async def __aenter__(self) -> Any:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._client.__aexit__(*args)

    async def _sleep(self) -> None:
        if self._delay > 0:
            await asyncio.sleep(self._delay)

    def _response_processing(
        self,
        r: Response,
        url_path: str,
        headers: dict[str, Any],
        data: dict[str, Any],
    ) -> tuple[Headers, Any]:
        rheaders = r.headers
        if int(rheaders["content-length"]) > 0:
            rdata = r.json()
        else:
            rdata = {}
        if r.status_code != codes.OK:
            logger.error(
                "\n%s\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, r, rheaders, rdata)
            )
            rdata = {}
        elif self._debug:
            logger.debug(
                "\n%s\n%s\n%s\n%s\n%s\n%s"
                % (url_path, headers, data, r, rheaders, rdata)
            )
        return rheaders, rdata

    async def get(
        self,
        url_path: str,
        headers: dict[str, Any],
        data: dict[str, Any],
    ) -> tuple[Headers, Any]:
        await self._sleep()
        r = await self._client.get(url_path, headers=headers, params=data)
        return self._response_processing(r, url_path, headers, data)

    async def post(
        self,
        url_path: str,
        headers: dict[str, Any],
        data: dict[str, Any],
    ) -> tuple[Headers, Any]:
        await self._sleep()
        r = await self._client.post(url_path, headers=headers, json=data)
        return self._response_processing(r, url_path, headers, data)

    async def post_params(
        self,
        url_path: str,
        headers: dict[str, Any],
        data: dict[str, Any],
    ) -> tuple[Headers, Any]:
        await self._sleep()
        r = await self._client.post(url_path, headers=headers, params=data)
        return self._response_processing(r, url_path, headers, data)

    async def delete(
        self,
        url_path: str,
        headers: dict[str, Any],
        data: dict[str, Any],
    ) -> tuple[Headers, Any]:
        await self._sleep()
        r = await self._client.delete(url_path, headers=headers, params=data)
        return self._response_processing(r, url_path, headers, data)
