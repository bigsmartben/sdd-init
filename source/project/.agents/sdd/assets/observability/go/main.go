package main

import (
 "context"
 "crypto/rand"
 "encoding/hex"
 "encoding/json"
 "fmt"
 "os"
 "time"
 "go.opentelemetry.io/otel/attribute"
 "go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploghttp"
 "go.opentelemetry.io/otel/log"
 sdklog "go.opentelemetry.io/otel/sdk/log"
 "go.opentelemetry.io/otel/sdk/resource"
)
func uuid() string { b:=make([]byte,16); if _,e:=rand.Read(b); e!=nil {panic(e)}; b[6]=(b[6]&15)|64;b[8]=(b[8]&63)|128; s:=hex.EncodeToString(b); return s[:8]+"-"+s[8:12]+"-"+s[12:16]+"-"+s[16:20]+"-"+s[20:] }
func main() {
 ctx:=context.Background(); exporter,err:=otlploghttp.New(ctx); if err!=nil {panic(err)}
 project:=os.Getenv("SDD_PROJECT"); if project=="" {project="sdd-go-example"}
 res:=resource.NewSchemaless(attribute.String("project",project),attribute.String("service.name","go-example"),attribute.String("service.version","1.0.0"),attribute.String("deployment.environment","dev"))
 provider:=sdklog.NewLoggerProvider(sdklog.WithResource(res),sdklog.WithProcessor(sdklog.NewBatchProcessor(exporter)))
 input:="原始文本"; if len(os.Args)>1 {input=os.Args[1]}; id:=uuid(); request:=uuid(); now:=time.Now()
 event:=map[string]any{"schema_version":"1.0.0","event_id":id,"project":project,"service":"go-example","program_version":"1.0.0","instance_id":nil,"event_time_unix_nano":fmt.Sprint(now.UnixNano()),"observed_time_unix_nano":nil,"session_id":nil,"request_id":request,"call_id":nil,"trace_id":nil,"span_id":nil,"stage":"received","sequence":0,"event_type":"raw_interaction","severity":"INFO","result":"unknown","error":nil,"content":map[string]any{"kind":"text","text":input,"media_uri":nil,"media_sha256":nil},"save_state":"unknown","integrity":"unknown"}
 body,err:=json.Marshal(event); if err!=nil {panic(err)}; var record log.Record; record.SetTimestamp(now); record.SetSeverity(log.SeverityInfo); record.SetBody(log.StringValue(string(body))); provider.Logger("sdd-example").Emit(ctx,record)
 event["event_id"]=uuid(); event["stage"]="generated"; event["sequence"]=1; event["event_time_unix_nano"]=fmt.Sprint(time.Now().UnixNano()); event["content"].(map[string]any)["text"]="echo: "+input
 body,err=json.Marshal(event); if err!=nil {panic(err)}; var generated log.Record; generated.SetTimestamp(time.Now()); generated.SetSeverity(log.SeverityInfo); generated.SetBody(log.StringValue(string(body))); provider.Logger("sdd-example").Emit(ctx,generated)
 fmt.Printf("output=%s event_id=%s\n", "echo: "+input,id)
 stop,cancel:=context.WithTimeout(ctx,5*time.Second); defer cancel(); if e:=provider.Shutdown(stop);e!=nil {fmt.Fprintln(os.Stderr,"export unconfirmed:",e)}
}
