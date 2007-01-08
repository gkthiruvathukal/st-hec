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

import java.io.IOException;
import info.jhpc.message2.Message;
import info.jhpc.message2.MessageClient;

public class VanillaClient {

	public static void main(String[] args) {
		String host;
		try {
			host = args[0];
		} catch (ArrayIndexOutOfBoundsException e) {
			host = "localhost";
		}
		int port;
		try {
			port = Integer.parseInt(args[1]);
		} catch (ArrayIndexOutOfBoundsException e) {
			port = VanillaService.VANILLA_SERVICE_PORT;
		}

		MessageClient conn;
		try {
			conn = new MessageClient(host, port);
		} catch (IOException e) {
			System.err.println("Could not contact VanillaService @ " + host
					+ ":" + port + ": " + e.getMessage());
			e.printStackTrace();
			return;
		}

		Message m = new Message();
		m.setType(VanillaService.VANILLA_SERVICE_MESSAGE);
		m.setStringParam("functionName", "acquire");
		m.setIntegerParam("lockId", 25);
		m.setStringParam("fileName", "xyz.dat");
		m.setIntegerParam("numberOfLocks", 2);

		m.setIntegerParam("offset0", 10);
		m.setIntegerParam("length0", 5);

		m.setIntegerParam("offset1", 20);
		m.setIntegerParam("length1", 5);
		
		m.setLongParam("long0", 12345678901234567L);
		m.setLongParam("long1", -23456789012345678L);

		m = conn.call(m);
		System.out.println("Message instance received from server " + m);
		conn.disconnect();
	}
}