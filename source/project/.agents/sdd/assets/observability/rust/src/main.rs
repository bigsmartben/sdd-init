use opentelemetry::{KeyValue, logs::{Logger, LoggerProvider as _, LogRecord as _, Severity}};
use opentelemetry_sdk::{logs::LoggerProvider, Resource};
use serde_json::json;
use std::time::{SystemTime, UNIX_EPOCH};
use uuid::Uuid;

#[tokio::main(flavor="multi_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let project=std::env::var("SDD_PROJECT").unwrap_or_else(|_|"sdd-rust-example".into());
    let input=std::env::args().nth(1).unwrap_or_else(||"原始文本".into());
    let exporter=opentelemetry_otlp::LogExporter::builder().with_http().build()?;
    let res=Resource::new(vec![KeyValue::new("project",project.clone()),KeyValue::new("service.name","rust-example"),KeyValue::new("service.version","1.0.0"),KeyValue::new("deployment.environment","dev")]);
    let provider=LoggerProvider::builder().with_resource(res).with_batch_exporter(exporter,opentelemetry_sdk::runtime::Tokio).build();
    let logger=provider.logger("sdd-example"); let mut record=logger.create_log_record();
    let id=Uuid::new_v4().to_string(); let request=Uuid::new_v4().to_string();
    let now=SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos().to_string();
    let mut event=json!({"schema_version":"1.0.0","event_id":id,"project":project,"service":"rust-example","program_version":"1.0.0","instance_id":null,"event_time_unix_nano":now,"observed_time_unix_nano":null,"session_id":null,"request_id":request,"call_id":null,"trace_id":null,"span_id":null,"stage":"received","sequence":0,"event_type":"raw_interaction","severity":"INFO","result":"unknown","error":null,"content":{"kind":"text","text":input,"media_uri":null,"media_sha256":null},"save_state":"unknown","integrity":"unknown"});
    record.set_severity_number(Severity::Info); record.set_body(event.to_string().into()); logger.emit(record);
    event["event_id"]=json!(Uuid::new_v4().to_string()); event["stage"]=json!("generated"); event["sequence"]=json!(1); event["event_time_unix_nano"]=json!(SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos().to_string()); event["content"]["text"]=json!(format!("echo: {}",input));
    let mut generated=logger.create_log_record(); generated.set_severity_number(Severity::Info); generated.set_body(event.to_string().into()); logger.emit(generated);
    println!("output=echo: {} event_id={}",input,id);
    if let Err(e)=provider.shutdown() { eprintln!("export unconfirmed: {e}"); }
    Ok(())
}
