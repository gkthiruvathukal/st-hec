/*
 * Created on Sep 14, 2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
package edu.northwestern.ece.lockserver.util;

import java.util.Random;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.Set;
import java.util.HashSet;

import jdsl.core.api.Comparator;
import jdsl.core.api.Locator;
import jdsl.core.ref.RedBlackTree;
import net.datastructures.RBTree;
import net.datastructures.Entry;
import edu.northwestern.ece.lockserver.FileLock;

public final class RBTreeTester {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		Comparator fileLockComparator = new FileLockOverlapComparator();

		edu.northwestern.ece.lockserver.util.RedBlackTree templeTree = new edu.northwestern.ece.lockserver.util.RedBlackTree();
		RBTree netDatastructuresTree = new RBTree();
		jdsl.core.ref.RedBlackTree jdslTree = new RedBlackTree(
				fileLockComparator);

		// Insert and remove 10000 random locks (maybe up this if we're
		// ambitious :)
		List insertList = new ArrayList();
		long off = 0;
		Random r = new Random();
		for (int i = 0; i < 10000; ++i) {
			long len = Math.abs(r.nextInt() % 100000);
			insertList.add(new FileLock(off, len));
			off += len + Math.abs(r.nextInt() % 1000);
		}
		List deleteList = new ArrayList(insertList);		
		Collections.shuffle(insertList);
		Collections.shuffle(deleteList);

		Iterator lockIter;
		long timeBegin;
		// Now give each tree a workout
		/*
		lockIter = insertList.iterator();
		long timeBegin = System.currentTimeMillis();
		while (lockIter.hasNext()) {
			templeTree.add(lockIter.next());
		}
		long templeTreeAddTime = System.currentTimeMillis() - timeBegin;

		lockIter = deleteList.iterator();
		timeBegin = System.currentTimeMillis();
		while (lockIter.hasNext()) {
			templeTree.delete(lockIter.next());
		}
		long templeTreeDeleteTime = System.currentTimeMillis() - timeBegin;
		*/

		lockIter = insertList.iterator();
		Set entrySet = new HashSet();
		timeBegin = System.currentTimeMillis();
		while (lockIter.hasNext()) {
			Object nextLock = lockIter.next();
			entrySet.add(netDatastructuresTree.insert(nextLock, nextLock));
		}
		long netDatastructuresTreeAddTime = System.currentTimeMillis()
				- timeBegin;

		Iterator entryIter = entrySet.iterator();
		timeBegin = System.currentTimeMillis();
		while (entryIter.hasNext()) {
			netDatastructuresTree.remove((Entry) entryIter.next());
		}
		long netDatastructuresTreeDeleteTime = System.currentTimeMillis()
				- timeBegin;

		lockIter = insertList.iterator();
		Set locatorSet = new HashSet();
		timeBegin = System.currentTimeMillis();
		while (lockIter.hasNext()) {
			Object nextLock = lockIter.next();
			locatorSet.add(jdslTree.insert(nextLock, nextLock));
		}
		long jdslTreeAddTime = System.currentTimeMillis() - timeBegin;

		Iterator locatorIter = locatorSet.iterator();
		timeBegin = System.currentTimeMillis();
		while (locatorIter.hasNext()) {
			jdslTree.remove((Locator) locatorIter.next());
		}
		long jdslTreeDeleteTime = System.currentTimeMillis() - timeBegin;

		//System.out.println("Temple tree: add time = " + templeTreeAddTime
		//		+ "ms; delete time = " + templeTreeDeleteTime + " ms");
		
		System.out.println("net.datastructures tree: add time = " + netDatastructuresTreeAddTime
				+ "ms; delete time = " + netDatastructuresTreeDeleteTime + " ms");
		
		System.out.println("JDSL tree: add time = " + jdslTreeAddTime
				+ "ms; delete time = " + jdslTreeDeleteTime + " ms");

	}

}
