import os
import requests
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

SERVICE = os.getenv("OTEL_SERVICE_NAME", "order-service")
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://simplest-collector:4318")
SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://service-b:8080")

# Setup tracing
resource = Resource.create({SERVICE_NAME: SERVICE})
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint=f"{OTLP_ENDPOINT}/v1/traces")
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

RequestsInstrumentor().instrument()

app = FastAPI(title="Order Service")
FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer(__name__)


@app.get("/")
def create_order():
    with tracer.start_as_current_span("create-order") as span:
        span.set_attribute("order.id", "order-123")
        span.set_attribute("order.type", "custom-jewelry")

        response = requests.get(f"{SERVICE_B_URL}/")
        calc = response.json()

        return {
            "service": SERVICE,
            "order_id": "order-123",
            "status": "PRICE_CALCULATED",
            "calculation": calc,
        }
