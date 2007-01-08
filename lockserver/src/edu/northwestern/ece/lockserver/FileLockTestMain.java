package edu.northwestern.ece.lockserver;

public class FileLockTestMain {

	public static void main(String[] args) {
		long[] offsets11 = {0, 128, 256};
		long[] lengths11 = {32, 64, 128};
		long[] offsets12 = {512, 600, 700};
		long[] lengths12 = {80, 75, 200};
		
		FileLockClientTester t1
			= new FileLockClientTester(offsets11, lengths11, 
									 offsets12, lengths12, "/tmp/test");
		t1.start();

		long[] offsets21 = {32, 100, 250};
		long[] lengths21 = {32, 50, 128};
		long[] offsets22 = {552, 650, 750};
		long[] lengths22 = {5, 23, 300};
		
		FileLockClientTester t2
			= new FileLockClientTester(offsets21, lengths21,
									 offsets22, lengths22, "/tmp/test");

		try { Thread.sleep(1000); } catch (InterruptedException e) { }
		t2.start();
	}
}
