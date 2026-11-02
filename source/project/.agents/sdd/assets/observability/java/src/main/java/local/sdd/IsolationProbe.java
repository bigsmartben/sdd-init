package local.sdd;

import java.nio.file.*;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/** A test adapter, not a durable loss ledger or a production capture library. */
public final class IsolationProbe {
  record Item(String id, byte[] bytes) {}
  static final class Worker {
    final ArrayBlockingQueue<Item> queue;
    final AtomicInteger rejected = new AtomicInteger(), failed = new AtomicInteger(), saved = new AtomicInteger();
    final Path dir; final CountDownLatch gate; final Thread thread;
    volatile boolean closing;
    Worker(Path dir, int capacity, CountDownLatch gate) {
      this.dir=dir; this.gate=gate; queue=new ArrayBlockingQueue<>(capacity);
      thread=new Thread(this::run,"observation-worker"); thread.setDaemon(true); thread.start();
    }
    // Input must already be an observation-owned immutable snapshot; never consume a business stream.
    boolean offer(Item item) { boolean ok=queue.offer(item); if(!ok) rejected.incrementAndGet(); return ok; }
    void run() {
      try {
        gate.await();
        while (!closing || !queue.isEmpty()) {
          Item i=queue.poll(100,TimeUnit.MILLISECONDS); if(i==null) continue;
          try {
            Files.createDirectories(dir);
            Path p=dir.resolve(i.id()+".bin");
            try (FileChannel f=FileChannel.open(p,StandardOpenOption.CREATE_NEW,StandardOpenOption.WRITE)) {
              ByteBuffer b=ByteBuffer.wrap(i.bytes()); while(b.hasRemaining()) f.write(b); f.force(true);
            }
            byte[] read=Files.readAllBytes(p);
            if(!Arrays.equals(i.bytes(),read)) throw new IllegalStateException("readback mismatch");
            saved.incrementAndGet();
          } catch (Exception e) { failed.incrementAndGet(); }
        }
      } catch(InterruptedException e) { Thread.currentThread().interrupt(); }
    }
    boolean close(long timeoutMs) throws InterruptedException {
      closing=true; thread.join(timeoutMs); return !thread.isAlive();
    }
  }
  static void require(boolean value,String message) { if(!value) throw new AssertionError(message); }
  public static void main(String[] args) throws Exception {
    Path root=Files.createTempDirectory("sdd-media-probe-");
    try {
      byte[] original=new byte[]{0,1,2,3,(byte)255,42};
      Worker good=new Worker(root.resolve("media"),2,new CountDownLatch(0));
      require(good.offer(new Item("raw",original)),"offer");
      require(good.close(5000),"flush timeout");
      byte[] read=Files.readAllBytes(root.resolve("media/raw.bin"));
      require(Arrays.equals(original,read),"media differs");
      String sha=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(read));
      require(good.saved.get()==1,"not saved");
      System.out.println("PASS raw media actual write/read sha256="+sha);
      CountDownLatch gate=new CountDownLatch(1); Worker slow=new Worker(root.resolve("slow"),1,gate);
      require(slow.offer(new Item("one",original)),"first offer");
      long start=System.nanoTime(); boolean accepted=slow.offer(new Item("two",original));
      long elapsed=TimeUnit.NANOSECONDS.toMillis(System.nanoTime()-start);
      require(!accepted && slow.rejected.get()==1 && elapsed<500,"saturation not exposed or blocked");
      require(Arrays.equals(original,new byte[]{0,1,2,3,(byte)255,42}),"business data changed");
      require(!slow.close(10),"blocked worker should exceed deadline"); gate.countDown(); require(slow.close(5000),"worker did not recover");
      System.out.println("PASS saturated worker: rejected=1, business input intact, offer_ms="+elapsed+", exit timeout visible");
      Path nonDirectory=root.resolve("not-directory"); Files.writeString(nonDirectory,"x");
      Worker broken=new Worker(nonDirectory,1,new CountDownLatch(0)); broken.offer(new Item("x",original));
      require(broken.close(5000) && broken.failed.get()==1,"storage failure not visible");
      System.out.println("PASS storage failure reported in process memory");
    } finally {
      try(var paths=Files.walk(root)) { paths.sorted(java.util.Comparator.reverseOrder()).forEach(p -> { try { Files.delete(p); } catch(Exception e) { throw new RuntimeException(e); } }); }
    }
  }
}
