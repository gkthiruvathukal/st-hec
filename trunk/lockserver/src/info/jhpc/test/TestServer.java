package info.jhpc.test;

import java.net.ServerSocket;
import java.net.Socket;
import java.io.DataInputStream;

public class TestServer {
    public static void main(String[] args) throws Exception {
        ServerSocket ss = new ServerSocket(24680);
        Socket s = ss.accept();
        DataInputStream in = new DataInputStream(s.getInputStream());
        String st = in.readUTF();
        System.out.println("received: <" + st + ">");
        //int i = in.readInt();
        //System.out.println("received: " + i);
    }
}

