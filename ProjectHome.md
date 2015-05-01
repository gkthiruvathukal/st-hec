This repository contains code for our work on Hydra (a user-level filesystem) and block/byte-range lock server (a user-level distributed locking framework). This work is related to our [Scalable Technologies for Ultra-scale I/O](http://www.st-hec.info) project, which was supported in part by the National Science Foundation.

Downloads at this time must be fetched directly from our Subversion repository.

## Fetching and Installing Hydra ##

The code for the Hydra filesystem can be checked out as follows
```
svn checkout http://st-hec.googlecode.com/svn/trunk/hydra
```

The build instructions are available in the [Hydra README.text](http://st-hec.googlecode.com/svn/trunk/hydra/README.txt) file, which can also be found in the top-level directory after you perform the repository checkout.

## Fetching and Installing the Distributed Lockserver ##

```
svn checkout http://st-hec.googlecode.com/svn/trunk/lockserver
```

Please contact us if you are interested in working with this code. We have not yet written an installation document but there are proper make files (for the C portion) and Ant build files (for the Java portion). So it is possible to explore on your own.