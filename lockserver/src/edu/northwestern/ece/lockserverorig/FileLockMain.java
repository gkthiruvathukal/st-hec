/*
 * Created on Mar 1, 2005
 *
 * TODO To change the template for this generated file go to
 * Window - Preferences - Java - Code Generation - Code and Comments
 */
package edu.northwestern.ece.lockserverorig;

import java.util.List;
import java.util.ArrayList;

/**
 * @author aarestad
 * 
 * TODO To change the template for this generated type comment go to Window -
 * Preferences - Java - Code Generation - Code and Comments
 */
public class FileLockMain {
	public static void main(String[] args) {
		List l1 = new ArrayList();
		l1.add(new FileLock(0, 32));
		l1.add(new FileLock(128, 64));
		l1.add(new FileLock(256, 128));
		FileLockClientTester t1 = new FileLockClientTester(l1, "/tmp/test");

		List l2 = new ArrayList();
		l2.add(new FileLock(32, 32));
		l2.add(new FileLock(100, 50));
		l2.add(new FileLock(250, 128));
		FileLockClientTester t2 = new FileLockClientTester(l2, "/tmp/test");

		t1.start();
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e) {
		}
		t2.start();
	}
}