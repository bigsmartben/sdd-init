package local.sdd;

import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CountDownLatch;

public final class BusinessDemoTest {
  static void ok(boolean b,String m) { if(!b) throw new AssertionError(m); }
  public static void main(String[] args) throws Exception {
    Path root=Files.createTempDirectory("sdd-business-test-");
    try {
      CountDownLatch gate=new CountDownLatch(1); var obs=new BusinessDemo.Observer(root,1,null,gate);
      String input="原始输入"; byte[] media=new byte[]{0,1,(byte)255};
      obs.observe(new BusinessDemo.Fact(UUID.randomUUID().toString(),"req","received",0,input,null));
      String rejectedId=UUID.randomUUID().toString(); obs.observe(new BusinessDemo.Fact(rejectedId,"req","received",1,null,media));
      ok(BusinessDemo.business(input).equals("echo: "+input),"business output changed");
      ok(!obs.finish(10),"slow observation must not report completed"); gate.countDown(); ok(obs.finish(5000),"not drained");
      String ledger=Files.readString(root.resolve("missing.jsonl")); ok(ledger.contains(rejectedId)&&ledger.contains("queue_full"),"missing event not durable");
      var line=Files.readAllLines(root.resolve("events.jsonl")).get(0); var json=BusinessDemo.JSON.readTree(line);
      ok(json.path("content").path("text").asText().equals(input),"raw text mismatch");
      String id=UUID.randomUUID().toString(); Files.createDirectory(root.resolve(id+".media"));
      var failing=new BusinessDemo.Observer(root,2,null); failing.observe(new BusinessDemo.Fact(id,"req","received",2,null,media));
      ok(failing.finish(5000),"failed worker hung"); ok(Files.readString(root.resolve("missing.jsonl")).contains(id),"failure identity not recorded");
      String goodId=UUID.randomUUID().toString(); var good=new BusinessDemo.Observer(root,2,null);
      good.observe(new BusinessDemo.Fact(goodId,"req","received",3,null,media)); ok(good.finish(5000),"media worker hung");
      ok(Arrays.equals(media,Files.readAllBytes(root.resolve(goodId+".media"))),"raw media mismatch");
      Path blocked=root.resolve("blocked"); Files.writeString(blocked,"file");
      var unavailable=new BusinessDemo.Observer(blocked,2,null); unavailable.observe(new BusinessDemo.Fact(UUID.randomUUID().toString(),"req","received",4,input,null));
      ok(!unavailable.finish(400),"unwritable ledger must be unresolved");
      unavailable.ledgerWorker.interrupt(); unavailable.ledgerWorker.join(1000);
      Path independent=root.resolve("independent-ledger");
      var separate=new BusinessDemo.Observer(blocked,independent,2,null,new CountDownLatch(0)); String failedId=UUID.randomUUID().toString();
      separate.observe(new BusinessDemo.Fact(failedId,"req","received",5,input,null));
      ok(separate.finish(5000),"independent ledger worker did not drain");
      ok(Files.readString(independent.resolve("missing.jsonl")).contains(failedId),"independent ledger did not record failure");
      System.out.println("PASS business unchanged, delayed worker, persisted missing counts, write failure, raw text and media readback");
    } finally {try(var paths=Files.walk(root)) {paths.sorted(Comparator.reverseOrder()).forEach(p->{try{Files.delete(p);}catch(Exception e){throw new RuntimeException(e);}});}}
  }
}
