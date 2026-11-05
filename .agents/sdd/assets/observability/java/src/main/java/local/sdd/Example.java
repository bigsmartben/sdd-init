package local.sdd;

import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.logs.Severity;
import io.opentelemetry.context.Scope;
import io.opentelemetry.exporter.otlp.http.logs.OtlpHttpLogRecordExporter;
import io.opentelemetry.exporter.otlp.http.trace.OtlpHttpSpanExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.logs.SdkLoggerProvider;
import io.opentelemetry.sdk.logs.export.BatchLogRecordProcessor;
import io.opentelemetry.sdk.resources.Resource;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
import java.time.Instant;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

public class Example {
  public static void main(String[] args) {
    String endpoint = System.getenv().getOrDefault("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:4318");
    String project = System.getenv().getOrDefault("SDD_PROJECT", "sdd-java-example");
    if (!project.matches("[a-zA-Z0-9_-]+")) throw new IllegalArgumentException("SDD_PROJECT must be alphanumeric, underscore or hyphen");
    Resource resource = Resource.getDefault().merge(Resource.create(Attributes.builder()
        .put("project", project).put("service.name", "sdd-java-example")
        .put("service.version", "1.0.0").put("deployment.environment", "dev").build()));
    var logs = SdkLoggerProvider.builder().setResource(resource).addLogRecordProcessor(
        BatchLogRecordProcessor.builder(OtlpHttpLogRecordExporter.builder().setEndpoint(endpoint + "/v1/logs").build()).build()).build();
    var traces = SdkTracerProvider.builder().setResource(resource).addSpanProcessor(
        BatchSpanProcessor.builder(OtlpHttpSpanExporter.builder().setEndpoint(endpoint + "/v1/traces").build()).build()).build();
    var sdk = OpenTelemetrySdk.builder().setLoggerProvider(logs).setTracerProvider(traces).build();
    var span = sdk.getTracer("sdd-example").spanBuilder("example").startSpan();
    String id = UUID.randomUUID().toString(); Instant now = Instant.now();
    String nanos = Long.toString(now.getEpochSecond() * 1_000_000_000L + now.getNano());
    try (Scope ignored = span.makeCurrent()) {
      // Fixed literal avoids treating arbitrary unescaped input as JSON. Real adapters must use a JSON encoder.
      String body = "{\"schema_version\":\"1.0.0\",\"event_id\":\""+id+"\",\"project\":\""+project+"\",\"service\":\"sdd-java-example\",\"program_version\":\"1.0.0\",\"instance_id\":null,\"event_time_unix_nano\":\""+nanos+"\",\"observed_time_unix_nano\":null,\"session_id\":null,\"request_id\":null,\"call_id\":null,\"trace_id\":\""+span.getSpanContext().getTraceId()+"\",\"span_id\":\""+span.getSpanContext().getSpanId()+"\",\"stage\":\"generated\",\"sequence\":0,\"event_type\":\"sample\",\"severity\":\"INFO\",\"result\":\"unknown\",\"error\":null,\"content\":{\"kind\":\"text\",\"text\":\"example\",\"media_uri\":null,\"media_sha256\":null},\"save_state\":\"unknown\",\"integrity\":\"unknown\"}";
      sdk.getLogsBridge().get("sdd-example").logRecordBuilder().setTimestamp(now).setSeverity(Severity.INFO).setBody(body).emit();
      System.out.println("event_id="+id+" trace_id="+span.getSpanContext().getTraceId()+"; local emission only, persistence unknown");
    } finally { span.end(); }
    var logResult=logs.forceFlush(); var traceResult=traces.forceFlush();
    long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);
    boolean logFlushed=logResult.join(5, TimeUnit.SECONDS).isSuccess();
    boolean traceFlushed=traceResult.join(Math.max(0, deadline-System.nanoTime()), TimeUnit.NANOSECONDS).isSuccess();
    System.out.println("flush logs="+logFlushed+" traces="+traceFlushed+"; readback still required");
    logs.shutdown(); traces.shutdown();
  }
}
