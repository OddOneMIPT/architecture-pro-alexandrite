import os
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

SERVICE = os.getenv("OTEL_SERVICE_NAME", "calculation-service")
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://simplest-collector:4318")

# Setup tracing
resource = Resource.create({SERVICE_NAME: SERVICE})
provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint=f"{OTLP_ENDPOINT}/v1/traces")
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

app = FastAPI(title="Calculation Service")
FastAPIInstrumentor.instrument_app(app)

tracer = trace.get_tracer(__name__)


@app.get("/")
def calculate_price():
    with tracer.start_as_current_span("calculate-price") as span:
        price = 15_000.00
        polygon_count = 12_500

        span.set_attribute("calculation.price", price)
        span.set_attribute("calculation.currency", "RUB")
        span.set_attribute("calculation.polygon_count", polygon_count)

        return {
            "service": SERVICE,
            "price": price,
            "currency": "RUB",
            "polygon_count": polygon_count,
            "calculation_time_sec": 2.5,
        }
