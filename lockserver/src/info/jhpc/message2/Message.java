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

package info.jhpc.message2;

import java.io.*;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.Iterator;

public class Message {
	private static boolean debug = false;

	private static int maxDebugLevel = 1;

	private static final String P_STRING = "S$";

	private static final String P_INTEGER = "I$";

	private static final String P_INTEGER_ARRAY = "IA$";
	
	private static final String P_LONG = "L$";
	
	private static final String P_LONG_ARRAY = "LA$";

	private static final String P_BOOLEAN = "B$";

	private Hashtable parameters = new Hashtable();

	private int type = 0;

	private int tag = 0;

	private int length = 0;

	public Message() {
		// nothing additional to do
	}

	public static void log(int level, String function, String message) {
		if (debug && level <= maxDebugLevel)
			System.out.println("Message::" + function + "> " + message);
	}

	public void encode(DataOutputStream out) throws IOException {
		// output a header
		out.writeUTF("SMA");
		// output length, type, tag
		out.writeInt(length);
		out.writeInt(type);
		out.writeInt(tag);
		// output # of pairs
		out.writeInt(parameters.size());
		// output pairs
		Enumeration e = parameters.keys();
		while (e.hasMoreElements()) {
			String key = (String) e.nextElement();
			out.writeUTF(key);
			Object value = parameters.get(key);
			if (key.startsWith(P_INTEGER_ARRAY))
				encodeIntArray(out, value);
			else if (key.startsWith(P_LONG_ARRAY))
				encodeLongArray(out, value);
			else
				out.writeUTF((String) value);
		}
	}

	private void encodeIntArray(DataOutputStream out, Object array) throws IOException {
		int[] values = (int []) array;
		out.writeInt(values.length);
		for (int i=0; i < values.length; i++) {
			out.writeInt(values[i]);
		}	
	}
	
	private void encodeLongArray(DataOutputStream out, Object array) throws IOException {
		long[] values = (long []) array;
		out.writeInt(values.length);
		for (int i=0; i < values.length; i++) {
			out.writeLong(values[i]);
		}	
	}
	
	public void decode(DataInputStream in) throws IOException {
		// read header
		String header = in.readUTF();
		if (!header.equals("SMA"))
			throw new IOException();
		// read length, type, tag
		length = in.readInt();
		//System.out.println("Length: " + length);
		type = in.readInt();
		//System.out.println("Type: " + type);
		tag = in.readInt();
		//System.out.println("Tag: " + tag);
		int parameterCount = in.readInt();
		//System.out.println("parameterCount: " + parameterCount);
		for (int i = 0; i < parameterCount; i++) {
			String key = in.readUTF();
			Object value;
			if (key.startsWith(P_INTEGER_ARRAY))
				value = decodeIntArray(in);
			else if (key.startsWith(P_LONG_ARRAY))
				value = decodeLongArray(in);
			else
				value = in.readUTF();
			parameters.put(key, value);
		}
	}

	private Object decodeIntArray(DataInputStream in) throws IOException {
		int length = in.readInt();
		int values[] = new int[length];
		for (int i=0; i < values.length; i++) {
			values[i] = in.readInt();
		}
		return values;
	}
	
	private Object decodeLongArray(DataInputStream in) throws IOException {
		int length = in.readInt();
		long[] values = new long[length];
		for (int i=0; i < values.length; i++) {
			values[i] = in.readLong();
		}
		return values;
	}
	
	public void setType(int type) {
		this.type = type;
	}

	public int getType() {
		return type;
	}

	public void setTag(int tag) {
		this.tag = tag;
	}

	public int getTag() {
		return tag;
	}

	public void setParam(String key, String value) {
		parameters.put(P_STRING + key, value);
	}

	public String getParam(String key) {
		return (String) parameters.get(P_STRING + key);
	}

	public void setStringParam(String key, String value) {
		parameters.put(P_STRING + key, value);
	}

	public String getStringParam(String key) {
		return (String) parameters.get(P_STRING + key);
	}

	public void setIntegerParam(String key, int value) {
		parameters.put(P_INTEGER + key, value + "");
	}
	
