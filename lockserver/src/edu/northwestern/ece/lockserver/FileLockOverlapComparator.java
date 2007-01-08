/*
 * Created on Jun 16, 2005
 */
package edu.northwestern.ece.lockserver;

import java.util.Comparator;

public final class FileLockOverlapComparator implements Comparator {

	public int compare(Object left, Object right) {
		FileLock l = (FileLock) left;
		FileLock r = (FileLock) right;
		long llb = l.getOffset();
		long lub = l.getOffset() + l.getLength() - 1;
		long rlb = r.getOffset();
		long rub = r.getOffset() + r.getLength() - 1;
		
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
}
