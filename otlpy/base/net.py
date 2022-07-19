import asyncio
from typing import Any, Optional

from httpx import AsyncClient, Headers, Response, codes
from loguru import logger
from websockets.legacy.client import Connect


def websocket_connect(
    uri: str,
    ping_interval: Optional[float] = None,
) -> Connect:
    return Connect(uri, ping_interval=ping_interval)


def http_client(
    base_url: str = "",
    timeout: Optional[float] = None,
) -> AsyncClient:
    return AsyncClient(base_url=base_url, timeout=timeout)


def response_processing(
    r: Response,
    url_path: str,
    headers: dict[str, Any],
    data: dict[str, Any],
    debug: bool,
) -> tuple[Headers, dict[str, Any]]:
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
    elif debug:
        logger.debug(
            "\n%s\n%s\n%s\n%s\n%s\n%s"
            % (url_path, headers, data, r, rheaders, rdata)
        )
    return rheaders, rdata


async def get(
    client: AsyncClient,
    url_path: str,
    headers: dict[str, Any],
    data: dict[str, Any],
    sleep: float,
    debug: bool,
) -> tuple[Headers, dict[str, Any]]:
    r = await client.get(
        url_path,
        headers=headers,
        params=data,
    )
    if sleep > 0:
        await asyncio.sleep(sleep)
    return response_processing(r, url_path, headers, data, debug)


async def post(
    client: AsyncClient,
    url_path: str,
    headers: dict[str, Any],
    data: dict[str, Any],
    sleep: float,
    debug: bool,
) -> tuple[Headers, dict[str, Any]]:
    r = await client.post(
        url_path,
        headers=headers,
        json=data,
    )
    if sleep > 0:
        await asyncio.sleep(sleep)
    return response_processing(r, url_path, headers, data, debug)
