from abc import ABC, abstractmethod
from typing import Any, Optional
from fastapi import Request, Response
from opentelemetry.trace.span import Span

class RequestHookHandler(ABC):
    @abstractmethod
    def server_request_hook(self, span: Span, scope: dict[str, Any]) -> None: ...

    @abstractmethod
    def client_request_hook(self, span: Span, scope: dict[str, Any], request: dict[str, Any]) -> None: ...

    @abstractmethod
    def client_response_hook(self, span: Span, scope: dict[str, Any], response: dict[str, Any]) -> None: ...

class DefaultRequestHookHandler(RequestHookHandler):
    def server_request_hook(self, span: Span, scope: dict[str, Any]) -> None:
        if span and span.is_recording():
            req: Optional[Request] = scope.get("request")
            if req:
                span.set_attribute("http.method", req.method)
                span.set_attribute("http.url", str(req.url))
                span.set_attribute("http.path", req.url.path)
                span.set_attribute("http.query", req.url.query)
                span.set_attribute("http.headers.user_agent", req.headers.get("user-agent", "unknown"))
                span.set_attribute("http.headers.host", req.headers.get("host", "unknown"))
                span.set_attribute("http.client_ip", req.client.host if req.client else "unknown")

    def server_response_hook(self, span: Span, scope: dict[str, Any], response: dict[str, Any]) -> None:
        if span and span.is_recording():
            status_code = response.get("status_code", 0)
            span.set_attribute("http.server_response.status_code", status_code)
            span.set_attribute("http.server_response.headers", str(response.get("headers", {})))
            if status_code >= 500:
                error = str(response.get("body", ""))
                span.set_attribute("error.preview", error)
                span.set_attribute("error", True)

    def client_request_hook(self, span: Span, scope: dict[str, Any], request: dict[str, Any]) -> None:
        if span and span.is_recording():
            span.set_attribute("http.client_request.url", str(request.get("url", "unknown")))
            span.set_attribute("http.client_request.method", request.get("method", "GET"))
            span.set_attribute("http.client_request.headers", str(request.get("headers", {})))

    def client_response_hook(self, span: Span, scope: dict[str, Any], response: dict[str, Any]) -> None:
        if span and span.is_recording():
            span.set_attribute("http.client_response.status_code", response.get("status_code", 0))
            span.set_attribute("http.client_response.headers", str(response.get("headers", {})))
            if response.get("status_code", 0) >= 500:
                error = str(response.get("body", ""))
                span.set_attribute("error.preview", error)

def provide_default_request_hook_handler() -> RequestHookHandler:
    return DefaultRequestHookHandler()