	public void createIntegerArrayParam(String key, int items) {
		int[] values = new int[items];
		parameters.put(P_INTEGER_ARRAY + key, values);
	}

	public int[] getIntegerArrayParam(String key) {
		return (int []) parameters.get(P_INTEGER_ARRAY + key);
	}
	
	public void setIntegerArrayParamValue(String key, int pos, int value) {
		getIntegerArrayParam(key)[pos] = value;
	}

	public int getIntegerArrayParamValue(String key, int pos) {
		return getIntegerArrayParam(key)[pos];
	}

	public int getIntegerParam(String key) {
		// Removed try/catch block - 2005/03/08 pma
		return Integer.parseInt((String) parameters.get(P_INTEGER + key));
	}

	public void setLongParam(String key, long value) {
		parameters.put(P_LONG + key, value + "");
	}

	public long getLongParam(String key) {
		// Removed try/catch block - 2005/03/08 pma
		return Long.parseLong((String) parameters.get(P_LONG + key));
	}
	
	public void createLongArrayParam(String key, int items) {
		long[] values = new long[items];
		parameters.put(P_LONG_ARRAY + key, values);
	}

	public long[] getLongArrayParam(String key) {
		return (long[]) parameters.get(P_LONG_ARRAY + key);
	}
	
	public void setLongArrayParamValue(String key, int pos, long value) {
		getLongArrayParam(key)[pos] = value;
	}

	public long getLongArrayParamValue(String key, int pos) {
		return getLongArrayParam(key)[pos];
	}

	public void setBooleanParam(String key, boolean value) {
		parameters.put(P_BOOLEAN + key, value + "");
	}

	public boolean getBooleanParam(String key) {
		String value = (String) parameters.get(P_BOOLEAN + key);
		return value.equals(true + "");
	}

	public void merge(Message m) {
		Enumeration e = m.parameters.keys();
		while (e.hasMoreElements()) {
			Object key = e.nextElement();
			parameters.put(key, m.parameters.get(key));
		}
	}

	public String toString() {
		String repAsString = "";
		return "Message: type = " + type + " param = " + stringifyParameters();
	}
	
	private String stringifyParameters() {
		StringBuffer buf = new StringBuffer();
		buf.append("{");
		Iterator keyIter = parameters.keySet().iterator();
		while (keyIter.hasNext()) {
			Object k = keyIter.next();
			buf.append(k);
			buf.append("=");
			Object v = parameters.get(k);
			if (v.getClass().isArray()) {
				int[] ia = {};
				long[] la = {};
				try {
					ia = (int[]) v;
				} catch (ClassCastException e) {}
				try {
					la = (long[]) v;
				} catch (ClassCastException e ) {}
				for (int i = 0; i < ia.length; ++i) {
					buf.append("[");
					buf.append("]");
				}
				for (int j = 0; j < la.length; ++j) {
					buf.append("[");
					buf.append(la[j]);
					buf.append("]");
				}
			} else {
				buf.append(v);
			}
			if (keyIter.hasNext()) {
				buf.append(", ");
			}
		}
		buf.append("}");
		return buf.toString();
	}

	public static void main(String args[]) {
		Message m1 = new Message();
		Message m2 = new Message();
		m1.setType(2);
		m1.setTag(3);
		m1.setStringParam("s1", "George");
		m1.setBooleanParam("b2", true);
		m1.setIntegerParam("i3", 100);
		m1.setIntegerParam("i4", 100);

		try {
			FileOutputStream fos = new FileOutputStream("m1.dat");
			DataOutputStream dos = new DataOutputStream(fos);
			m1.encode(dos);
			fos.close();
		} catch (Exception e) {
			System.out.println("exception/m1.dat" + e);
		}
		System.out.println("Message written to m1.dat");
		try {
			FileInputStream fis = new FileInputStream("m1.dat");
			DataInputStream dis = new DataInputStream(fis);
			m2.decode(dis);
			fis.close();
		} catch (Exception e) {
			System.out.println("exception/m2 " + e);
		}
		System.out.println("Read m2");
		System.out.println("Message m1 " + m1);
		System.out.println("Message m2 " + m2);

	}
}