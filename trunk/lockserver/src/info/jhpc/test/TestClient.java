package info.jhpc.test;

import java.net.Socket;
import java.io.DataOutputStream;

public class TestClient {
    public static void main(String[] args) throws Exception {
        Socket s = new Socket("localhost", 24680);
        DataOutputStream out = new DataOutputStream(s.getOutputStream());
        out.writeUTF("Hello");
    }
}
