/*
 * Created on Mar 7, 2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
package edu.northwestern.ece.lockserver;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;

import info.jhpc.message2.Message;
import info.jhpc.message2.MessageClient;
import info.jhpc.message2.MessageListener;
import info.jhpc.message2.MessageServer;

/**
 * @author aarestad
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Generation - Code and Comments
 */
public final class FileLockClientService implements MessageListener {
	public static final int FILE_LOCK_CLIENT_SERVICE_SERVER_MESSAGE = 200;
	public static final int FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE = 201;
	public static final int FILE_LOCK_CLIENT_SERVICE_PORT = 46822;
	public static String FILE_LOCK_SERVER_SERVICE_NAME = null;

	/**
	 * @see info.jhpc.message2.MessageListener#accept(info.jhpc.message2.Message)
	 */
	public Message accept(Message m) {
		//System.out.println("got message:" + m);
		int msgType = m.getType();
		if (msgType == FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE) {
			String action = m.getStringParam("functionName");
			if (action.equalsIgnoreCase("acquire")) {
				try {
					Message reply = acquireLocks(m);
					return reply;
				} catch (IOException e) {
					e.printStackTrace();
					return null;
				}
			} else if (action.equalsIgnoreCase("acquiremore")) {
				try {
					Message reply = acquireMoreLocks(m);
					return reply;
				} catch (IOException e) {
					e.printStackTrace();
					return null;
				}
			} else if (action.equalsIgnoreCase("release")
                       || action.equalsIgnoreCase("releaseblock")) {
				try {
					Message reply = releaseLocks(m);
					//System.out.println("Released locks");
					return reply;
				} catch (IOException e) {
					e.printStackTrace();
					return null;
				}
            } else if (action.equalsIgnoreCase("acquireblock")) {
                try {
                    Message reply = acquireBlockLocks(m);
                    return reply;
                } catch (IOException e) {
                    e.printStackTrace();
                    return null;
                }
			} else if (action.equalsIgnoreCase("acquiremoreblock")) {
				try {
					Message reply = acquireMoreBlockLocks(m);
					return reply;
				} catch (IOException e) {
					e.printStackTrace();
					return null;
				}
			} else {
				throw new FileLockServerException("Unknown action: " + action);
			}
		} else if (msgType == FILE_LOCK_CLIENT_SERVICE_SERVER_MESSAGE) {
			return processTimeouts(m);
		} else {
			throw new FileLockServerException("Unknown message type: "
					+ msgType);
		}
	}

	// TODO Placeholder - fill out later
	protected Message processTimeouts(Message m) {
		return null;
	}
	
	/**
	 * Same as acquireLocks(), but provides a previously-acquired lock ID
	 * up front
	 * @param m the incoming message
	 * @return Message from the server
	 * @throws IOException
	 */
	protected Message acquireMoreLocks(Message m) throws IOException {
		String fileName = m.getStringParam("fileName");
		int numLocks = m.getIntegerParam("numLocks");
		int lockID = m.getIntegerParam("lockID");
		List lockList = new ArrayList();
		long[] offsets = m.getLongArrayParam("offsets");
		long[] lengths = m.getLongArrayParam("lengths");

		for (int i = 0; i < numLocks; ++i) {
			lockList.add(new FileLock(offsets[i], lengths[i]));
		}

		Collections.sort(lockList);
		Message result = getLocks(fileName, lockList, lockID);
		//System.out.println("Reply from lock server: " + result);
		int locksAcquired = result.getIntegerParam("fileLocksGranted");
		//System.out.println("locks acquired: " + locksAcquired + "; numlocks: " + lockList.size());
		
		int timeToSleep = 1;
		while (locksAcquired != lockList.size()) {
			try {
				Thread.sleep(timeToSleep);
			} catch (InterruptedException e) {}

            // Limit backoff time to 1024 ms
            if (timeToSleep < 1024) {
                timeToSleep *= 2;
            }

			List lockSublist = lockList.subList(locksAcquired, lockList.size());
			result = getLocks(fileName, lockSublist, lockID);
			//System.out.println("Reply from lock server: " + result);
			locksAcquired += result.getIntegerParam("fileLocksGranted");
			//System.out.println("locks acquired: " + locksAcquired + "; numlocks: " + lockList.size());
		}
		result.setIntegerParam("fileLocksGranted", locksAcquired);
		return result;
	}

