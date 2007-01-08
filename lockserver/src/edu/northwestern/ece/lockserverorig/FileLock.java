package edu.northwestern.ece.lockserverorig;

import java.util.Date;

/**
 * Trivial class that represents a file lock
 */
public class FileLock implements Comparable {
	private int lockID;

	private int offset;

	private int length;

	private long timeCreated;

	public FileLock(int id, int off, int len) {
		lockID = id;
		offset = off;
		length = len;
		timeCreated = new Date().getTime();
	}

	public FileLock(int off, int len) {
		this(-1, off, len);
	}

	public int compareTo(Object other) {
		return offset - ((FileLock) other).offset;
	}

	public boolean equals(Object other) {
		return offset == ((FileLock) other).offset;
	}

	public int getOffset() {
		return offset;
	}

	public int getLength() {
		return length;
	}

	public int getLockID() {
		return lockID;
	}

	public long getTimeCreated() {
		return timeCreated;
	}

	public String toString() {
		return "lockID=" + lockID + "; offset=" + offset + "; length=" + length
				+ "; timeCreated=" + timeCreated;
	}
}