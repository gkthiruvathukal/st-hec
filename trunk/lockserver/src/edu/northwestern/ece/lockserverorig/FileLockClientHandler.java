package edu.northwestern.ece.lockserverorig;

import java.net.Socket;
import java.net.InetAddress;
import java.io.*;
import java.util.*;

public class FileLockClientHandler extends Thread {

	private Socket clientSock;

	private DataInputStream clientSockIn;

	private DataOutputStream clientSockOut;

	public FileLockClientHandler(Socket sock) throws IOException {
		clientSock = sock;
		clientSockIn = new DataInputStream(clientSock.getInputStream());
		clientSockOut = new DataOutputStream(clientSock.getOutputStream());
	}

	public void run() {
		try {
			boolean isClient = clientSockIn.readBoolean();
			if (isClient) {
				String fileName = clientSockIn.readUTF();
				int numLocks = clientSockIn.readInt();
				List lockList = new ArrayList();

				while (numLocks > 0) {
					int offset = clientSockIn.readInt();
					int length = clientSockIn.readInt();
					lockList.add(new FileLock(offset, length));
					--numLocks;
				}
				Collections.sort(lockList);
				List result = getLocks(fileName, lockList);
				int lockID = ((Integer) result.get(0)).intValue();
				int locksAcquired = ((Integer) result.get(1)).intValue();
				try {
					Thread.sleep(1000);
				} catch (InterruptedException e) {
				}
				while (locksAcquired != lockList.size()) {
					List lockSublist = lockList.subList(locksAcquired, lockList
							.size());
					// locksAcquired += getLocks(fileName, lockSublist);
					result = getLocks(fileName, lockSublist, lockID);
					locksAcquired += ((Integer) result.get(1)).intValue();
					try {
						Thread.sleep(1000);
					} catch (InterruptedException e) {
					}
				}
				releaseLocks(fileName, lockID);
				clientSockOut.writeBoolean(true);
			} else {
				// TODO handle timeouts here
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}

	/**
	 * Called the first time we want to get locks
	 * 
	 * @param fileName
	 *            name of file to lock
	 * @param locks
	 *            List of FileLock elements
	 * @return 2-element list: lock ID and number of locks granted
	 */
	private static List getLocks(String fileName, List locks) {
		return getLocks(fileName, locks, -1);
	}

	/**
	 * Attempt to acquire the passed-in locks on the specified file
	 * 
	 * @param fileName
	 *            name of file to lock
	 * @param locks
	 *            List of FileLock elements
	 * @param lockID
	 *            the ID for these locks (acquired from previous call to
	 *            getLocks()
	 * @return 2-element list: lock ID and number of locks granted
	 */
	private static List getLocks(String fileName, List locks, int lockID) {
		List retVals = new ArrayList();
		try {
			// XXX Testing purposes only
			Socket serverSock = new Socket(InetAddress.getLocalHost(), 35711);
			DataInputStream serverSockIn = new DataInputStream(serverSock
					.getInputStream());
			DataOutputStream serverSockOut = new DataOutputStream(serverSock
					.getOutputStream());

			serverSockOut.writeBoolean(true);
			serverSockOut.writeInt(lockID);
			serverSockOut.writeUTF(fileName);
			serverSockOut.writeInt(locks.size());

			Iterator lockIter = locks.iterator();
			while (lockIter.hasNext()) {
				FileLock fl = (FileLock) lockIter.next();
				serverSockOut.writeInt(fl.getOffset());
				serverSockOut.writeInt(fl.getLength());
			}

			lockID = serverSockIn.readInt();
			int locksAcquired = serverSockIn.readInt();
			retVals.add(new Integer(lockID));
			retVals.add(new Integer(locksAcquired));

			System.out.println("Acquired " + locksAcquired + " locks");
			System.out.println("Lock ID: " + lockID);

			for (int i = 0; i < locksAcquired; ++i) {
				FileLock fl = (FileLock) locks.get(i);
				System.out.println("Got lock: " + fl);
			}
			serverSock.close();
		} catch (IOException e) {
			e.printStackTrace();
			return null;
		}
		return retVals;
	}

	private static void releaseLocks(String fileName, int lockID) {
		try {
			Socket serverSock = new Socket(InetAddress.getLocalHost(), 35711);
			DataInputStream serverSockIn = new DataInputStream(serverSock
					.getInputStream());
			DataOutputStream serverSockOut = new DataOutputStream(serverSock
					.getOutputStream());
			serverSockOut.writeBoolean(false);
			serverSockOut.writeInt(lockID);
			serverSockOut.writeUTF(fileName);
			boolean success = serverSockIn.readBoolean();
			// success will always be true - if there's an error, it'll
			// be an exception
			System.out.println("Released locks");
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}