	/**
	 * Right now this is all-or-nothing acquisition - method attempts to reaqcuire
	 * any locks it can't get the first time until all locks are gotten
	 * @param m message containing filename/lock info
	 * @return message with lock ID for given locks
	 * @throws IOException
	 */
	protected Message acquireLocks(Message m) throws IOException {
		String fileName = m.getStringParam("fileName");
		int numLocks = m.getIntegerParam("numLocks");
		List lockList = new ArrayList();
		long[] offsets = m.getLongArrayParam("offsets");
		long[] lengths = m.getLongArrayParam("lengths");

		for (int i = 0; i < numLocks; ++i) {
			lockList.add(new FileLock(offsets[i], lengths[i]));
		}

		Collections.sort(lockList);
		Message result = getLocks(fileName, lockList);
		//System.out.println("Reply from lock server: " + result);
		int lockID = result.getIntegerParam("lockID");
		int locksAcquired = result.getIntegerParam("fileLocksGranted");
		//System.out.println("locks acquired: " + locksAcquired + "; numlocks: " + lockList.size());
	
        int timeToSleep = 1;
		while (locksAcquired != lockList.size()) {
			try {
				Thread.sleep(timeToSleep);
			} catch (InterruptedException e) {}

            // Limit backoff time to 1024 ms
            if (timeToSleep < 1024) {
                timeToSleep *= 2;
            }

			List lockSublist = lockList.subList(locksAcquired, lockList.size());
			result = getLocks(fileName, lockSublist, lockID);
			//System.out.println("Reply from lock server: " + result);
			locksAcquired += result.getIntegerParam("fileLocksGranted");
			//System.out.println("locks acquired: " + locksAcquired + "; numlocks: " + lockList.size());
		}
		result.setIntegerParam("fileLocksGranted", locksAcquired);
		return result;
	}

