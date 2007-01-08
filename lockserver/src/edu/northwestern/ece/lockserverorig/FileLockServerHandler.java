package edu.northwestern.ece.lockserverorig;

import java.util.*;
import java.net.Socket;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

class FileLockServerHandler extends Thread {
	private Socket clientSock;

	private DataInputStream sockIn;

	private DataOutputStream sockOut;

	public FileLockServerHandler(Socket clientSock) throws IOException {
		this.clientSock = clientSock;
		sockIn = new DataInputStream(clientSock.getInputStream());
		sockOut = new DataOutputStream(clientSock.getOutputStream());
	}

	public void run() {
		List lockList = new ArrayList();
		Map fileLockDict = FileLockServer.fileLockDict;
		int numLocks = 0;
		boolean acquiring = true;
		String fileName = "";
		Integer lockID = FileLockServer.lockID;
		int fileLocksGranted = 0;
		int myLockID = 0;

		synchronized (fileLockDict) {
			synchronized (lockID) {
				try {
					acquiring = sockIn.readBoolean();
					System.out.print("Acquiring: ");
					System.out.println(acquiring);
					myLockID = sockIn.readInt();
					if (myLockID == -1) {
						myLockID = lockID.intValue();
						FileLockServer.lockID = new Integer(myLockID + 1);
					}
					fileName = sockIn.readUTF();
					System.out.println("File name: " + fileName);
					if (acquiring) {
						numLocks = sockIn.readInt();
						System.out.print("Number of locks: ");
						System.out.println(numLocks);

						while (numLocks > 0) {
							int offset = sockIn.readInt();
							int length = sockIn.readInt();
							FileLock fl = new FileLock(myLockID, offset, length);
							lockList.add(fl);
							System.out.println("New lock: " + fl);
							--numLocks;
						}
					}
				} catch (IOException e) {
					e.printStackTrace();
					return;
				}
				Collections.sort(lockList);

				if (acquiring) {
					if (!fileLockDict.containsKey(fileName)) {
						// Just add the list of locks to the dictionary
						System.out
								.println("File not found - granting all locks");
						fileLockDict.put(fileName, lockList);
						fileLocksGranted = lockList.size();
					} else {
						List currentFileLocks = (List) fileLockDict
								.get(fileName);
						Iterator newLockIter = lockList.iterator();
						newlockeval: while (newLockIter.hasNext()) {
							FileLock newLock = (FileLock) newLockIter.next();
							System.out.println("Evaluating lock " + newLock);
							int newLockFirst = newLock.getOffset();
							int newLockLast = newLock.getOffset()
									+ newLock.getLength() - 1;
							Iterator currLockIter = currentFileLocks.iterator();
							currlockeval: while (currLockIter.hasNext()) {
								FileLock currLock = (FileLock) currLockIter
										.next();
								int currLockFirst = currLock.getOffset();
								int currLockLast = currLock.getOffset()
										+ currLock.getLength() - 1;
								if (currLockLast < newLockFirst) {
									// This lock is too early in the file - keep
									// going
									continue currlockeval;
								}
								if (currLockFirst > newLockLast) {
									// We got past the area where the new lock
									// is without finding a conflict
									System.out.println("Granting lock "
											+ newLock);
									fileLocksGranted++;
									currentFileLocks.add(newLock);
									break currlockeval;
								}

								if ((currLockFirst >= newLockFirst && currLockFirst <= newLockLast)
										|| (currLockFirst <= newLockFirst && currLockLast >= newLockFirst)) {
									// This lock is ungrantable - quit now
									System.out.println("Cannot grant lock "
											+ newLock);
									break newlockeval;
								}
							} // end while (currLockIter.hasNext())
							// If we get here, we ran out of locks, so we
							// know it's OK to grant the new lock
							System.out.println("Granting lock " + newLock);
							fileLocksGranted++;
							currentFileLocks.add(newLock);
						} // end while (newLockIter.hasNext())

						Collections.sort(currentFileLocks);
					} // end else of if (!fileLockDict.containsKey(fileName))
				} else { // acquiring == false; thus, releasing
					if (fileLockDict.containsKey(fileName)) {
						List toDelete = new ArrayList();
						List currentFileLocks = (List) fileLockDict
								.get(fileName);
						Iterator currentLockIter = currentFileLocks.iterator();
						while (currentLockIter.hasNext()) {
							FileLock currLock = (FileLock) currentLockIter
									.next();
							if (myLockID == currLock.getLockID()) {
								System.out.println("Marking for removal: "
										+ currLock);
								toDelete.add(currLock);
							}
						}
						Iterator toDeleteIter = toDelete.iterator();
						while (toDeleteIter.hasNext()) {
							System.out.println("Removing lock:"
									+ toDeleteIter.next());
							currentFileLocks.remove(toDeleteIter.next());
						}

						// Remove the hash entry if there are no more locks
						if (currentFileLocks.size() == 0) {
							System.out
									.println("Removing lock table entry for file "
											+ fileName);
							fileLockDict.remove(fileName);
						}
					}
				} // end else of if (acquiring)
			} // end synchronized(lockID)
		} // end synchronized(fileLockDict)

		// Send a message back to the client - either the number of
		// locks granted, or a success flag
		try {
			if (acquiring) {
				sockOut.writeInt(myLockID);
				sockOut.writeInt(fileLocksGranted);
			} else {
				sockOut.writeBoolean(true);
			}
			clientSock.close();
		} catch (IOException e) {
			e.printStackTrace();
		}

		System.out.println("Current locks:");
		if (fileLockDict.isEmpty()) {
			System.out.println("(none)");
		} else {
			Set keys = fileLockDict.keySet();
			Iterator keyIter = keys.iterator();
			while (keyIter.hasNext()) {
				String key = (String) keyIter.next();
				List fll = (List) fileLockDict.get(key);
				System.out.println("File:" + key);
				Iterator flliter = fll.iterator();
				while (flliter.hasNext()) {
					FileLock fl = (FileLock) flliter.next();
					System.out.println(fl);
				}
			}
		}
	}
}