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

import net.datastructures.Dictionary;
import net.datastructures.Entry;
import net.datastructures.RBTree;

import info.jhpc.message2.Message;
import info.jhpc.message2.MessageListener;
import info.jhpc.message2.MessageServer;


/**
 * @author aarestad
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Generation - Code and Comments
 */
public final class FileLockServerServiceExp3 implements MessageListener {
	public static final int FILE_LOCK_SERVER_SERVICE_MESSAGE = 100;

	public static final int FILE_LOCK_SERVER_SERVICE_PORT = 35711;

    private static final int initBlockArrSize = 1024;

	/**
	 * Lock information: key=filename, val=Dictionary of locks on the file
	 */
	private static Map fileLockDictByName;
	
	/**
	 * key=lock ID, value=List of Entry objects corresponding to that ID's locks
	 */
	
	private static Map fileLockDictByID;

    /** Block list dictionary: key = filename, val = bitmap of blocks
     */
    private static Map fileBlockDictByName;

    /** key = id; value = array of blocks */
    private static Map fileBlockDictByID;

	/**
	 * Next lock ID to be issued
	 */
	private static Integer lockID;

	public static String mapToString(Map m) {
		Iterator keyIter = m.keySet().iterator();
		StringBuffer b = new StringBuffer();
		b.append("{");
		while (keyIter.hasNext()) {
			Object key = keyIter.next();
			b.append("[" + key + ",");
			Dictionary d = (Dictionary) m.get(key);
			Iterator i = d.entries();
			while (i.hasNext()) {
				Entry e = (Entry) i.next();
				Object k = e.key();
				Object v = e.value();
				b.append("(" + k + "," + v + ")");
			}
			b.append("]");
		}
		b.append("}");
		return b.toString();
	}

	/**
	 * @see info.jhpc.message2.MessageListener#accept(info.jhpc.message2.Message)
	 */
	public Message accept(Message m) {
		//System.out.println("got message: " + m);
		int myLockID = m.getIntegerParam("lockID");
		//System.err.println("Client's lock ID: " + myLockID);
		if (myLockID == -1) {
			synchronized (lockID) {
				myLockID = lockID.intValue();
				lockID = new Integer(myLockID + 1);
			}
		}

		String fileName = m.getStringParam("fileName");

		String fileLockName = m.getStringParam("functionName");
		// TODO Do dynamic method dispatch here
		if (fileLockName.equalsIgnoreCase("acquire")) {
			return acquire(m, myLockID, fileName);
        } else if (fileLockName.equalsIgnoreCase("acquireblocks")) {
			return acquireBlocks(m, myLockID, fileName);
		} else if (fileLockName.equalsIgnoreCase("release")) {
			return release(myLockID, fileName);
        } else if (fileLockName.equalsIgnoreCase("releaseblock")) {
            return releaseBlocks(myLockID, fileName);
		} else {
			throw new FileLockServerException("Invalid method name: "
					+ fileLockName);
		}
	}

