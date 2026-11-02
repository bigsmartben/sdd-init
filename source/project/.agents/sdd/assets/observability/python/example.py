import json, logging, os, sys, time, uuid
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

def main():
    project=os.environ.get('SDD_PROJECT','sdd-python-example')
    endpoint=os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT','http://127.0.0.1:4318')
    provider=LoggerProvider(resource=Resource.create({'project':project,'service.name':'python-example','service.version':'1.0.0','deployment.environment':'dev'}))
    provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint+'/v1/logs')))
    log=logging.getLogger('sdd-example'); log.setLevel(logging.INFO); log.addHandler(LoggingHandler(level=logging.INFO,logger_provider=provider)); log.propagate=False
    source=sys.argv[1] if len(sys.argv)>1 else '原始文本'
    event={'schema_version':'1.0.0','event_id':str(uuid.uuid4()),'project':project,'service':'python-example','program_version':'1.0.0','instance_id':None,
           'event_time_unix_nano':str(time.time_ns()),'observed_time_unix_nano':None,'session_id':None,'request_id':str(uuid.uuid4()),'call_id':None,'trace_id':None,'span_id':None,
           'stage':'received','sequence':0,'event_type':'raw_interaction','severity':'INFO','result':'unknown','error':None,
           'content':{'kind':'text','text':source,'media_uri':None,'media_sha256':None},'save_state':'unknown','integrity':'unknown'}
    log.info(json.dumps(event,ensure_ascii=False,separators=(',',':')))
    output='echo: '+source
    generated={**event,'event_id':str(uuid.uuid4()),'event_time_unix_nano':str(time.time_ns()),'stage':'generated','sequence':1,'content':{**event['content'],'text':output}}
    log.info(json.dumps(generated,ensure_ascii=False,separators=(',',':')))
    print(json.dumps({'output':output,'event_id':event['event_id']},ensure_ascii=False),flush=True)
    print('flush confirmed:',provider.force_flush(timeout_millis=5000),'; backend readback required',flush=True)
    provider.shutdown()

if __name__=='__main__': main()
