package edu.northwestern.ece.lockserverorig;

import java.net.ServerSocket;
import java.net.Socket;
import java.util.*;
import java.io.IOException;

public class FileLockServer {
	/**
	 * Lock information: key=filename, val=List of locks on the file
	 */
	public static Map fileLockDict;

	/**
	 * Next lock ID to be issued
	 */
	public static Integer lockID;

	/**
	 * The server's socket
	 */
	private static ServerSocket serverSock;
	
	/**
	 * The server port
	 */
	private static final int FILE_LOCK_SERVER_PORT = 35711;
	
	public static void main(String[] args) {
		try {
			System.out.println("Starting server at port " + FILE_LOCK_SERVER_PORT);
			serverSock = new ServerSocket(FILE_LOCK_SERVER_PORT);
			fileLockDict = new HashMap();
			lockID = new Integer(0);

			while (true) {
				Socket clientSock = serverSock.accept();
				System.out.println("Accepting client from "
						+ clientSock.getRemoteSocketAddress());
				FileLockServerHandler flsh = new FileLockServerHandler(
						clientSock);
				System.out.println("Starting new FileLockHandler thread");
				flsh.start();
			}
		} catch (IOException e) {
			e.printStackTrace();
			System.exit(1);
		}
	}
}