#######################################################################################
#
#   Copyright (c) 2006 Loyola University Chicago and Contributors. All rights reserved.
#   This file is part of The Hydra Filesystem.
#
#   The Hydra Filesystem is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   The Hydra Filesystem is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with the Hydra Filesystem; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#######################################################################################

 This is version 0.1 of the Hydra Filesystem, a pure-python attempt at a distributed filesystem.

 Please note that this is the first release, and that the software has only been tested in a closed lab environment. As
 such there might still be issues we are unaware of. Please let us know if you find any bug/issue with this software.

 This software is distributed under version 2 of the GNU Public License. Read the file COPYING for more details.


 * Brief instructions on how to use the filesystem

	 To familiarize yourself with the workings of the filesystem, please read the following documents:
	
	 The Hydra Filesystem: A distributed storage framework (published in LCI 2006)
	 http://etl.cs.luc.edu/research/hydra-file-system/paper/lci2006.pdf
	
	 A presentation outlining most of the packet exchanges:
	 http://webpages.cs.luc.edu/~bgonzalez/lci/


 * Requirements

	 To run this software you require:
	
	 Berkeley DB >= 3.2: http://www.sleepycat.com/
	
	 Python Bindings for Berkeley DB: http://pybsddb.sourceforge.net/
	
	 Download and install this packages before attempting to use hydra.


 * How to setup

	 1) Modify the metadata server parameters at:
	
		metadata/conf/metadata.conf
	
		id a unique integer identifying this metadata server
	
		address ip & port should be the address your metadata server will be listening to	
	
		backlog number is the number of concurrent connections your metadata server will sustain
	
		Under defaults you can specify: the default block size (in bytes) and the default number of replicas
		for each file
	
		storage path is where the metadata server database will be created
	
	
	 2) Modify your data server(s) parameters at:
	
		dataserver/conf/client*_conf.xml 
	
	 	id should be a unique integer for each dataserver
		
		address ip & port should be the address your dataserver will be listening to
		
		backlog number is the number of concurrent connections your dataserver will sustain
		
		under metadataservers, please define the address where your metadata server is listening (defined in metadata.conf)
	
		storage path is where the blocks are stored, and db is the filename of your block database
	
	 3) Modify the client library parameters at:
	
		 conf/fileclient1.xml
		
		 In this file you just need to provide the client with a few locations where a metadata server can be found. In other words,
		 make sure you specify the same address in metadata/metadata.conf.

 * How to run

	 1) Start the metadata server
	
		 ./mdserver.py -c metadata/conf/metadata.conf
	
	 2) Start one or more dataservers
	
		 ./dataserver.py -c dataserver/conf/client1_conf.xml
		 ./dataserver.py -c dataserver/conf/client2_conf.xml
		
		 (This starts dataservers 1 & 2)
	
	 3) That's it! You can now use the common.HydraFile module to access the filesystem.
	
		 Examples of usage:
		
		 sample_create_file.py
		 sample_upload_folder.py

		 The code in those files should be very self-explanatory

 * How to extend
 
	At this time, you can add to kinds of plugins to the filesytem:
	
	a) Packet plugins (redefine or create your own pacekts)
	
		The packet plugin is under common/plugins/packet.py
		
		Quick guide on how to add a packet builder:
		
		1) Define a name for your packet under: common/packet_types.py

		2) Define a class that extends Packet, with the following methods:
		
			__init__: define your packet structure in self.format_str (see the python struct module documentation for more information on how to do this)
			
			pack: Pack the parameters of the incoming data structure into a packet.
			
			unpack: Unpack the incoming packet into a data structure		
	
		3) At the end of the file you'll see an initialize() function. Register your packet class by calling:
		
			app.registerPacket(packet_types.YOUR_PACKET_TYPE,YourBuilderClass())
			
		Note that you don't necessarily need to do steps 2 & 3 under packet.py, you can do this in a separate
		file as long as:
		
			-Your file is under common/plugins
			-It has a .py extension
			-It defines an initialize() function that receives an app object
			
		For obvious reasons you can only define one packet builder per packet type.
		
	b) Handler plugins (redefine how the metadata & dataserver handle requests)
	
		There are two places where handlers are defined:
		
			metadata/plugins/packet_handers_metadata.py (for metadata server handlers)
			dataserver/plugins/packet_handlers_metadata.py (for dataserver handlers)
			
		How to add your own handler:
		
			1) Define a class that extends PacketHandler
			
			2) Add a process method that receives an incoming data structure
			
				With this class, you receive the following inherited properties:
				
				self.app: access to your application's public methods
					For the metadata server these are under metadata.py, in the class MDServer
					For the dataserver these are under dataserver.py, in the class DataServer
					
				self.net: access to a NetworkTransport object, where you can read/write data
				(This is the way to communicate with the client)
				
				self.fs: access to the server's object database
				
				self.pb: access to a packet building object
				
				self.cfg: your application's configuration parameters
			
				After your process method is done, you can either return:
					None: There are no more objects that should be called afterwards
					
					An instance of another class with a process method: You can return another
					instance of a class if your transaction involves more than a request/response.
					
					(See the classes Handle_FS_BEGIN_WRITE, STATE_STORE_BLOCK_INFO, STATE_STORE_BLOCK_WRITE
					under plugins/packet_handlers_dataserver.py for a concrete example of this)
					
			Note: You can pass handler specific parameters in your __init__ method.
			(see packet_handlers_monitor.py for a concrete example of this)
					
			3) Register your handler with the application
			
				At the end of the file there is an initialize() method, where you can register your handler in the following way:
				
				app.addHandler(packet_types.YOUR_PACKET_TYPE,Your_Handler_Class())
				
				Note that you can register several handler classes for a single packet. You can specify the
				order by setting the priority parameter (a higher value means the handler has less precedence)
				
				app.addHandler(packet_types.YOUR_PACKET_TYPE,Your_Handler_Class())
				app.addHandler(packet_types.YOUR_PACKET_TYPE,Your_Second_Handler_Class(),priority=60)
				
				In this case Your_Second_Handler_Class will be invoked after Your_Handler_Class is done
				
				The default priority is 50.
				
			Note that you don't necessarily need to do steps 2 & 3 under packet_handlers_metadata.py or packet_handers_dataserver.py. You can do this in a separate file as long as:
					
						-Your file is under metadata/plugins for metadata plugisn or dataserver/plugins for dataserver plugins
						-It has a .py extension
						-It defines an initialize() function that receives an app object

 If you have any questions or comments please contact us at:

	bgonzalez@cs.luc.edu
	gkt@cs.luc.edu
	
