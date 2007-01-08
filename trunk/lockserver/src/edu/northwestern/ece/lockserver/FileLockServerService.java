/*
 * Created on Mar 7, 2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
package edu.northwestern.ece.lockserver;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Comparator;

import info.jhpc.message2.Message;
import info.jhpc.message2.MessageListener;
import info.jhpc.message2.MessageServer;

/**
 * @author aarestad
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Generation - Code and Comments
 */
public final class FileLockServerService implements MessageListener {
	public static final int FILE_LOCK_SERVER_SERVICE_MESSAGE = 100;

	public static final int FILE_LOCK_SERVER_SERVICE_PORT = 35711;

	/**
	 * Lock information: key=filename, val=List of locks on the file
	 */
	private static Map fileLockDict;

	/**
	 * Next lock ID to be issued
	 */
	private static Integer lockID;

	/**
	 * @see info.jhpc.message2.MessageListener#accept(info.jhpc.message2.Message)
	 */
	public Message accept(Message m) {
		int myLockID = m.getIntegerParam("lockID");
		//System.err.println("Client's lock ID: " + myLockID);
		if (myLockID == -1) {
			synchronized (lockID) {
				//System.err.println("Assign lock ID " + lockID);
				myLockID = lockID.intValue();
				lockID = new Integer(myLockID + 1);
			}
		}

		String fileName = m.getStringParam("fileName");
		//System.err.println("File name: " + fileName);

		String fileLockName = m.getStringParam("functionName");
		// TODO Do dynamic method dispatch here
		if (fileLockName.equalsIgnoreCase("acquire")) {
			return acquire(m, myLockID, fileName);
		} else if (fileLockName.equalsIgnoreCase("release")) {
			return release(myLockID, fileName);
		} else {
			throw new FileLockServerException("Invalid method name: "
					+ fileLockName);
		}
	}

	private Message acquire(Message m, int myLockID, String fileName) {
		long timeBegin = System.currentTimeMillis();
		List newLockList = Collections.synchronizedList(new ArrayList());
		int fileLocksGranted = 0;

		int numLocks = m.getIntegerParam("numLocks");
		//System.err.print("Number of locks to acquire: ");
		//System.err.println(numLocks);

		for (int i = 0; i < numLocks; ++i) {
			long offset = m.getLongParam("offset" + i);
			long length = m.getLongParam("length" + i);
			FileLock fl = new FileLock(myLockID, offset, length);
			newLockList.add(fl);
			//System.err.println("New lock: " + fl);
		}

		// Not needed since the locks are sorted by the ClientService
		//Collections.sort(newLockList);

		if (!fileLockDict.containsKey(fileName)) {
			// Just add the list of locks to the dictionary
			//System.err.println("File not found - granting all locks");
			synchronized (fileLockDict) {
				fileLockDict.put(fileName, newLockList);
			}
			fileLocksGranted = newLockList.size();
		} else {
			List currentFileLocks = (List) fileLockDict.get(fileName);
			FileLock firstNewLock = (FileLock) newLockList.get(0);
			FileLock lastNewLock = (FileLock) newLockList.get(newLockList
					.size() - 1);
			long newLockLB = firstNewLock.getOffset();
			long newLockUB = lastNewLock.getOffset()
					+ lastNewLock.getLength() - 1;

			synchronized (currentFileLocks) {
				FileLock firstCurrLock = (FileLock) currentFileLocks.get(0);
				FileLock lastCurrLock = (FileLock) currentFileLocks
						.get(currentFileLocks.size() - 1);
				long currLockLB = firstCurrLock.getOffset();
				long currLockUB = lastCurrLock.getOffset()
						+ lastCurrLock.getLength() - 1;
				if (currLockUB < newLockLB) {
					currentFileLocks.addAll(newLockList);
					fileLocksGranted = newLockList.size();
				} else if (newLockUB < currLockLB) {
					currentFileLocks.addAll(0, newLockList);
					fileLocksGranted = newLockList.size();
				} else {
					Iterator newLockIter = newLockList.iterator();
					Comparator lockComparator = new FileLockOverlapComparator();
					while (newLockIter.hasNext()) {
						FileLock newLock = (FileLock) newLockIter.next();
						int insertIdx = Collections.binarySearch(
								currentFileLocks, newLock, lockComparator);
						if (insertIdx < 0) {
							int idx = -(insertIdx + 1);
							fileLocksGranted++;
							currentFileLocks.add(idx, newLock);
						} else {
							break;
						}
					}
				}
			}
		} // end else of if (!fileLockDict.containsKey(fileName))

		Message reply = new Message();
		reply.setIntegerParam("lockID", myLockID);
		reply.setIntegerParam("fileLocksGranted", fileLocksGranted);

		long timeEnd = System.currentTimeMillis();
		long timeDiff = timeEnd - timeBegin;
		System.out.println("Time to satisfy lock request in ms: " + timeDiff);
		//System.err.println("Reply: " + reply);
		//System.err.println("Current locks:" + fileLockDict);
		return reply;
	}

	private Message release(int myLockID, String fileName) {
		long timeBegin = System.currentTimeMillis();
		Message reply = new Message();
		if (fileLockDict.containsKey(fileName)) {
			List currentFileLocks = (List) fileLockDict.get(fileName);
			synchronized (currentFileLocks) {
				Iterator lockIter = currentFileLocks.iterator();
				while (lockIter.hasNext()) {
					FileLock currLock = (FileLock) lockIter.next();
					if (myLockID == currLock.getLockID()) {
						lockIter.remove();
					}
				}
			}
			// Remove the hash entry if there are no more locks
			if (currentFileLocks.size() == 0) {
				//System.err.println("Removing lock table entry for file " +
				// fileName);
				synchronized (fileLockDict) {
					fileLockDict.remove(fileName);
				}
			}
			reply.setBooleanParam("success", true);
		} else {
			//System.err.println("No locks being held on file " + fileName);
			reply.setBooleanParam("success", false);
		}

		long timeEnd = System.currentTimeMillis();
		long timeDiff = timeEnd - timeBegin;
		System.out
				.println("Time to satisfy release request in ms: " + timeDiff);
		//System.err.println("Current locks:" + fileLockDict);
		return reply;
	}

	public static void main(String[] args) {
		fileLockDict = Collections.synchronizedMap(new HashMap());
		lockID = new Integer(0);

		FileLockServerService flss = new FileLockServerService();
		MessageServer ms;
		try {
			ms = new MessageServer(FILE_LOCK_SERVER_SERVICE_PORT);
		} catch (Exception e) {
			System.err.println("Could not start service " + e);
			return;
		}
		Thread msThread = new Thread(ms);
		ms.addMessageListener(FILE_LOCK_SERVER_SERVICE_MESSAGE, flss);
		msThread.start();
	}
}
