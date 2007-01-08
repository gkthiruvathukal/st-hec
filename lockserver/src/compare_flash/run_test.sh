#!/bin/sh
#mpi="/home/aching/Avery/Work.School/Research/mpi-pvfs2-datatype/mpich2-1.0.1"
mpi="/soft/apps/packages/mpich-gm-1.2.6..13b-intel-8.1-2"
#pvfs_dir="/home/aching/Avery/Work.School/Research/mpi-pvfs2-datatype/pvfs2"
pvfs_dir="/usr"
#exec_dir="/home/aching/Avery/Work.School/Research/mpi-pvfs2-datatype/compare_flash1.6"
exec_dir="$HOME/compare_flash"

proc_list="2 4 8"
#mpiexec="$mpi/bin/mpiexec"
mpiexec="$mpi/bin/mpirun"
exec="$exec_dir/flash-io"
#pvfs_copy="$pvfs_dir/src/apps/admin/pvfs2-cp"
test_types="datatype collective"
file_prefix="/mnt/pvfs2/"
reps="2"

# delete the old UFS files
for procs in $proc_list
  do
    for ((a=0; a < reps; a++))

      do
        echo $mpiexec -np $procs $exec $test_types
        $mpiexec -np $procs -machinefile $PBS_NODEFILE $exec $test_types
	sleep 2
    done
done

