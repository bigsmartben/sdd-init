package local.sdd;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.logs.Logger;
import io.opentelemetry.api.logs.Severity;
import io.opentelemetry.exporter.otlp.http.logs.OtlpHttpLogRecordExporter;
import io.opentelemetry.sdk.logs.SdkLoggerProvider;
import io.opentelemetry.sdk.logs.export.BatchLogRecordProcessor;
import io.opentelemetry.sdk.resources.Resource;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;

/** Demonstration only: no assertion of crash-proof loss accounting. */
public final class BusinessDemo {
  static final ObjectMapper JSON=new ObjectMapper();
  record Fact(String id,String request,String stage,long seq,String text,byte[] media,Instant eventTime) {
    Fact(String id,String request,String stage,long seq,String text,byte[] media) { this(id,request,stage,seq,text,media,Instant.now()); }
  }
  static final class Observer implements AutoCloseable {
    record Missing(String event_id,String request_id,String stage,long sequence,String reason,String time) {}
    final ArrayBlockingQueue<Fact> queue; final ArrayBlockingQueue<Missing> missing; final Path root, ledgerRoot; final Thread worker, ledgerWorker;
    final AtomicLong unrecorded=new AtomicLong();
    volatile boolean closing, ledgerClosing, ledgerFailed; final Logger logger; final CountDownLatch gate;
    Observer(Path root,int capacity,Logger logger) { this(root,root,capacity,logger,new CountDownLatch(0)); }
    Observer(Path root,int capacity,Logger logger,CountDownLatch gate) { this(root,root,capacity,logger,gate); }
    Observer(Path root,Path ledgerRoot,int capacity,Logger logger,CountDownLatch gate) {
      this.root=root; this.ledgerRoot=ledgerRoot; this.logger=logger; this.gate=gate; queue=new ArrayBlockingQueue<>(capacity); missing=new ArrayBlockingQueue<>(capacity);
      ledgerWorker=new Thread(this::runLedger,"observation-ledger"); ledgerWorker.setDaemon(true); ledgerWorker.start();
      worker=new Thread(this::run,"observation-worker"); worker.setDaemon(true); worker.start();
    }
    // The caller supplies an observation-owned, immutable snapshot and never passes a live stream.
    void observe(Fact f) { if(closing) {unrecorded.incrementAndGet(); return;} if(!queue.offer(f)) markMissing(f,"queue_full"); }
    void markMissing(Fact f,String reason) {
      if(!missing.offer(new Missing(f.id(),f.request(),f.stage(),f.seq(),reason,Instant.now().toString()))) unrecorded.incrementAndGet();
    }
    void append(Path path,byte[] bytes) throws Exception {
      try(FileChannel c=FileChannel.open(path,StandardOpenOption.CREATE,StandardOpenOption.WRITE,StandardOpenOption.APPEND)) {
        ByteBuffer b=ByteBuffer.wrap(bytes); while(b.hasRemaining()) c.write(b); c.force(true);
      }
    }
    void persist(Fact f) throws Exception {
      Files.createDirectories(root); String uri=null, sha=null;
      if(f.media()!=null) {
        Path path=root.resolve(f.id()+".media");
        try(FileChannel c=FileChannel.open(path,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)) {
          ByteBuffer b=ByteBuffer.wrap(f.media()); while(b.hasRemaining()) c.write(b); c.force(true);
        }
        byte[] actual=Files.readAllBytes(path);
        if(!Arrays.equals(actual,f.media())) throw new IllegalStateException("media readback mismatch");
        sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual)); uri=path.toUri().toString();
      }
      Instant t=f.eventTime(); Map<String,Object> event=new LinkedHashMap<>();
      event.put("schema_version","1.0.0"); event.put("event_id",f.id()); event.put("project","sdd-java-demo"); event.put("service","business-demo");
      event.put("program_version","1.0.0"); event.put("instance_id",null); event.put("event_time_unix_nano",Long.toString(t.getEpochSecond()*1000000000L+t.getNano()));
      event.put("observed_time_unix_nano",null); event.put("session_id",null); event.put("request_id",f.request()); event.put("call_id",null);
      event.put("trace_id",null); event.put("span_id",null); event.put("stage",f.stage()); event.put("sequence",f.seq()); event.put("event_type","raw_interaction");
      event.put("severity","INFO"); event.put("result","unknown"); event.put("error",null);
      Map<String,Object> content=new LinkedHashMap<>(); content.put("kind",f.media()==null?"text":"media"); content.put("text",f.text()); content.put("media_uri",uri); content.put("media_sha256",sha);
      event.put("content",content); event.put("save_state","unknown"); event.put("integrity","unknown");
      String encoded=JSON.writeValueAsString(event); append(root.resolve("events.jsonl"),(encoded+"\n").getBytes(StandardCharsets.UTF_8));
      if(logger!=null) logger.logRecordBuilder().setSeverity(Severity.INFO).setBody(encoded).emit();
    }
    void runLedger() {
      Missing pending=null;
      while(!ledgerClosing || pending!=null || !missing.isEmpty()) {
        try {
          if(pending==null) pending=missing.poll(100,TimeUnit.MILLISECONDS);
          if(pending==null) continue;
          Files.createDirectories(ledgerRoot);
          append(ledgerRoot.resolve("missing.jsonl"),(JSON.writeValueAsString(pending)+"\n").getBytes(StandardCharsets.UTF_8));
          pending=null;
        } catch(InterruptedException e) {Thread.currentThread().interrupt(); return;}
        catch(Exception e) {ledgerFailed=true; try {Thread.sleep(100);} catch(InterruptedException interrupted) {Thread.currentThread().interrupt(); return;}}
      }
    }
    void run() {
      try { gate.await(); } catch(InterruptedException e) {Thread.currentThread().interrupt(); return;}
      while(!closing || !queue.isEmpty()) {
        try { Fact f=queue.poll(100,TimeUnit.MILLISECONDS); if(f!=null) try {persist(f);} catch(Exception e) {markMissing(f,"local_write_failed");} }
        catch(InterruptedException e) {Thread.currentThread().interrupt(); break;}
      }
    }
    boolean finish(long timeoutMs) throws InterruptedException {
      long end=System.nanoTime()+TimeUnit.MILLISECONDS.toNanos(timeoutMs); closing=true;
      if(timeoutMs>0) worker.join(timeoutMs);
      if(!worker.isAlive()) ledgerClosing=true;
      long left=TimeUnit.NANOSECONDS.toMillis(Math.max(0,end-System.nanoTime())); if(left>0) ledgerWorker.join(left);
      return !worker.isAlive()&&!ledgerWorker.isAlive()&&!ledgerFailed&&unrecorded.get()==0;
    }
    public void close() throws InterruptedException {finish(5000);}
  }
  static String business(String input) { return "echo: "+input; }
  public static void main(String[] args) throws Exception {
    if(args.length<1 || args.length>2) throw new IllegalArgumentException("usage: BusinessDemo <existing-test-directory> [input]");
    Path root=Path.of(args[0]); if(!Files.isDirectory(root)) throw new IllegalArgumentException("directory must exist");
    String endpoint=System.getenv().getOrDefault("OTEL_EXPORTER_OTLP_ENDPOINT","http://127.0.0.1:4318");
    var provider=SdkLoggerProvider.builder().setResource(Resource.getDefault().merge(Resource.create(Attributes.builder().put("project","sdd-java-demo").put("service.name","business-demo").put("deployment.environment","dev").build())))
      .addLogRecordProcessor(BatchLogRecordProcessor.builder(OtlpHttpLogRecordExporter.builder().setEndpoint(endpoint+"/v1/logs").build()).build()).build();
    Observer obs=new Observer(root,16,provider.get("business-demo"));
    String request=UUID.randomUUID().toString(), input=args.length==2?args[1]:"你好, streaming world", output=business(input);
    obs.observe(new Fact(UUID.randomUUID().toString(),request,"received",0,input,null));
    byte[] media=new byte[]{0,1,2,(byte)255}; obs.observe(new Fact(UUID.randomUUID().toString(),request,"received",1,null,media));
    int split=output.offsetByCodePoints(0,Math.min(6,output.codePointCount(0,output.length())));
    obs.observe(new Fact(UUID.randomUUID().toString(),request,"generated",2,output.substring(0,split),null));
    obs.observe(new Fact(UUID.randomUUID().toString(),request,"generated",3,output.substring(split),null));
    System.out.println(output); long deadline=System.nanoTime()+TimeUnit.SECONDS.toNanos(5);
    boolean done=obs.finish(5000); long remaining=Math.max(0,deadline-System.nanoTime());
    boolean flushed=provider.forceFlush().join(remaining,TimeUnit.NANOSECONDS).isSuccess(); provider.shutdown();
    System.out.println("request="+request+" worker_complete="+done+" exporter_flushed="+flushed+" (backend readback required)");
  }
}
