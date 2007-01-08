#!/bin/sh
procs="2"
#mpi="/home/aching/timing/mpich2-1.0.1"
#pvfs_dir="/home/aching/timing/pvfs2"
pvfs_dir="/usr"
#exec_dir="/home/aching/timing/compare_flash1.6"
exec_dir="$HOME/compare_flash"

mpiexec="mpirun"
exec="$exec_dir/flash-io"
pvfs_copy="$pvfs_dir/src/apps/admin/pvfs2-cp"
test_types="posix collective datatype ufs"
file_prefix="/mnt/pvfs2/"

# delete the old UFS files
for test in $test_types
  do 
    echo rm $test
    rm $test
done

# generate the PVFS2 files with the various test_types
echo $mpiexec -np $procs $exec $test_types
$mpiexec -np $procs $exec $test_types

# copy the PVFS2 files into UFS
for test in $test_types
  do
  if [ $test != "ufs" ]; then
      echo $pvfs_copy $file_prefix$test $test
      $pvfs_copy $file_prefix$test $test
      echo chmod 777 $test
      chmod 777 $test
      lasttest=$test
  fi
done

# compare the files to see if they are identical
for test in $test_types
  do
    echo diff -s $test $lasttest
    diff -s $test $lasttest
    lasttest=$test
done 

