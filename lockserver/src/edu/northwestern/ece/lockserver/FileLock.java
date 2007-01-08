package edu.northwestern.ece.lockserver;

import java.util.Date;

/**
 * Trivial class that represents a file lock
 */
public final class FileLock implements Comparable {
	private int lockID;

	private long offset;

	private long length;

	private long timeCreated;

	public FileLock(int id, long off, long len) {
		lockID = id;
		offset = off;
		length = len;
		timeCreated = new Date().getTime();
	}

	public FileLock(long off, long len) {
		this(-1, off, len);
	}

	public int compareTo(Object other) {
		FileLock l = this;
		FileLock r = (FileLock) other;
		long llb = l.offset;
		long lub = l.offset + l.length - 1;
		long rlb = r.offset;
		long rub = r.offset + r.length - 1;
		
		if (lub < rlb) {
            //System.out.println(l + " < " + r);
            return -1;
		}

		if (rub < llb) {
            //System.out.println(r + " < " + l);
            return 1;
		}

		//System.out.println(l + " == (overlaps) " + r);
		return 0;   
	}

	/**
	 * Overlapping locks will be considered to be "equal"
	 */
	public boolean equals(Object other) {
		if (this.compareTo(other) != 0) {
			return false;
		}
		return true;
	}

	public long getOffset() {
		return offset;
	}

	public long getLength() {
		return length;
	}

	public int getLockID() {
		return lockID;
	}

	public long getTimeCreated() {
		return timeCreated;
	}

	public String toString() {
		return "<lockID=" + lockID + "; offset=" + offset + "; length=" + length
				+ "; timeCreated=" + timeCreated + ">";
	}
}