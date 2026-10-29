
import asyncio

from aiohttp import web, ClientSession, ClientTimeout, WSMsgType


TARGET = "http://10.166.218.86:50006"
BUFFER_SIZE = 64 * 1024

HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def clean_headers(headers):
    excluded = set(HOP_HEADERS)

    # Connection 헤더에 지정된 추가 홉별 헤더도 제거
    for value in headers.get("Connection", "").split(","):
        value = value.strip().lower()
        if value:
            excluded.add(value)

    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in excluded
        and key.lower() not in ("host", "content-length")
    }


async def proxy_websocket(request, upstream_url):
    protocols = [
        value.strip()
        for value in request.headers.get(
            "Sec-WebSocket-Protocol", ""
        ).split(",")
        if value.strip()
    ]

    ws_down = web.WebSocketResponse(protocols=protocols)
    await ws_down.prepare(request)

    ws_up = None

    try:
        ws_url = upstream_url.replace(
            "http://", "ws://", 1
        )

        session = request.app["session"]

        ws_up = await session.ws_connect(
            ws_url,
            headers=clean_headers(request.headers),
            protocols=protocols,
            origin=request.headers.get("Origin"),
            autoping=True,
        )

        async def browser_to_server():
            async for msg in ws_down:
                if msg.type == WSMsgType.TEXT:
                    await ws_up.send_str(msg.data)
                elif msg.type == WSMsgType.BINARY:
                    await ws_up.send_bytes(msg.data)
                elif msg.type == WSMsgType.ERROR:
                    break

        async def server_to_browser():
            async for msg in ws_up:
                if msg.type == WSMsgType.TEXT:
                    await ws_down.send_str(msg.data)
                elif msg.type == WSMsgType.BINARY:
                    await ws_down.send_bytes(msg.data)
                elif msg.type == WSMsgType.ERROR:
                    break

        tasks = [
            asyncio.ensure_future(browser_to_server()),
            asyncio.ensure_future(server_to_browser()),
        ]

        try:
            await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )
        finally:
            for task in tasks:
                task.cancel()

            await asyncio.gather(
                *tasks, return_exceptions=True
            )

    except Exception as exc:
        print("WebSocket proxy error: {}".format(exc))

    finally:
        if ws_up is not None:
            await ws_up.close()

        await ws_down.close()

    return ws_down


async def proxy_http(request, upstream_url):
    session = request.app["session"]
    body = await request.read()

    async with session.request(
        request.method,
        upstream_url,
        headers=clean_headers(request.headers),
        data=body if body else None,
        allow_redirects=False,
    ) as upstream:

        headers = clean_headers(upstream.headers)

        response = web.StreamResponse(
            status=upstream.status,
            headers=headers,
        )

        await response.prepare(request)

        async for chunk in upstream.content.iter_chunked(
            BUFFER_SIZE
        ):
            await response.write(chunk)

        await response.write_eof()
        return response


async def proxy(request):
    upstream_url = TARGET + request.rel_url.path_qs

    if (
        request.headers.get("Upgrade", "").lower()
        == "websocket"
    ):
        return await proxy_websocket(
            request, upstream_url
        )

    return await proxy_http(request, upstream_url)


async def on_startup(app):
    app["session"] = ClientSession(
        timeout=ClientTimeout(total=None),
        auto_decompress=False,
    )


async def on_cleanup(app):
    await app["session"].close()


app = web.Application(client_max_size=100 * 1024**2)

app.router.add_route("*", "/", proxy)
app.router.add_route("*", "/{path:.*}", proxy)

app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)


if __name__ == "__main__":
    web.run_app(
        app,
        host="0.0.0.0",
        port=8080,
    )