    private Message acquireBlocks(Message m, int myLockID, String fileName) {
        int fileBlocksGranted = 0;
        boolean hasKey = false;
        int numBlocks = m.getIntegerParam("numBlocks");
        long[] blocks = m.getLongArrayParam("blocks");
        // Again assuming the locks are sorted by the ClientService
        // java.util.Arrays.sort(blocks);
        
        synchronized (fileBlockDictByName) {
            hasKey = fileBlockDictByName.containsKey(fileName);
            if (!hasKey) {
                byte[] newBlockArr = new byte[initBlockArrSize];
                for (int i = 0; i < blocks.length; ++i) {
                    int b = (int) blocks[i];
                    if (b >= newBlockArr.length * 8) {
                        // Resize array
                        int newLength = newBlockArr.length * 2;;
                        while (b < newLength * 8) {
                            newLength *= 2;
                        }
                        byte[] ba = new byte[newLength];
                        System.arraycopy(newBlockArr, 0, ba, 0,
                                         newBlockArr.length);
                        newBlockArr = ba;
                    }
                    newBlockArr[b/8] |= (1 << (b % 8));
                }
                fileBlockDictByName.put(fileName, newBlockArr);
                fileBlocksGranted = blocks.length;

                if (fileBlockDictByID.containsKey(new Integer(myLockID))) {
                    long[] blocksByID = (long[]) fileBlockDictByID.get(
                                                 new Integer (myLockID));
                    // Concatenate old block list with new list in a 
                    // new array
                    long[] newBlockList = new long[blocksByID.length +
                                                   blocks.length];
                    System.arraycopy(blocksByID, 0, newBlockList, 0,
                                     blocksByID.length);
                    System.arraycopy(blocks, 0, newBlockList, blocksByID.length,
                                     blocks.length);
                    synchronized(fileBlockDictByID) {
                        fileBlockDictByID.put(new Integer(myLockID),
                                              newBlockList);
                    }
                } else {
                    synchronized(fileBlockDictByID) {
                        fileBlockDictByID.put(new Integer(myLockID), blocks);
                    }
                }
            }
        }

        if (hasKey) {
            byte[] currentFileBlocks = (byte[]) fileBlockDictByName.get(fileName);
            synchronized (currentFileBlocks) {
                for (int i = 0; i < blocks.length; ++i) {
                    int b = (int) blocks[i];
                    if (b < (currentFileBlocks.length * 8)
                        && ((currentFileBlocks[b/8] & (1 << b % 8)) != 0)) {
                        // lock has already been granted - bail
                        break;
                    } else {
                        fileBlocksGranted++;
                        if (b >= currentFileBlocks.length * 8) {
                            // Resize array
                            int newLength = currentFileBlocks.length * 2;
                            while (b < newLength * 8) {
                                newLength *= 2;
                            }
                            byte[] ba = new byte[newLength];
                            System.arraycopy(currentFileBlocks, 0, ba, 0,
                                             currentFileBlocks.length);
                            currentFileBlocks = ba;
                        }
                        currentFileBlocks[b/8] |= (1 << (b % 8));
                    }
                }
                if (fileBlockDictByID.containsKey(new Integer(myLockID))) {
                    long[] blocksByID = (long[]) fileBlockDictByID.get(
                            new Integer (myLockID));
                    // Concatenate old block list with new list in a
                    // new array
                    long[] newBlockList = new long[blocksByID.length
                        + fileBlocksGranted];
                    System.arraycopy(blocksByID, 0, newBlockList, 0,
                            blocksByID.length);
                    System.arraycopy(blocks, 0, newBlockList,
                            blocksByID.length, fileBlocksGranted);
                    synchronized(fileBlockDictByID) {
                        fileBlockDictByID.put(new Integer(myLockID),
                                newBlockList);
                    }
                } else {
                    synchronized(fileBlockDictByID) {
                        fileBlockDictByID.put(new Integer(myLockID), blocks);
                    }
                }
            }
        }

        Message reply = new Message();
		//System.err.println("Reply: " + reply);
		//System.err.println("Current locks:" + fileBlockDictByName);
        reply.setIntegerParam("lockID", myLockID);
        reply.setIntegerParam("fileBlocksGranted", fileBlocksGranted);

        return reply;
    }

    private Message releaseBlocks(int myLockID, String fileName) {
        if (fileBlockDictByID.containsKey(new Integer(myLockID))) {
            long[] blocks;
            synchronized (fileBlockDictByID) {
                blocks = (long[]) fileBlockDictByID.remove(
                                    new Integer(myLockID));
            }
            if (fileBlockDictByName.containsKey(fileName)) {
                byte[] currentFileBlocks = (byte[]) fileBlockDictByName
                                                     .get(fileName);
                synchronized (currentFileBlocks) {
                    for (int i = 0; i < blocks.length; ++i) {
                        int b = (int) blocks[i];
                        currentFileBlocks[b/8] &= ~(1 << b % 8);
                    }
                }
            }
        }
        // Even if the lock ID or file name were bogus, report success
        Message reply = new Message();
        reply.setBooleanParam("success", true);
        return reply;
    }

	private Message acquire(Message m, int myLockID, String fileName) {
		long timeBegin = System.currentTimeMillis();
		Dictionary newLockDict = new RBTree();
		List newEntryList = Collections.synchronizedList(new ArrayList());
		int fileLocksGranted = 0;

		int numLocks = m.getIntegerParam("numLocks");
		long[] offsets = m.getLongArrayParam("offsets");
		long[] lengths = m.getLongArrayParam("lengths");

		for (int i = 0; i < numLocks; ++i) {
			FileLock fl = new FileLock(myLockID, offsets[i], lengths[i]);
			newEntryList.add(newLockDict.insert(fl, fl));
			//System.err.println("New lock: " + fl);
		}

		// Not needed since the locks are sorted by the ClientService
		//Collections.sort(newLockList);
		boolean hasKey;
		
		synchronized (fileLockDictByName) {
			hasKey = fileLockDictByName.containsKey(fileName);
			if (!hasKey) {
				fileLockDictByName.put(fileName, newLockDict);
				fileLocksGranted = newLockDict.size();
				
				if (fileLockDictByID.containsKey(new Integer(myLockID))) {
					List ids = (List) fileLockDictByID.get(new Integer(myLockID));
					synchronized (ids) {
						ids.addAll(newEntryList);
					}
				} else {
					fileLockDictByID.put(new Integer(myLockID), newEntryList);
				}
			}
		}

		if (hasKey) {
			Dictionary currentFileLocks = (Dictionary) fileLockDictByName.get(fileName);

			synchronized (currentFileLocks) {
				Iterator newLockIter = newLockDict.entries();
				while (newLockIter.hasNext()) {
					FileLock newLock = (FileLock) ((Entry) newLockIter.next()).key();
					Object val = currentFileLocks.find(newLock);
					if (val == null) {
						fileLocksGranted++;
						Entry e = currentFileLocks.insert(newLock, newLock);
						if (fileLockDictByID.containsKey(new Integer(myLockID))) {
							List l = (List) fileLockDictByID.get(new Integer(myLockID));
							synchronized (l) {
								l.add(e);
							}
						} else {
							List l = Collections.synchronizedList(new ArrayList());
							l.add(e);
							fileLockDictByID.put(new Integer(myLockID), l);
						}
					} else {
						break;
					}
				}
			}
		}

		Message reply = new Message();
		reply.setIntegerParam("lockID", myLockID);
		reply.setIntegerParam("fileLocksGranted", fileLocksGranted);

		long timeEnd = System.currentTimeMillis();
		long timeDiff = timeEnd - timeBegin;
		//System.out.println("Time to satisfy lock request in ms: " + timeDiff);
		//System.err.println("Reply: " + reply);
		//System.err.println("Current locks:" + mapToString(fileLockDictByName));
		return reply;
	}

