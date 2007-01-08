/*
 * Created on Mar 1, 2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
package edu.northwestern.ece.lockserverorig;

import java.util.*;
import java.net.InetAddress;
import java.net.Socket;
import java.io.*;

/**
 * @author aarestad
 * 
 * A class that tests the functionality of the lock server. This part will be
 * rewritten in C and interfaced with the ADIO code.
 */
public class FileLockClientTester extends Thread {

	private List lockList;

	private String fileName;

	public FileLockClientTester(List l, String name) {
		lockList = l;
		fileName = name;
	}

	public void run() {
		System.out.println("Acquiring locks");
		// XXX Testing purposes only, obviously
		try {
			Socket clientSock = new Socket(InetAddress.getLocalHost(), 46822);
			DataInputStream sockIn = new DataInputStream(clientSock
					.getInputStream());
			DataOutputStream sockOut = new DataOutputStream(clientSock
					.getOutputStream());

			sockOut.writeBoolean(true);
			sockOut.writeUTF(fileName);
			sockOut.writeInt(lockList.size());

			Iterator lockIter = lockList.iterator();
			while (lockIter.hasNext()) {
				FileLock fl = (FileLock) lockIter.next();
				sockOut.writeInt(fl.getOffset());
				sockOut.writeInt(fl.getLength());
			}
			boolean result = sockIn.readBoolean();
		} catch (IOException e) {
			e.printStackTrace();
			return;
		}
		System.out.println("Locks released");
	}
}