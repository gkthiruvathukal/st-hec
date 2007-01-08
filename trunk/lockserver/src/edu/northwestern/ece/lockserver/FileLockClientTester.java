/*
 * Created on Mar 7, 2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
package edu.northwestern.ece.lockserver;

import info.jhpc.message2.Message;
import info.jhpc.message2.MessageClient;

import java.io.IOException;

/**
 * @author aarestad
 *
 * TODO To change the template for this generated type comment go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
public class FileLockClientTester extends Thread {

	private long[] o1, l1, o2, l2;

	private String fileName;

	public FileLockClientTester(long[] o1, long[] l1, long[] o2, long[] l2, String name) {
		this.o1 = o1;
		this.l1 = l1;
		this.o2 = o2;
		this.l2 = l2;
		fileName = name;
	}
	
	public void run() {
		System.out.println("Trying to acquire locks: fileName=" + fileName);
		MessageClient client;
		try {
			client = new MessageClient("localhost",
					FileLockClientService.FILE_LOCK_CLIENT_SERVICE_PORT);
		} catch (IOException e) {
			e.printStackTrace();
			return;
		}

		Message m = new Message();
		m.setType(FileLockClientService.FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE);
		m.setStringParam("functionName", "acquire");
		m.setStringParam("fileName", fileName);
		m.setIntegerParam("numLocks", o1.length);
		m.createLongArrayParam("offsets", o1.length);
		m.createLongArrayParam("lengths", l1.length);

		for (int i = 0; i < o1.length; ++i) {
			m.setLongArrayParamValue("offsets", i, o1[i]);
			m.setLongArrayParamValue("lengths", i, l1[i]);
		}
		System.out.println("m: " + m);
		Message reply = client.call(m);
		System.out.println("Locks acquired; lock ID=" + reply.getIntegerParam("lockID"));
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e) {}
		
		Message m3 = new Message();
		m3.setType(FileLockClientService.FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE);
		m3.setStringParam("functionName", "acquiremore");
		m3.setStringParam("fileName", fileName);
		m3.setIntegerParam("numLocks", o2.length);
		m3.setIntegerParam("lockID", reply.getIntegerParam("lockID"));
		m3.createLongArrayParam("offsets", o2.length);
		m3.createLongArrayParam("lengths", l2.length);

		for (int i = 0; i < o2.length; ++i) {
			m3.setLongArrayParamValue("offsets", i, o2[i]);
			m3.setLongArrayParamValue("lengths", i, l2[i]);
		}

		System.out.println("m3: " + m3);
		Message reply3 = client.call(m3);
		System.out.println("Locks acquired; lock ID=" + reply.getIntegerParam("lockID"));
		try {
			Thread.sleep(5000);
		} catch (InterruptedException e) {}

		Message m2 = new Message();
		m2.setType(FileLockClientService.FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE);
		m2.setStringParam("functionName", "release");
		m2.setStringParam("fileName", fileName);
		m2.setIntegerParam("lockID", reply.getIntegerParam("lockID"));
		System.out.println("m2: "+ m2);
		Message reply2 = client.call(m2);

		client.disconnect();

		System.out.println("Locks released: fileName=" + fileName);
	}
}