	private Message release(int myLockID, String fileName) {
		long timeBegin = System.currentTimeMillis();
		Message reply = new Message();
		/*
		 * append myLockID to a Queue of release requests create reply message
		 * saying success
		 */
		synchronized(FileLockRemovalThread.requestQueue) {
			FileLockRemovalThread.requestQueue.add(new RemoveRequest(fileName,
					myLockID));
		}

		reply.setBooleanParam("success", true);

		long timeEnd = System.currentTimeMillis();
		long timeDiff = timeEnd - timeBegin;
		//System.out.println("Time to satisfy release request in ms: " + timeDiff);
		//System.err.println("Current locks:" + mapToString(fileLockDictByName));
		return reply;
	}

	public static void main(String[] args) {
		fileLockDictByName = Collections.synchronizedMap(new HashMap());
		fileLockDictByID   = Collections.synchronizedMap(new HashMap());

        fileBlockDictByName = Collections.synchronizedMap(new HashMap());
        fileBlockDictByID   = Collections.synchronizedMap(new HashMap());
		lockID             = new Integer(0);

		FileLockServerServiceExp3 flss = new FileLockServerServiceExp3();
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

		FileLockRemovalThread flrt = new FileLockRemovalThread();
		flrt.start();
	}

	private static class FileLockRemovalThread extends Thread {
		public static List requestQueue;

		public FileLockRemovalThread() {
			requestQueue = Collections.synchronizedList(new ArrayList());
		}

		public void run() {
			while (true) {
				RemoveRequest req = null;
				boolean isEmpty;
				synchronized(requestQueue) {
					isEmpty = requestQueue.isEmpty();
					if (!isEmpty) {
						//System.out.println(requestQueue.size() + " requests outstanding");
						req = (RemoveRequest) requestQueue.remove(0);
					}
				}
				if (isEmpty) {
					try {
						Thread.sleep(10);
					} catch (InterruptedException e) {}
					continue;
				}
				// else...
				String fileName = req.getFileName();
				int myLockID = req.getLockID();
				if (fileLockDictByName.containsKey(fileName) &&
					fileLockDictByID.containsKey(new Integer(myLockID))) {
					Dictionary currentFileDict = (Dictionary) fileLockDictByName
							.get(fileName);
					List lockEntries = (List) fileLockDictByID.get(new Integer(myLockID));

					Iterator entryIter = lockEntries.iterator();
					while (entryIter.hasNext()) {
						synchronized (currentFileDict) {
							currentFileDict.remove((Entry) entryIter.next());
						}
					}

					synchronized(fileLockDictByID) {
						fileLockDictByID.remove(new Integer(myLockID));
					}

		            //System.err.println("Current locks:" + currentFileDict);

					// Remove the hash entry if there are no more locks
					if (currentFileDict.size() == 0) {
						// System.err.println("Removing lock table entry for file "
						// + fileName);
						synchronized (fileLockDictByName) {
							fileLockDictByName.remove(fileName);
						}
					}
					//System.err.println("Current locks:" + mapToString(fileLockDictByName));
				}/* else {
					System.err.println("No locks being held on file " +
					fileName + " with ID " + myLockID);
				}*/
			}
		}
	}

	private class RemoveRequest {
		private String fileName;

		private int lockID;

		public RemoveRequest(String fn, int lid) {
			fileName = fn;
			lockID = lid;
		}

		public String getFileName() {
			return fileName;
		}

		public int getLockID() {
			return lockID;
		}
	}
}
