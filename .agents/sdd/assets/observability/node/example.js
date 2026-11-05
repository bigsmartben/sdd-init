'use strict';
const { randomUUID } = require('node:crypto');
const { Resource } = require('@opentelemetry/resources');
const { LoggerProvider, BatchLogRecordProcessor } = require('@opentelemetry/sdk-logs');
const { OTLPLogExporter } = require('@opentelemetry/exporter-logs-otlp-http');
const { SeverityNumber } = require('@opentelemetry/api-logs');

async function main() {
  const project = process.env.SDD_PROJECT || 'sdd-node-example';
  const endpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://127.0.0.1:4318';
  const provider = new LoggerProvider({resource: new Resource({'project': project, 'service.name': 'node-example', 'service.version': '1.0.0', 'deployment.environment': 'dev'})});
  provider.addLogRecordProcessor(new BatchLogRecordProcessor(new OTLPLogExporter({url: endpoint + '/v1/logs'})));
  const input = process.argv[2] || '原始文本';
  const output = 'echo: ' + input;
  const id = randomUUID(), request = randomUUID();
  const now = BigInt(Date.now()) * 1000000n;
  const event = {schema_version:'1.0.0',event_id:id,project,service:'node-example',program_version:'1.0.0',instance_id:null,
    event_time_unix_nano:now.toString(),observed_time_unix_nano:null,session_id:null,request_id:request,call_id:null,trace_id:null,span_id:null,
    stage:'received',sequence:0,event_type:'raw_interaction',severity:'INFO',result:'unknown',error:null,
    content:{kind:'text',text:input,media_uri:null,media_sha256:null},save_state:'unknown',integrity:'unknown'};
  provider.getLogger('sdd-example').emit({severityNumber:SeverityNumber.INFO,body:JSON.stringify(event),timestamp:Number(now / 1000000n)});
  const outputEvent={...event,event_id:randomUUID(),event_time_unix_nano:(BigInt(Date.now())*1000000n).toString(),stage:'generated',sequence:1,content:{...event.content,text:output}};
  provider.getLogger('sdd-example').emit({severityNumber:SeverityNumber.INFO,body:JSON.stringify(outputEvent)});
  process.stdout.write(JSON.stringify({output,event_id:id,request_id:request})+'\n');
  let timer; try { await Promise.race([provider.forceFlush(), new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('flush timeout')),5000);})]); }
  catch(e) { process.stderr.write('export unconfirmed: '+e.message+'\n'); }
  finally { clearTimeout(timer); }
  await provider.shutdown();
}
main().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1;});
