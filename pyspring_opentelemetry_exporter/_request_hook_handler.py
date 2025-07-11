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
                span.set_attribute("user_agent", req.headers.get("user-agent", "unknown"))
                span.set_attribute("path", req.url.path)
    def client_request_hook(self, span: Span, scope: dict[str, Any], request: dict[str, Any]) -> None:
        if span and span.is_recording():
            span.set_attribute("client_request_url", str(request.get("url", "unknown")))
    def client_response_hook(self, span: Span, scope: dict[str, Any], response: dict[str, Any]) -> None:
        if span and span.is_recording():
            span.set_attribute("response_status_code", response.get("status_code", 0))


def provide_default_request_hook_handler() -> RequestHookHandler:
    return DefaultRequestHookHandler()