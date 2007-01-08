/*
 * Copyright (c) 2000, Thomas W. Christopher and George K. Thiruvathukal
 * 
 * Java and High Performance Computing (JHPC) Organzization Tools of Computing
 * LLC
 * 
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 * 
 * Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 * 
 * Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 * 
 * The names Java and High-Performance Computing (JHPC) Organization, Tools of
 * Computing LLC, and/or the names of its contributors may not be used to
 * endorse or promote products derived from this software without specific prior
 * written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 * This license is based on version 2 of the BSD license. For more information
 * on Open Source licenses, please visit http://opensource.org.
 */

package info.jhpc.textbook.message2;

import info.jhpc.message2.MessageListener;
import info.jhpc.message2.Message;
import info.jhpc.message2.MessageServer;

import java.util.Date;

public class VanillaService implements MessageListener {
	public static final int VANILLA_SERVICE_MESSAGE = 100;

	public static final int VANILLA_SERVICE_PORT = 1999;

	public Message accept(Message m) {
		System.out.println("got message: " + m);
		Date today = new Date();
		String functionName = m.getStringParam("functionName");
		if (functionName.equalsIgnoreCase("acquire")) {
			return acquire(m);
		} else if (functionName.equalsIgnoreCase("release")) {
			return release(m);
		}
		return m;
	}

	protected Message acquire(Message m) {
		int lockId = m.getIntegerParam("lockId");
		String fileName = m.getStringParam("fileName");
		int numberOfLocks = m.getIntegerParam("numberOfLocks");

		int[] offset = new int[numberOfLocks];
		int[] length = new int[numberOfLocks];
		for (int i = 0; i < numberOfLocks; i++) {
			offset[i] = m.getIntegerParam("offset" + i);
			length[i] = m.getIntegerParam("length" + i);
		}
		
		long long0 = m.getLongParam("long0");
		long long1 = m.getLongParam("long1");
		
		System.out.println("long0: " + long0);
		System.out.println("long1: " + long1);
		
		int[] offsets1 = m.getIntegerArrayParam("offsets1");
		long[] lengths2 = m.getLongArrayParam("lengths2");
		
		int offsets10 = m.getIntegerArrayParamValue("offsets1", 0);
		long lengths21 = m.getLongArrayParamValue("lengths2", 1);
		
		System.out.println("offsets1: " + offsets1);
		System.out.println("lengths2: " + lengths2);
		
		System.out.println("offsets10: " + offsets10);
		System.out.println("lengths21: " + lengths21);

		Message reply = new Message();
		reply.setIntegerParam("lockId", lockId);
		reply.setIntegerParam("numberOfLocksGranted", numberOfLocks);
		return reply;
	}

	protected Message release(Message m) {

		Message reply = new Message();
		reply.setStringParam("nop", "nop");
		return reply;
	}

	public static void main(String args[]) {
		VanillaService ds = new VanillaService();
		MessageServer ms;
		try {
			ms = new MessageServer(VANILLA_SERVICE_PORT);
		} catch (Exception e) {
			System.err.println("Could not start service " + e);
			return;
		}
		Thread msThread = new Thread(ms);
		ms.addMessageListener(VANILLA_SERVICE_MESSAGE, ds);
		msThread.start();
	}
}