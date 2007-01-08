/*
 * Created on Sep 14, 2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
package edu.northwestern.ece.lockserver.util;

import jdsl.core.api.Comparator;
import edu.northwestern.ece.lockserver.FileLock;

public final class FileLockOverlapComparator implements Comparator {

	public int compare(Object a, Object b) throws ClassCastException {
		return ((FileLock) a).compareTo(b);
	}

	public boolean isGreaterThan(Object a, Object b) throws ClassCastException {
		return ((FileLock) a).compareTo(b) > 0;
	}

	public boolean isLessThan(Object a, Object b) throws ClassCastException {
		return ((FileLock) a).compareTo(b) < 0;
	}

	public boolean isGreaterThanOrEqualTo(Object a, Object b)
			throws ClassCastException {
		return ((FileLock) a).compareTo(b) >= 0;
	}

	public boolean isLessThanOrEqualTo(Object a, Object b)
			throws ClassCastException {
		return ((FileLock) a).compareTo(b) <= 0;
	}

	public boolean isComparable(Object o) {
		if (o instanceof FileLock) {
			return true;
		} else {
			return false;
		}
	}

	public boolean isEqualTo(Object a, Object b) throws ClassCastException {
		return ((FileLock) a).equals(b);
	}

}
