
import asyncio

from aiohttp import web, ClientSession, WSMsgType
from urllib.parse import urlsplit

TARGET = "http://10.166.218.86:50006"
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
    # Connection 헤더가 별도로 지정한 헤더도 제외
    excluded = set(HOP_HEADERS)
    excluded.update(
        value.strip().lower()
        for value in headers.get("Connection", "").split(",")
        if value.strip()
    )
    return {
        k: v for k, v in headers.items()
        if k.lower() not in excluded
        and k.lower() not in {"host", "content-length"}
    }


async def proxy(request):
    upstream_url = TARGET + request.rel_url.path_qs

    # WebSocket 요청 중계
    if request.headers.get("Upgrade", "").lower() == "websocket":
        ws_down = web.WebSocketResponse()
        await ws_down.prepare(request)

        session = request.app["session"]
        protocols = [
            p.strip()
            for p in request.headers.get(
                "Sec-WebSocket-Protocol", ""
            ).split(",")
            if p.strip()
        ]

        ws_url = upstream_url.replace("http://", "ws://", 1)

        try:
            async with session.ws_connect(
                ws_url,
                protocols=protocols,
                headers=clean_headers(request.headers),
                origin=request.headers.get("Origin"),
                autoping=True,
            ) as ws_up:

                async def browser_to_upstream():
                    async for msg in ws_down:
                        if msg.type == WSMsgType.TEXT:
                            await ws_up.send_str(msg.data)
                        elif msg.type == WSMsgType.BINARY:
                            await ws_up.send_bytes(msg.data)
                        elif msg.type == WSMsgType.ERROR:
                            break

                async def upstream_to_browser():
                    async for msg in ws_up:
                        if msg.type == WSMsgType.TEXT:
                            await ws_down.send_str(msg.data)
                        elif msg.type == WSMsgType.BINARY:
                            await ws_down.send_bytes(msg.data)
                        elif msg.type == WSMsgType.ERROR:
                            break

                tasks = [
                    asyncio.create_task(browser_to_upstream()),
                    asyncio.create_task(upstream_to_browser()),
                ]
                try:
                    await asyncio.wait(
                        tasks, return_when=asyncio.FIRST_COMPLETED
                    )
                finally:
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(
                        *tasks, return_exceptions=True
                    )
        except Exception:
            await ws_down.close(code=1011, message=b"Proxy error")
        finally:
            await ws_down.close()

        return ws_down

    # 일반 HTTP 요청 중계
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

        async for chunk in upstream.content.iter_chunked(64 * 1024):
            await response.write(chunk)

        await response.write_eof()
        return response


async def on_startup(app):
    app["session"] = ClientSession(
        timeout=None,
        auto_decompress=False,
    )


async def on_cleanup(app):
    await app["session"].close()


app = web.Application(client_max_size=100 * 1024**2)
app.router.add_route("*", "/{path:.*}", proxy)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
