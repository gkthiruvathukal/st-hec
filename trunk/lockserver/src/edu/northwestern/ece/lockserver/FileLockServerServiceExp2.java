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
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import info.jhpc.message2.Message;
import info.jhpc.message2.MessageListener;
import info.jhpc.message2.MessageServer;

/**
 * @author aarestad
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Generation - Code and Comments
 */
public final class FileLockServerServiceExp2 implements MessageListener {
	public static final int FILE_LOCK_SERVER_SERVICE_MESSAGE = 100;

	public static final int FILE_LOCK_SERVER_SERVICE_PORT = 35711;

	/**
	 * Lock information: key=filename, val=Set of locks on the file
	 */
	static Map fileLockDictByName;

	/**
	 * key=lock ID, val=Set of locks with that ID
	 */
	static Map fileLockDictByID;

	/**
	 * Next lock ID to be issued
	 */
	private static Integer lockID;

	public FileLockServerServiceExp2() {
		// fire off thread for lock removal?
	}

	/**
	 * @see info.jhpc.message2.MessageListener#accept(info.jhpc.message2.Message)
	 */
	public Message accept(Message m) {
		int myLockID = m.getIntegerParam("lockID");
		System.err.println("Client's lock ID: " + myLockID);
		if (myLockID == -1) {
			synchronized (lockID) {
				System.err.println("Assign lock ID " + lockID);
				myLockID = lockID.intValue();
				lockID = new Integer(myLockID + 1);
			}
		}

		String fileName = m.getStringParam("fileName");
		System.err.println("File name: " + fileName);

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
		List newLockList = new ArrayList();
		int fileLocksGranted = 0;

		int numLocks = m.getIntegerParam("numLocks");
		System.err.print("Number of locks to acquire: ");
		System.err.println(numLocks);

		for (int i = 0; i < numLocks; ++i) {
			long offset = m.getLongParam("offset" + i);
			long length = m.getLongParam("length" + i);
			FileLock fl = new FileLock(myLockID, offset, length);
			newLockList.add(fl);
			System.err.println("New lock: " + fl);
		}

		// Not needed since the locks are sorted by the ClientService
		//Collections.sort(newLockList);

		synchronized (fileLockDictByName) {
			boolean fileExists = fileLockDictByName.containsKey(fileName);
			if (!fileExists) {
				System.err.println("No locks present for file " + fileName);
				Set newLockSet = Collections.synchronizedSet(new HashSet());
				Iterator newLockIter = newLockList.iterator();
				while (newLockIter.hasNext()) {
					FileLock fl = (FileLock) newLockIter.next();
					newLockSet.add(fl);
				}
				fileLockDictByName.put(fileName, newLockSet);
				fileLocksGranted = newLockSet.size();
				boolean idExists = fileLockDictByID.containsKey(new Integer(
						myLockID));
				if (!idExists) {
					Set newLockSet2 = Collections
							.synchronizedSet(new HashSet());
					newLockSet2.addAll(newLockList);
					fileLockDictByID.put(new Integer(myLockID), newLockSet2);
				} else {
					Set exisitingLockSet = (Set) fileLockDictByID
							.get(new Integer(myLockID));
					synchronized (exisitingLockSet) {
						exisitingLockSet.addAll(newLockList);
					}
				}
			} else {
				System.err.println("File " + fileName + " exists");
				Set existingLockSetByName = (Set) fileLockDictByName
						.get(fileName);
				Iterator newLockIter = newLockList.iterator();
				while (newLockIter.hasNext()) {
					FileLock fl = (FileLock) newLockIter.next();
					System.err.println("Evaluating lock " + fl);
					synchronized (existingLockSetByName) {
						if (!existingLockSetByName.add(fl)) {
							// lock already present - break now
							System.err.println("Cannot grant lock " + fl);
							break;
						}
					}
					++fileLocksGranted;
					boolean idExists = fileLockDictByID
							.containsKey(new Integer(myLockID));
					Set lockSetByID;
					if (!idExists) {
						lockSetByID = Collections
								.synchronizedSet(new HashSet());
						lockSetByID.add(fl);
						fileLockDictByID
								.put(new Integer(myLockID), lockSetByID);
					} else {
						lockSetByID = (Set) fileLockDictByID.get(new Integer(
								myLockID));
						synchronized (lockSetByID) {
							lockSetByID.add(fl);
						}
					} //end else
				} // end while
			} // end else
		} // end synchronized

		Message reply = new Message();
		reply.setIntegerParam("lockID", myLockID);
		reply.setIntegerParam("fileLocksGranted", fileLocksGranted);

		long timeEnd = System.currentTimeMillis();
		long timeDiff = timeEnd - timeBegin;
		System.out.println("Time to satisfy lock request in ms: " + timeDiff);
		//System.err.println("Reply: " + reply);
		System.err.println("Current locks by filename:" + fileLockDictByName);
		System.err.println("Current locks by ID:" + fileLockDictByID);
		return reply;
	}

	private Message release(int myLockID, String fileName) {
		long timeBegin = System.currentTimeMillis();
		Message reply = new Message();

		if (fileLockDictByName.containsKey(fileName)
				&& fileLockDictByID.containsKey(new Integer(myLockID))) {
			Set currentFileLocks = (Set) fileLockDictByName.get(fileName);
			Set currentLocksByID = (Set) fileLockDictByID.get(new Integer(
					myLockID));
			Iterator lockIter = currentLocksByID.iterator();

			synchronized (currentFileLocks) {
				while (lockIter.hasNext()) {
					FileLock currLock = (FileLock) lockIter.next();
					currentFileLocks.remove(currLock);
				}
			}

			// Remove the hash entry if there are no more locks
			if (currentFileLocks.size() == 0) {
				//System.err.println("Removing lock table entry for
				// file "
				// + fileName);
				synchronized (fileLockDictByName) {
					fileLockDictByName.remove(fileName);
				}
			}
			synchronized (fileLockDictByID) {
				fileLockDictByID.remove(new Integer(myLockID));
			}
		} else {
			System.err.println("No locks being held on file " + fileName
					+ " or with ID " + myLockID);
		}

		reply.setBooleanParam("success", true);

		long timeEnd = System.currentTimeMillis();
		long timeDiff = timeEnd - timeBegin;
		System.out
				.println("Time to satisfy release request in ms: " + timeDiff);
		System.err.println("Current locks by filename:" + fileLockDictByName);
		System.err.println("Current locks by ID:" + fileLockDictByID);
		return reply;
	}

	public static void main(String[] args) {
		fileLockDictByName = Collections.synchronizedMap(new HashMap());
		fileLockDictByID = Collections.synchronizedMap(new HashMap());
		lockID = new Integer(0);

		FileLockServerServiceExp2 flss = new FileLockServerServiceExp2();
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
