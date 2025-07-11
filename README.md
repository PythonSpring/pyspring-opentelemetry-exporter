# pyspring-opentelemetry-exporter

A seamless OpenTelemetry integration for PySpring applications that provides automatic instrumentation and distributed tracing capabilities.

## Overview

`pyspring-opentelemetry-exporter` is a Python package that integrates OpenTelemetry tracing with PySpring applications. It automatically instruments FastAPI applications to capture request/response traces and sends them to OpenTelemetry-compatible backends via OTLP HTTP exporter.

## Features

- 🔍 **Automatic Instrumentation**: Automatically instruments FastAPI applications for distributed tracing
- 📊 **OTLP Export**: Sends traces to any OpenTelemetry-compatible backend via OTLP HTTP
- 🎯 **Custom Hooks**: Extensible request/response hook system for custom trace attributes
- ⚡ **Easy Integration**: Simple setup with PySpring's dependency injection system
- 🏷️ **Rich Metadata**: Captures user agent, request paths, response status codes, and more

## Installation

### Prerequisites

- Python 3.10 or higher (up to 3.12)
- PySpring Core 0.0.16 or higher

### Install via PDM

```bash
# Install PDM if you haven't already
pip install pdm

# Install the package
pdm add pyspring-opentelemetry-exporter
```

### Install from Source

```bash
git clone https://github.com/your-username/pyspring-opentelemetry-exporter.git
cd pyspring-opentelemetry-exporter
pdm install
```

## Quick Start

### 1. Basic Setup

Add the OpenTelemetry exporter to your PySpring application:

```python
from py_spring_core import PySpringApplication
from pyspring_opentelemetry_exporter import provider_opentelemetry_exporter, provide_default_request_hook_handler

def main():
    app = PySpringApplication(
        "./app-config.json", 
        entity_providers=[
            provider_opentelemetry_exporter(
                provide_default_request_hook_handler()
            )
        ]
    )
    app.run()

if __name__ == "__main__":
    main():
```

### 2. Configuration

Create an `application-properties.json` file with your OpenTelemetry configuration:

```json
{
    "tracer_exporter": {
        "service_name": "my-service",
        "endpoint": "https://your-otlp-endpoint.com/v1/traces"
    }
}
```

### 3. Create a Controller

```python
from py_spring_core import GetMapping, RestController

class HelloController(RestController):
    
    @GetMapping("/hello")
    def get(self) -> str:
        return "Hello, OpenTelemetry!"
```

## Configuration

### Tracer Exporter Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `service_name` | string | Yes | Name of your service for trace identification |
| `endpoint` | string | Yes | OTLP HTTP endpoint URL (e.g., `https://otlp.devcloudhub.org/v1/traces`) |

### Example Configuration

```json
{
    "tracer_exporter": {
        "service_name": "user-service",
        "endpoint": "https://otlp.devcloudhub.org/v1/traces"
    }
}
```

## Custom Request Hooks

You can customize what information is captured in traces by implementing your own `RequestHookHandler`:

```python
from pyspring_opentelemetry_exporter import RequestHookHandler
from opentelemetry.trace.span import Span
from typing import Any

class CustomRequestHookHandler(RequestHookHandler):
    def server_request_hook(self, span: Span, scope: dict[str, Any]) -> None:
        if span and span.is_recording():
            # Add custom server request attributes
            span.set_attribute("custom.server.attribute", "value")
    
    def client_request_hook(self, span: Span, scope: dict[str, Any], request: dict[str, Any]) -> None:
        if span and span.is_recording():
            # Add custom client request attributes
            span.set_attribute("custom.client.attribute", "value")
    
    def client_response_hook(self, span: Span, scope: dict[str, Any], response: dict[str, Any]) -> None:
        if span and span.is_recording():
            # Add custom client response attributes
            span.set_attribute("custom.response.attribute", "value")

# Use your custom handler
app = PySpringApplication(
    "./app-config.json", 
    entity_providers=[
        provider_opentelemetry_exporter(CustomRequestHookHandler())
    ]
)
```

## Default Behavior

The default `RequestHookHandler` automatically captures:

- **Server Request**: User agent, request path
- **Client Request**: Request URL
- **Client Response**: Response status code

## Supported OpenTelemetry Backends

This exporter works with any OpenTelemetry-compatible backend that supports OTLP HTTP, including:

- [Jaeger](https://www.jaegertracing.io/)
- [Zipkin](https://zipkin.io/) (via OTLP adapter)
- [Tempo](https://grafana.com/oss/tempo/)
- [New Relic](https://newrelic.com/)
- [Datadog](https://www.datadoghq.com/)
- [Honeycomb](https://www.honeycomb.io/)
- [Grafana Cloud](https://grafana.com/products/cloud/)

## Example with Jaeger

1. **Start Jaeger** (using Docker):

```bash
docker run -d --name jaeger \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 16686:16686 \
  -p 4318:4318 \
  jaegertracing/all-in-one:latest
```

2. **Configure your application**:

```json
{
    "tracer_exporter": {
        "service_name": "my-app",
        "endpoint": "http://localhost:4318/v1/traces"
    }
}
```

3. **View traces** at `http://localhost:16686`

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/pyspring-opentelemetry-exporter.git
cd pyspring-opentelemetry-exporter

# Install dependencies
pdm install

# Install development dependencies
pdm install --group dev
```

### Running Tests

```bash
pdm run pytest
```

### Building

```bash
pdm build
```

## Dependencies

- `py-spring-core>=0.0.16` - PySpring framework core
- `opentelemetry-instrumentation-fastapi>=0.55b1` - FastAPI instrumentation
- `opentelemetry-sdk>=1.34.1` - OpenTelemetry SDK
- `opentelemetry-exporter-otlp-proto-http>=1.34.1` - OTLP HTTP exporter

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please:

1. Check the [Issues](https://github.com/your-username/pyspring-opentelemetry-exporter/issues) page
2. Create a new issue with detailed information about your problem
3. Include your Python version, PySpring version, and configuration

## Changelog

### v0.1.0
- Initial release
- Basic OpenTelemetry integration with PySpring
- Default request hook handler
- OTLP HTTP exporter support
