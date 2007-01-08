/*
 * Created on Mar 1, 2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
package edu.northwestern.ece.lockserverorig;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * @author aarestad
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Generation - Code and Comments
 */
public class FileLockClient {

	private static ServerSocket serverSock;
	
	private static final int FILE_LOCK_CLIENT_PORT = 46822;

	public static void main(String[] args) {
		try {
			System.out.println("Starting client-side server at port " + FILE_LOCK_CLIENT_PORT);
			serverSock = new ServerSocket(FILE_LOCK_CLIENT_PORT);

			while (true) {
				Socket clientSock = serverSock.accept();
				System.out.println("Accepting client from "
						+ clientSock.getRemoteSocketAddress());
				FileLockClientHandler flch = new FileLockClientHandler(
						clientSock);
				System.out.println("Starting new FileLockClientHandler thread");
				flch.start();
			}
		} catch (IOException e) {
			e.printStackTrace();
			System.exit(1);
		}
	}
}