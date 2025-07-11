import traceback
from typing import Awaitable, Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.middleware.base import _StreamingResponse
from opentelemetry.trace import get_current_span


class ResponseTraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            response = await call_next(request)
            if isinstance(response, _StreamingResponse):
                # _StreamingResponse - read the body by iterating
                body = b""
                async for chunk in response.body_iterator: # type: ignore
                    if isinstance(chunk, str):
                        body += chunk.encode('utf-8')
                    else:
                        body += chunk
                response = Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )
            else:
                # Regular Response object
                body = bytes(response.body) if response.body else b""
                response = Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

            span = get_current_span()
            if span and span.is_recording() and response.status_code >= 500:
                span.set_attribute("http.server_response.body", body.decode(errors="ignore"))
                span.set_attribute("http.server_response.status_code", response.status_code)

            return response
        except Exception as e:
            span = get_current_span()
            if span and span.is_recording():
                span.set_attribute("exception.message", str(e))
                span.set_attribute("exception.stacktrace", traceback.format_exc())
            raise