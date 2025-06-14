import os
import base64
import dotenv

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from opentelemetry import trace

import openlit

dotenv.load_dotenv()

LANGFUSE_PUBLIC_KEY=os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY=os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST=os.getenv("LANGFUSE_HOST")
LANGFUSE_AUTH=base64.b64encode(f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()).decode()

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{LANGFUSE_HOST}/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"
 
trace_provider = TracerProvider()
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))

trace.set_tracer_provider(trace_provider)
 
# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)

openlit.init(tracer=tracer, disable_batch=True)

def callback_factory(span_name: str, tags: list[str] = []):
    def callback(data):
        with tracer.start_span(span_name) as span:
            span.set_attribute("langfuse.user.id", "user-123")
            span.set_attribute("langfuse.session.id", "123456789")
            if tags and len(tags) > 0:
                span.set_attribute("langfuse.tags", tags)
            span.set_attribute("client_id", "123456789")
            # check if data is a dictionary
            if isinstance(data, dict):
                span.set_attribute("output.value", json.dumps(data))
            else:
                span.set_attribute("output.value", str(data))
    return callback