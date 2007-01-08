#!/bin/sh
mpi_path="/home/aching/timing/mpich2-1.0.1"

mpi_pvfs2="$mpi_path/src/mpi/romio/adio/ad_pvfs2"
cur_dir=`pwd`

echo cd $mpi_pvfs2
cd $mpi_pvfs2
echo make clean
make clean
echo make
make
echo cd $cur_dir
cd $cur_dir
echo make clean all
make clean all