	/**
	 * Called the first time we want to get locks (-1 signals to the server
	 * that we need a new lock ID assigned to us)
	 * 
	 * @param fileName
	 *            name of file to lock
	 * @param locks
	 *            List of FileLock elements
	 * @return 2-element list: lock ID and number of locks granted
	 * @throws IOException
	 */
	private static Message getLocks(String fileName, List locks)
			throws IOException {
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
	private static Message getLocks(String fileName, List locks, int lockID)
			throws IOException {
		MessageClient client = new MessageClient(FILE_LOCK_SERVER_SERVICE_NAME,
				FileLockServerService.FILE_LOCK_SERVER_SERVICE_PORT);

		Message m = new Message();
		m.setType(FileLockServerService.FILE_LOCK_SERVER_SERVICE_MESSAGE);
		m.setStringParam("functionName", "acquire");
		m.setIntegerParam("lockID", lockID);
		m.setStringParam("fileName", fileName);
		m.setIntegerParam("numLocks", locks.size());
		m.createLongArrayParam("offsets", locks.size());
		m.createLongArrayParam("lengths", locks.size());

		Iterator lockIter = locks.iterator();
		for (int i = 0; lockIter.hasNext(); ++i) {
			FileLock fl = (FileLock) lockIter.next();
			m.setLongArrayParamValue("offsets", i, fl.getOffset());
			m.setLongArrayParamValue("lengths", i, fl.getLength());
		}

		//System.out.println("sending message: " + m);
		Message reply = client.call(m);		
		client.disconnect();
		return reply;
	}

	protected Message releaseLocks(Message m)
			throws IOException {
		MessageClient client = new MessageClient(FILE_LOCK_SERVER_SERVICE_NAME,
				FileLockServerService.FILE_LOCK_SERVER_SERVICE_PORT);
		m.setType(FileLockServerService.FILE_LOCK_SERVER_SERVICE_MESSAGE);
		Message reply = client.call(m);
		client.disconnect();
		return reply;
	}

    protected Message acquireBlockLocks(Message m) throws IOException {
		String fileName = m.getStringParam("fileName");
		int numLocks = m.getIntegerParam("numLocks");
        List blockList = new ArrayList();
		long[] startBlocks = m.getLongArrayParam("startblocks");
		long[] lengths     = m.getLongArrayParam("lengths");
        int totalBlocks = 0;

        for (int i = 0; i < numLocks; ++i) {
            for (int j = 0; j < lengths[i]; ++j) {
                blockList.add(new Long(startBlocks[i] + j));
                totalBlocks++;
            }
        }

		Collections.sort(blockList);
		Message result = getBlockLocks(fileName, blockList);
		//System.out.println("Reply from lock server: " + result);
		int lockID = result.getIntegerParam("lockID");
		int locksAcquired = result.getIntegerParam("fileBlocksGranted");
		//System.out.println("locks acquired: " + locksAcquired + "; numlocks: " + blockList.size());
	
        int timeToSleep = 1;
		while (locksAcquired < totalBlocks) {
			try {
				Thread.sleep(timeToSleep);
			} catch (InterruptedException e) {}

            // Limit backoff time to 1024 ms
            if (timeToSleep < 1024) {
                timeToSleep *= 2;
            }

			List blockSublist = blockList.subList(locksAcquired,
                                                  blockList.size());
			result = getBlockLocks(fileName, blockSublist, lockID);
			//System.out.println("Reply from lock server: " + result);
			locksAcquired += result.getIntegerParam("fileBlocksGranted");
			//System.out.println("locks acquired: " + locksAcquired + "; numlocks: " + blockList.size());
		}
		result.setIntegerParam("fileLocksGranted", locksAcquired);
		return result;
    }

    protected Message acquireMoreBlockLocks(Message m) throws IOException {
		String fileName = m.getStringParam("fileName");
		int numLocks = m.getIntegerParam("numLocks");
		int lockID = m.getIntegerParam("lockID");
		List blockList = new ArrayList();
		long[] startBlocks = m.getLongArrayParam("startblocks");
		long[] lengths     = m.getLongArrayParam("lengths");
        int totalBlocks = 0;

		for (int i = 0; i < numLocks; ++i) {
            for (int j = 0; j < lengths[i]; ++j) {
                blockList.add(new Long(startBlocks[i] + j));
                totalBlocks++;
            }
		}

		Collections.sort(blockList);
		Message result = getBlockLocks(fileName, blockList, lockID);
		//System.out.println("Reply from lock server: " + result);
		int locksAcquired = result.getIntegerParam("fileBlocksGranted");
		//System.out.println("locks acquired: " + locksAcquired + "; numlocks: " + blockList.size());
		
		int timeToSleep = 1;
		while (locksAcquired < totalBlocks) {
			try {
				Thread.sleep(timeToSleep);
			} catch (InterruptedException e) {}

            // Limit backoff time to 1024 ms
            if (timeToSleep < 1024) {
                timeToSleep *= 2;
            }

			List blockSublist = blockList.subList(locksAcquired,
                                                  blockList.size());
			result = getBlockLocks(fileName, blockSublist, lockID);
			//System.out.println("Reply from lock server: " + result);
			locksAcquired += result.getIntegerParam("fileBlocksGranted");
			//System.out.println("locks acquired: " + locksAcquired + "; numlocks: " + blockList.size());
		}
		result.setIntegerParam("fileLocksGranted", locksAcquired);
		return result;
    }

	private static Message getBlockLocks(String fileName, List blocks)
			throws IOException {
		return getBlockLocks(fileName, blocks, -1);
	}

	private static Message getBlockLocks(String fileName, List blocks,
            int lockID) throws IOException {
		MessageClient client = new MessageClient(FILE_LOCK_SERVER_SERVICE_NAME,
				FileLockServerService.FILE_LOCK_SERVER_SERVICE_PORT);

		Message m = new Message();
		m.setType(FileLockServerService.FILE_LOCK_SERVER_SERVICE_MESSAGE);
		m.setStringParam("functionName", "acquireblocks");
		m.setIntegerParam("lockID", lockID);
		m.setStringParam("fileName", fileName);
		m.setIntegerParam("numBlocks", blocks.size());
		m.createLongArrayParam("blocks", blocks.size());

		Iterator blockIter = blocks.iterator();
		for (int i = 0; blockIter.hasNext(); ++i) {
			Long b = (Long) blockIter.next();
			m.setLongArrayParamValue("blocks", i, b.longValue());
		}

		//System.out.println("sending message: " + m);
		Message reply = client.call(m);		
		client.disconnect();
		return reply;
	}

	public static void main(String[] args) {
		FILE_LOCK_SERVER_SERVICE_NAME = args[0];
		FileLockClientService flcs = new FileLockClientService();
		MessageServer ms;
		try {
			ms = new MessageServer(FILE_LOCK_CLIENT_SERVICE_PORT);
		} catch (Exception e) {
			System.err.println("Could not start service " + e);
			return;
		}
		Thread msThread = new Thread(ms);
		ms.addMessageListener(FILE_LOCK_CLIENT_SERVICE_SERVER_MESSAGE, flcs);
		ms.addMessageListener(FILE_LOCK_CLIENT_SERVICE_CLIENT_MESSAGE, flcs);
		msThread.start();
	}
}
