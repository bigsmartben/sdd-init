package local.sdd.androidexample;

import android.app.Activity;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.json.JSONArray;
import org.json.JSONObject;

/** Custom OTLP/JSON demo, not the OpenTelemetry Android SDK. Requires adb reverse. */
public final class MainActivity extends Activity {
  private static final Object N=JSONObject.NULL;
  private final java.util.concurrent.atomic.AtomicInteger rejected=new java.util.concurrent.atomic.AtomicInteger();
  private final java.util.concurrent.ThreadPoolExecutor worker=new java.util.concurrent.ThreadPoolExecutor(1,1,0,java.util.concurrent.TimeUnit.SECONDS,new java.util.concurrent.ArrayBlockingQueue<>(64),(r,e)->rejected.incrementAndGet());
  private static JSONObject kv(String key,String value) throws Exception { return new JSONObject().put("key",key).put("value",new JSONObject().put("stringValue",value)); }
  @Override public void onCreate(Bundle state) {
    super.onCreate(state); LinearLayout layout=new LinearLayout(this); layout.setOrientation(LinearLayout.VERTICAL);
    EditText input=new EditText(this); Button button=new Button(this); TextView output=new TextView(this); button.setText("Echo");
    layout.addView(input); layout.addView(button); layout.addView(output); setContentView(layout);
    button.setOnClickListener(v->{String raw=input.getText().toString(); output.setText("echo: "+raw); worker.execute(()->send(raw));});
  }
  @Override protected void onDestroy() { worker.shutdown(); super.onDestroy(); }
  private void send(String input) {
    try {
      String id=UUID.randomUUID().toString(); long time=System.currentTimeMillis()*1000000L;
      JSONObject content=new JSONObject().put("kind","text").put("text",input).put("media_uri",N).put("media_sha256",N);
      JSONObject e=new JSONObject().put("schema_version","1.0.0").put("event_id",id).put("project","sdd-android-example").put("service","android-example").put("program_version","1.0.0").put("instance_id",N)
       .put("event_time_unix_nano",Long.toString(time)).put("observed_time_unix_nano",N).put("session_id",N).put("request_id",UUID.randomUUID().toString()).put("call_id",N).put("trace_id",N).put("span_id",N)
       .put("stage","received").put("sequence",0).put("event_type","raw_interaction").put("severity","INFO").put("result","unknown").put("error",N).put("content",content).put("save_state","unknown").put("integrity","unknown");
      JSONObject record=new JSONObject().put("timeUnixNano",Long.toString(time)).put("severityNumber",9).put("body",new JSONObject().put("stringValue",e.toString()));
      JSONArray attrs=new JSONArray().put(kv("project","sdd-android-example")).put(kv("service.name","android-example")).put(kv("service.version","1.0.0")).put(kv("deployment.environment","dev"));
      JSONObject payload=new JSONObject().put("resourceLogs",new JSONArray().put(new JSONObject().put("resource",new JSONObject().put("attributes",attrs)).put("scopeLogs",new JSONArray().put(new JSONObject().put("logRecords",new JSONArray().put(record))))));
      HttpURLConnection c=(HttpURLConnection)new URL("http://127.0.0.1:14318/v1/logs").openConnection(); c.setConnectTimeout(2000); c.setReadTimeout(2000); c.setRequestMethod("POST"); c.setDoOutput(true); c.setRequestProperty("Content-Type","application/json");
      try {try(java.io.OutputStream os=c.getOutputStream()){os.write(payload.toString().getBytes(StandardCharsets.UTF_8));} android.util.Log.i("sdd-example","HTTP "+c.getResponseCode()+" event_id="+id+"; backend readback required");} finally {c.disconnect();}
    } catch(Exception e) {android.util.Log.e("sdd-example","observation unconfirmed",e);}
  }
}
