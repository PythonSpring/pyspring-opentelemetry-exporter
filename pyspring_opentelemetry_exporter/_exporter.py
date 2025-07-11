

from py_spring_core import ApplicationContextRequired, EntityProvider, Properties
from typing import ClassVar, Optional
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from pyspring_opentelemetry_exporter._request_hook_handler import RequestHookHandler, provide_default_request_hook_handler
from pyspring_opentelemetry_exporter._response_trace_middleware import ResponseTraceMiddleware

class TracerExporterProperties(Properties):
    __key__ = "tracer_exporter"
    service_name: str
    endpoint: str

class PySpringOpenTelemetryExporter(EntityProvider, ApplicationContextRequired):
    _handler: ClassVar[Optional[RequestHookHandler]] = None

    def _get_tracer_properties(self) -> TracerExporterProperties:
        app_context = self.get_application_context()
        props = app_context.get_properties(TracerExporterProperties)
        assert props is not None
        return props

    
    def provider_init(self) -> None:
        app_context = self.get_application_context()
        tracer_properties = self._get_tracer_properties()
        otlp_exporter = OTLPSpanExporter(
            endpoint=tracer_properties.endpoint,
        )
        provider = TracerProvider(
            resource=Resource.create({"service.name": tracer_properties.service_name})
        )
        provider.add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )

        if self.__class__._handler is None:
            self.__class__._handler = provide_default_request_hook_handler()
        trace.set_tracer_provider(provider)
        app_context.server.add_middleware(ResponseTraceMiddleware)
        self.inject_instrumentation(app_context.server, self.__class__._handler)


    def inject_instrumentation(self, server: FastAPI, request_hook_handler: RequestHookHandler) -> None:
        FastAPIInstrumentor.instrument_app(
            server,
            server_request_hook=request_hook_handler.server_request_hook,
            client_request_hook=request_hook_handler.client_request_hook,
            client_response_hook=request_hook_handler.client_response_hook
        )

def provider_opentelemetry_exporter(handler: RequestHookHandler) -> PySpringOpenTelemetryExporter:
    exporter = PySpringOpenTelemetryExporter(
        properties_classes=[TracerExporterProperties],
    )
    exporter.__class__._handler = handler
    return exporter